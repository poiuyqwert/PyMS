
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad, named_flags

import struct

class CHKDoodad:
	SPRITE = (1 << 12)
	DISABLED = (1 << 15)

	def __init__(self, chk):
		self.chk = chk
		self.doodadID = 0
		self.position = [0,0]
		self.owner = 0
		self.flags = 0

	def load_data(self, data):
		self.doodadID,x,y,self.owner,self.flags = struct.unpack('<3HBxH', data[:10])
		self.position = [x,y]

	def save_data(self):
		return struct.pack('<3HBxH', self.doodadID,self.position[0],self.position[1],self.owner,self.flags)

	def decompile(self):
		result = "\t#\n"
		result += '\t%s\n' % pad('DoodadID', self.doodadID)
		result += '\t%s\n' % pad('Position', '%s,%s' % (self.position[0],self.position[1]))
		result += '\t%s\n' % pad('Owner', self.owner)
		header,values = named_flags(self.flags, ["Sprite",None,None,"Disabled"], 16, 12)
		result += '\t%s%s\n' % (pad('#'), header)
		result += '\t%s\n' % pad('Flags', values)
		return result

class CHKSectionTHG2(CHKSection):
	NAME = 'THG2'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.doodads = []
	
	def load_data(self, data):
		self.doodads = []
		o = 0
		while o+10 <= len(data):
			doodad = CHKDoodad(self.chk)
			doodad.load_data(data[o:o+10])
			self.doodads.append(doodad)
			o += 10
	
	def save_data(self):
		result = ''
		for doodad in self.doodads:
			result += doodad.save_data()
		return result
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		for doodad in self.doodads:
			result += doodad.decompile()
		return result
