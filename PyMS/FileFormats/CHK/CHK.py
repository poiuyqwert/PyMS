
from __future__ import annotations

from .CHKRequirements import CHKRequirements
from .CHKSectionUnknown import CHKSectionUnknown
from . import Sections

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
	SECTION_TYPES: dict[bytes, Type[CHKSection]] = {
		Sections.CHKSectionTYPE.NAME:Sections.CHKSectionTYPE,
		Sections.CHKSectionVER.NAME:Sections.CHKSectionVER,
		Sections.CHKSectionIVER.NAME:Sections.CHKSectionIVER,
		Sections.CHKSectionIVE2.NAME:Sections.CHKSectionIVE2,
		Sections.CHKSectionVCOD.NAME:Sections.CHKSectionVCOD,
		Sections.CHKSectionIOWN.NAME:Sections.CHKSectionIOWN,
		Sections.CHKSectionOWNR.NAME:Sections.CHKSectionOWNR,
		Sections.CHKSectionERA.NAME:Sections.CHKSectionERA,
		Sections.CHKSectionDIM.NAME:Sections.CHKSectionDIM,
		Sections.CHKSectionSIDE.NAME:Sections.CHKSectionSIDE,
		Sections.CHKSectionMTXM.NAME:Sections.CHKSectionMTXM,
		Sections.CHKSectionPUNI.NAME:Sections.CHKSectionPUNI,
		Sections.CHKSectionUPGR.NAME:Sections.CHKSectionUPGR,
		Sections.CHKSectionPTEC.NAME:Sections.CHKSectionPTEC,
		Sections.CHKSectionUNIT.NAME:Sections.CHKSectionUNIT,
		Sections.CHKSectionTILE.NAME:Sections.CHKSectionTILE,
		Sections.CHKSectionDD2.NAME:Sections.CHKSectionDD2,
		Sections.CHKSectionTHG2.NAME:Sections.CHKSectionTHG2,
		Sections.CHKSectionMASK.NAME:Sections.CHKSectionMASK,
		Sections.CHKSectionSTR.NAME:Sections.CHKSectionSTR,
		Sections.CHKSectionUPRP.NAME:Sections.CHKSectionUPRP,
		Sections.CHKSectionUPUS.NAME:Sections.CHKSectionUPUS,
		Sections.CHKSectionMRGN.NAME:Sections.CHKSectionMRGN,
		Sections.CHKSectionTRIG.NAME:Sections.CHKSectionTRIG,
		Sections.CHKSectionMBRF.NAME:Sections.CHKSectionMBRF,
		Sections.CHKSectionSPRP.NAME:Sections.CHKSectionSPRP,
		Sections.CHKSectionFORC.NAME:Sections.CHKSectionFORC,
		Sections.CHKSectionWAV.NAME:Sections.CHKSectionWAV,
		Sections.CHKSectionUNIS.NAME:Sections.CHKSectionUNIS,
		Sections.CHKSectionUPGS.NAME:Sections.CHKSectionUPGS,
		Sections.CHKSectionTECS.NAME:Sections.CHKSectionTECS,
		Sections.CHKSectionSWNM.NAME:Sections.CHKSectionSWNM,
		Sections.CHKSectionCOLR.NAME:Sections.CHKSectionCOLR,
		Sections.CHKSectionPUPx.NAME:Sections.CHKSectionPUPx,
		Sections.CHKSectionPTEx.NAME:Sections.CHKSectionPTEx,
		Sections.CHKSectionUNIx.NAME:Sections.CHKSectionUNIx,
		Sections.CHKSectionUPGx.NAME:Sections.CHKSectionUPGx,
		Sections.CHKSectionTECx.NAME:Sections.CHKSectionTECx
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
		self.sections: dict[bytes, CHKSection] = {}
		self.section_order: list[bytes] = []

	def get_section_named(self, name: bytes, game_mode: int = CHKRequirements.MODE_ALL) -> CHKSection | None:
		sect_class = CHK.SECTION_TYPES[name]
		required = False

		if name == Sections.CHKSectionVER.NAME:
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
		if sect is not None and not isinstance(sect, section_type):
			return None
		if required and sect is None:
			sect = section_type(self)
			self.sections[section_type.NAME] = sect
		return sect

	def player_color(self, player: int) -> int:
		colors = Sections.CHKSectionCOLR.DEFAULT_COLORS
		if colr := self.get_section(Sections.CHKSectionCOLR):
			colors = colr.colors
		colors.extend((Sections.CHKSectionCOLR.GREEN,Sections.CHKSectionCOLR.PALE_YELLOW,Sections.CHKSectionCOLR.TAN,Sections.CHKSectionCOLR.NEUTRAL))
		return colors[player]

	def load_file(self, file: str | BinaryIO) -> None:
		data = load_file(file, 'CHK')
		try:
			self.load_data(data)
		except PyMSError as e:
			raise e
		except Exception as exc:
			raise PyMSError('Load', f"Unsupported CHK file '{file}', could possibly be corrupt") from exc

	def load_data(self, data: bytes) -> None:
		offset = 0
		sections: dict[bytes, CHKSection] = {}
		section_order: list[bytes] = []
		toProcess: list[CHKSection] = []
		while offset < len(data)-8:
			header = struct.unpack('<4sL', data[offset:offset+8])
			name = header[0]
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
		except Exception as exc:
			raise PyMSError('Save', f"Could not save CHK to file '{file}'") from exc
		f.write(data)
		f.close()

	def save_data(self) -> bytes:
		result = b''
		order: list[bytes] = []
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
