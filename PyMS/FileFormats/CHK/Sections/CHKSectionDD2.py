
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKDoodadVisual(object):
	def __init__(self, chk): # type: (CHK) -> None
		self.chk = chk
		self.doodadID = 0
		self.position = [0,0]
		self.owner = 0
		self.enabled = False

	def load_data(self, data): # type: (bytes) -> None
		self.doodadID,x,y,self.owner,enabled = tuple(int(v) for v in struct.unpack('<3H2B', data[:8]))
		self.position = [x,y]
		self.enabled = bool(enabled)

	def save_data(self): # type: () -> bytes
		return struct.pack('<3H2B', self.doodadID,self.position[0],self.position[1],self.owner,self.enabled)

	def decompile(self):
		result = "\t#\n"
		result += '\t%s\n' % pad('DoodadID', self.doodadID)
		result += '\t%s\n' % pad('Position', '%s,%s' % (self.position[0],self.position[1]))
		result += '\t%s\n' % pad('Owner', self.owner)
		result += '\t%s\n' % pad('Enabled', self.enabled)
		return result

class CHKSectionDD2(CHKSection):
	NAME = 'DD2 '
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)
	
	def __init__(self, chk): # type: (CHK) -> None
		CHKSection.__init__(self, chk)
		self.doodads = [] # type: list[CHKDoodadVisual]
	
	def load_data(self, data): # type: (bytes) -> None
		self.doodads = []
		o = 0
		while o+8 <= len(data):
			doodad = CHKDoodadVisual(self.chk)
			doodad.load_data(data[o:o+8])
			self.doodads.append(doodad)
			o += 8
	
	def save_data(self): # type: () -> bytes
		result = b''
		for doodad in self.doodads:
			result += doodad.save_data()
		return result
	
	def decompile(self): # type: () -> str
		result = '%s:\n' % (self.NAME)
		for doodad in self.doodads:
			result += doodad.decompile()
		return result
