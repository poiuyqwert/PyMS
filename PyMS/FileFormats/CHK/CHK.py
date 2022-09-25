
from .CHKRequirements import CHKRequirements
from .CHKSectionUnknown import CHKSectionUnknown
from .Sections import *

from ...FileFormats import TBL, AIBIN

from ...Utilities import Assets
from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct, math, os

class CHK:
	SECTION_TYPES = {
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

	def __init__(self, stat_txt=None, aiscript=None):
		if isinstance(stat_txt, TBL.TBL):
			self.stat_txt = stat_txt
		else:
			if stat_txt == None:
				stat_txt = Assets.mpq_file_path('rez', 'stat_txt.tbl')
			self.stat_txt = TBL.TBL()
			self.stat_txt.load_file(stat_txt)
		if isinstance(aiscript, AIBIN.AIBIN):
			self.aiscript = aiscript
		else:
			if aiscript == None:
				aiscript = Assets.mpq_file_path('scripts', 'aiscript.bin')
			self.aiscript = AIBIN.AIBIN(stat_txt=self.stat_txt)
			self.aiscript.load_file(aiscript)
		self.sections = {}
		self.section_order = []

	def get_section(self, name, game_mode=CHKRequirements.MODE_ALL):
		sect_class = CHK.SECTION_TYPES[name]
		required = False

		if name == CHKSectionVER.NAME:
			required = True
		elif sect_class:
			required = sect_class.REQUIREMENTS.is_required(self, game_mode)
		sect = self.sections.get(name)
		if required and sect == None and sect_class:
			sect = sect_class(self)
			self.sections[name] = sect
		return sect

	def player_color(self, player):
		colors = CHKSectionCOLR.DEFAULT_COLORS
		colr = self.get_section(CHKSectionCOLR.NAME)
		if colr:
			colors = colr.colors
		colors.extend((CHKSectionCOLR.GREEN,CHKSectionCOLR.PALE_YELLOW,CHKSectionCOLR.TAN,CHKSectionCOLR.NEUTRAL))
		return colors[player]

	def load_file(self, file):
		data = load_file(file, 'CHK')
		try:
			self.load_data(data)
		except PyMSError as e:
			raise e
		except:
			raise PyMSError('Load',"Unsupported CHK file '%s', could possibly be corrupt" % file)

	def load_data(self, data):
		offset = 0
		sections = {}
		section_order = []
		toProcess = []
		while offset < len(data)-8:
			name,length = struct.unpack('<4sL', data[offset:offset+8])
			offset += 8
			sect_class = CHK.SECTION_TYPES.get(name)
			if not sect_class:
				sect = CHKSectionUnknown(self, name)
			else:
				sect = sect_class(self)
			sect.load_data(data[offset:offset+min(length,len(data)-offset)])
			sections[name] = sect
			section_order.append(name)
			if hasattr(sect, "process_data"):
				toProcess.append(sect)
			offset += length
		self.sections = sections
		self.section_order = section_order
		for sect in toProcess:
			sect.process_data()

	def save_file(self, file):
		data = self.save_data()
		try:
			f = AtomicWriter(file, 'wb')
		except:
			raise PyMSError('Save',"Could not save CHK to file '%s'" % file)
		f.write(data)
		f.close()

	def save_data(self):
		result = ''
		order = []
		order.extend(self.section_order)
		for name in self.sections.keys():
			if not name in order:
				order.append(name)
		for name in order:
			section = self.sections.get(name)
			if section:
				data = section.save_data()
				result += struct.pack('<4sL', section.name, len(data))
				result += data
		return result
