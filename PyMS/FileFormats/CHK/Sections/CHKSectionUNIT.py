
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad, named_flags

import struct

class CHKUnit:
	NYDUS_LINK = (1 << 9)
	ADDON_LINK = (1 << 10)

	CLOAK = (1 << 0)
	BURROW = (1 << 1)
	IN_TRANSIT = (1 << 2)
	HULLUCINATED = (1 << 3)
	INVINCIBLE = (1 << 4)

	OWNER = (1 << 0)
	HEALTH = (1 << 1)
	SHIELDS = (1 << 2)
	ENERGY = (1 << 3)
	RESOURCE = (1 << 4)
	HANGER = (1 << 5)

	def __init__(self, chk, ref_id):
		self.ref_id = ref_id
		self.chk = chk
		self.instanceID = 0
		self.position = [0,0]
		self.unit_id = 0
		self.buildingRelation = 0
		self.validAbilities = 0
		self.validProperties = 0
		self.owner = 0
		self.health = 0
		self.shields = 0
		self.energy = 0
		self.resources = 0
		self.hangerUnits = 0
		self.abilityStates = 0
		self.unitRelationID = 0

	def load_data(self, data):
		self.instanceID,x,y,self.unit_id,self.buildingRelation,self.validAbilities,self.validProperties,self.owner,self.health,self.shields,self.energy,self.resources,self.hangerUnits,self.abilityStates,self.unitRelationID = \
			struct.unpack('<L6H4BL2H4xL', data[:36])
		self.position = [x,y]

	def save_data(self):
		return struct.pack('<L6H4BL2H4xL', self.instanceID,self.position[0],self.position[1],self.unit_id,self.buildingRelation,self.validAbilities,self.validProperties,self.owner,self.health,self.shields,self.energy,self.resources,self.hangerUnits,self.abilityStates,self.unitRelationID)

	def decompile(self):
		result = '\t#\n'
		data = {
			'InstanceID': self.instanceID,
			'Position': '%s,%s' % (self.position[0], self.position[1]),
			'UnitID': self.unit_id,
			'BuildingRelation': named_flags(self.buildingRelation, ["Nydus Link","Addon Link"], 16, 9),
			'ValidAbilities': named_flags(self.validAbilities, ["Cloak", "Burrow", "In Transit", "Hullucinated", "Invincible"], 16),
			'ValidProperties': named_flags(self.validProperties, ["Owner", "Health", "Shields", "Energy", "Resources", "Hanger"], 16),
			'Owner': self.owner + 1,
			'Health': '%s%%' % self.health,
			'Shields': '%s%%' % self.shields,
			'Energy': '%s%%' % self.energy,
			'Resources': self.resources,
			'HangerUnits': self.hangerUnits,
			'AbilityStates': named_flags(self.validAbilities, ["Cloaked", "Burrowed", "In Transit", "Hullucinated", "Invincible"], 16),
			'UnitRelationID': self.unitRelationID
		}
		for key in ['InstanceID','Position','UnitID','BuildingRelation','ValidAbilities','ValidProperties','Owner','Health','Shields','Energy','Resources','HangerUnits','AbilityStates','UnitRelationID']:
			value = data[key]
			if isinstance(value, tuple):
				result += '\t%s%s\n' % (pad('#'), value[0])
				value = value[1]
			result += '\t%s\n' % pad(key, value)
		return result

class CHKSectionUNIT(CHKSection):
	NAME = 'UNIT'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.units = {}
		self.unused_ids = []
	
	def load_data(self, data):
		self.units = {}
		o = 0
		ref_id = 0
		while o+36 <= len(data):
			unit = CHKUnit(self.chk, ref_id)
			unit.load_data(data[o:o+36])
			self.units[ref_id] = unit
			ref_id += 1
			o += 36

	def unit_count(self):
		return len(self.units)

	def nth_unit(self, n):
		ref_ids = sorted(self.units.keys())
		return self.units[ref_ids[n]]

	def get_unit(self, ref_id):
		return self.units.get(ref_id)
	
	def save_data(self):
		result = ''
		for ref_id in sorted(self.units.keys()):
			unit = self.units[ref_id]
			result += unit.save_data()
		return result
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		for ref_id in sorted(self.units.keys()):
			unit = self.units[ref_id]
			result += unit.decompile()
		return result
