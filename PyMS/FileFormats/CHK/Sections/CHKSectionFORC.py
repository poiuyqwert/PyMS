
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad, named_flags

import struct

class CHKForce:
	RANDOM_START = (1 << 0)
	ALLIES = (1 << 1)
	ALLIED_VICTORY = (1 << 2)
	SHARED_VISION = (1 << 4)

	def __init__(self):
		self.name = 0
		self.properties = 0

class CHKSectionFORC(CHKSection):
	NAME = 'FORC'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.playerForces = [0] * 8
		self.forces = []
		for _ in range(4):
			self.forces.append(CHKForce())
	
	def load_data(self, data):
		o = 0
		self.playerForces = list(struct.unpack('<8B', data[o:o+8]))
		o += 8
		names = list(struct.unpack('<4H', data[o:o+8]))
		o += 8
		properties = list(struct.unpack('<4B', data[o:o+4]))
		for f in range(4):
			self.forces[f].name = names[f]
			self.forces[f].properties = properties[f]
	
	def save_data(self):
		names = []
		properties = []
		for force in self.forces:
			names.append(force.name)
			properties.append(force.properties)
		return struct.pack('<8B4H4B', *(self.playerForces + names + properties))
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		result += '\t%s\n' % pad('#', 'Force')
		for p in range(8):
			result += '\t%s\n' % pad('Player %d' % (p+1), self.playerForces[p]+1)
		properties = ''
		for f,force in enumerate(self.forces):
			result += '\t%s\n' % pad('Name%d' % (f+1), 'String %d' % force.name)
			header,values = named_flags(force.properties, ["Random Start","Allies","Allied Victory","Shared Vision"], 8)
			if not properties:
				properties = '\t%s%s\n' % (pad('#'), header)
			properties += '\t%s\n' % pad('Properies%d' % (f+1), values)
		return result + properties
