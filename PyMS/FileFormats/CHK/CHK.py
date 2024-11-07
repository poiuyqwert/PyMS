
from __future__ import annotations

from .CHKRequirements import CHKRequirements
from .CHKSectionUnknown import CHKSectionUnknown
from .Sections import *

from ...FileFormats import TBL
from ...FileFormats.AIBIN import AIBIN

from .CHKSection import CHKSection

from ...Utilities import Assets
from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

from typing import TYPE_CHECKING, Type, TypeVar
if TYPE_CHECKING:
	from typing import BinaryIO

S = TypeVar('S', bound=CHKSection)

class CHK:
	SECTION_TYPES: dict[str, Type[CHKSection]] = {
		CHKSectionTYPE.NAME:CHKSectionTYPE,
		CHKSectionVER.NAME:CHKSectionVER,
		CHKSectionIVER.NAME:CHKSectionIVER,
		CHKSectionIVE2.NAME:CHKSectionIVE2,
		CHKSectionVCOD.NAME:CHKSectionVCOD,
		CHKSectionIOWN.NAME:CHKSectionIOWN,
		CHKSectionOWNR.NAME:CHKSectionOWNR,
		CHKSectionERA.NAME:CHKSectionERA,
		CHKSectionDIM.NAME:CHKSectionDIM,
		CHKSectionSIDE.NAME:CHKSectionSIDE,
		CHKSectionMTXM.NAME:CHKSectionMTXM,
		CHKSectionPUNI.NAME:CHKSectionPUNI,
		CHKSectionUPGR.NAME:CHKSectionUPGR,
		CHKSectionPTEC.NAME:CHKSectionPTEC,
		CHKSectionUNIT.NAME:CHKSectionUNIT,
		CHKSectionTILE.NAME:CHKSectionTILE,
		CHKSectionDD2.NAME:CHKSectionDD2,
		CHKSectionTHG2.NAME:CHKSectionTHG2,
		CHKSectionMASK.NAME:CHKSectionMASK,
		CHKSectionSTR.NAME:CHKSectionSTR,
		CHKSectionUPRP.NAME:CHKSectionUPRP,
		CHKSectionUPUS.NAME:CHKSectionUPUS,
		CHKSectionMRGN.NAME:CHKSectionMRGN,
		CHKSectionTRIG.NAME:CHKSectionTRIG,
		CHKSectionMBRF.NAME:CHKSectionMBRF,
		CHKSectionSPRP.NAME:CHKSectionSPRP,
		CHKSectionFORC.NAME:CHKSectionFORC,
		CHKSectionWAV.NAME:CHKSectionWAV,
		CHKSectionUNIS.NAME:CHKSectionUNIS,
		CHKSectionUPGS.NAME:CHKSectionUPGS,
		CHKSectionTECS.NAME:CHKSectionTECS,
		CHKSectionSWNM.NAME:CHKSectionSWNM,
		CHKSectionCOLR.NAME:CHKSectionCOLR,
		CHKSectionPUPx.NAME:CHKSectionPUPx,
		CHKSectionPTEx.NAME:CHKSectionPTEx,
		CHKSectionUNIx.NAME:CHKSectionUNIx,
		CHKSectionUPGx.NAME:CHKSectionUPGx,
		CHKSectionTECx.NAME:CHKSectionTECx
	}

	def __init__(self, stat_txt: TBL.TBL | str | None = None, aiscript: AIBIN.AIBIN | str | None = None) -> None:
		if isinstance(stat_txt, TBL.TBL):
			self.stat_txt = stat_txt
		else:
			if stat_txt is None:
				stat_txt = Assets.mpq_file_path('rez', 'stat_txt.tbl')
			self.stat_txt = TBL.TBL()
			self.stat_txt.load_file(stat_txt)
		if isinstance(aiscript, AIBIN.AIBIN):
			self.aiscript = aiscript
		else:
			if aiscript is None:
				aiscript = Assets.mpq_file_path('scripts', 'aiscript.bin')
			self.aiscript = AIBIN.AIBIN()#stat_txt=self.stat_txt)
			self.aiscript.load(aiscript, bw_input=None)
		self.sections: dict[str, CHKSection] = {}
		self.section_order: list[str] = []

	def get_section_named(self, name: str, game_mode: int = CHKRequirements.MODE_ALL) -> CHKSection | None:
		sect_class = CHK.SECTION_TYPES[name]
		required = False

		if name == CHKSectionVER.NAME:
			required = True
		elif sect_class:
			required = sect_class.REQUIREMENTS.is_required(self, game_mode)
		sect = self.sections.get(name)
		if required and sect is None and sect_class:
			sect = sect_class(self)
			self.sections[name] = sect
		return sect

	def get_section(self, section_type: Type[S], game_mode: int = CHKRequirements.MODE_ALL) -> S | None:
		required = section_type.REQUIREMENTS.is_required(self, game_mode)
		sect = self.sections.get(section_type.NAME)
		if not isinstance(sect, section_type):
			return None
		if required and sect is None:
			sect = section_type(self)
			self.sections[section_type.name] = sect
		return sect

	def player_color(self, player: int) -> int:
		colors = CHKSectionCOLR.DEFAULT_COLORS
		if colr := self.get_section(CHKSectionCOLR):
			colors = colr.colors
		colors.extend((CHKSectionCOLR.GREEN,CHKSectionCOLR.PALE_YELLOW,CHKSectionCOLR.TAN,CHKSectionCOLR.NEUTRAL))
		return colors[player]

	def load_file(self, file: str | BinaryIO) -> None:
		data = load_file(file, 'CHK')
		try:
			self.load_data(data)
		except PyMSError as e:
			raise e
		except:
			raise PyMSError('Load',"Unsupported CHK file '%s', could possibly be corrupt" % file)

	def load_data(self, data: bytes) -> None:
		offset = 0
		sections: dict[str, CHKSection] = {}
		section_order: list[str] = []
		toProcess: list[CHKSection] = []
		while offset < len(data)-8:
			header = struct.unpack('<4sL', data[offset:offset+8])
			name = str(header[0])
			length = int(header[1])
			offset += 8
			sect_class = CHK.SECTION_TYPES.get(name)
			if not sect_class:
				sect: CHKSection = CHKSectionUnknown(self, name)
			else:
				sect = sect_class(self)
			sect.load_data(data[offset:offset+min(length,len(data)-offset)])
			sections[name] = sect
			section_order.append(name)
			if sect.requires_post_processing():
				toProcess.append(sect)
			offset += length
		self.sections = sections
		self.section_order = section_order
		for sect in toProcess:
			sect.process_data()

	def save_file(self, file: str) -> None:
		data = self.save_data()
		try:
			f = AtomicWriter(file, 'wb')
		except:
			raise PyMSError('Save',"Could not save CHK to file '%s'" % file)
		f.write(data)
		f.close()

	def save_data(self) -> bytes:
		result = b''
		order: list[str] = []
		order.extend(self.section_order)
		for name in list(self.sections.keys()):
			if not name in order:
				order.append(name)
		for name in order:
			section = self.sections.get(name)
			if section:
				data = section.save_data()
				result += struct.pack('<4sL', section.NAME, len(data))
				result += data
		return result
