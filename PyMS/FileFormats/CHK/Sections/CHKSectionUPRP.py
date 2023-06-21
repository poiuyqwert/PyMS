
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad, named_flags

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKUnitProperties(object):
	def __init__(self, chk): # type: (CHK) -> None
		self.chk = chk
		self.validAbilities = 0
		self.validProperties = 0
		self.owner = 0
		self.health = 0
		self.shields = 0
		self.energy = 0
		self.resources = 0
		self.hangerUnits = 0
		self.abilityStates = 0

	def load_data(self, data): # type: (bytes) -> None
		self.validAbilities,self.validProperties,self.owner,self.health,self.shields,self.energy,self.resources,self.hangerUnits,self.abilityStates = \
			tuple(int(v) for v in struct.unpack('<2H4BL2H4x', data[:20]))

	def save_data(self): # type: () -> bytes
		return struct.pack('<2H4BL2H4x', self.validAbilities,self.validProperties,self.owner,self.health,self.shields,self.energy,self.resources,self.hangerUnits,self.abilityStates)

	def decompile(self): # type: () -> str
		result = '\t#\n'
		data = {
			'ValidAbilities': named_flags(self.validAbilities, ["Cloak", "Burrow", "In Transit", "Hullucinated", "Invincible"], 16),
			'ValidProperties': named_flags(self.validProperties, ["Owner", "Health", "Shields", "Energy", "Resources", "Hanger"], 16),
			'Owner': self.owner + 1,
			'Health': '%s%%' % self.health,
			'Shields': '%s%%' % self.shields,
			'Energy': '%s%%' % self.energy,
			'Resources': self.resources,
			'HangerUnits': self.hangerUnits,
			'AbilityStates': named_flags(self.validAbilities, ["Cloaked", "Burrowed", "In Transit", "Hullucinated", "Invincible"], 16),
		}
		for key in ['ValidAbilities','ValidProperties','Owner','Health','Shields','Energy','Resources','HangerUnits','AbilityStates']:
			value = data[key]
			if isinstance(value, tuple):
				result += '\t%s%s\n' % (pad('#'), value[0])
				value = value[1]
			result += '\t%s\n' % pad(key, str(value))
		return result

class CHKSectionUPRP(CHKSection):
	NAME = 'UPRP'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)
	
	def __init__(self, chk): # type: (CHK) -> None
		CHKSection.__init__(self, chk)
		self.properties = [] # type: list[CHKUnitProperties]
	
	def load_data(self, data): # type: (bytes) -> None
		self.properties = []
		o = 0
		while o+20 <= len(data):
			properties = CHKUnitProperties(self.chk)
			properties.load_data(data[o:o+20])
			self.properties.append(properties)
			o += 20
	
	def save_data(self): # type: () -> bytes
		result = b''
		for properties in self.properties:
			result += properties.save_data()
		return result
	
	def decompile(self): # type: () -> str
		result = '%s:\n' % (self.NAME)
		for properties in self.properties:
			result += properties.decompile()
		return result
