
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKUnitStats:
	def __init__(self):
		self.default = True
		self.health = 0
		self.shields = 0
		self.armor = 0
		self.buildTime = 0
		self.costMinerals = 0
		self.costGas = 0
		self.name = 0
class CHKWeaponStats:
	def __init__(self):
		self.damage = 0
		self.damageUpgrade = 0

class CHKSectionUNIS(CHKSection):
	NAME = 'UNIS'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_VANILLA_HYBRID, CHKRequirements.MODE_UMS)

	UNITS = 228
	WEAPONS = 100
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.unit_stats = []
		for _ in range(self.UNITS):
			self.unit_stats.append(CHKUnitStats())
		self.weapon_stats = []
		for _ in range(self.WEAPONS):
			self.weapon_stats.append(CHKWeaponStats())
	
	def load_data(self, data):
		o = 0
		defaults = list(struct.unpack('<%dB' % self.UNITS, data[o:o+self.UNITS]))
		o += self.UNITS
		healths = list(struct.unpack('<%dL' % self.UNITS, data[o:o+self.UNITS*4]))
		o += self.UNITS*4
		shields = list(struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		armor = list(struct.unpack('<%dB' % self.UNITS, data[o:o+self.UNITS]))
		o += self.UNITS
		buildTimes = list(struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		costMinerals = list(struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		costGas = list(struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		names = list(struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		for n,values in enumerate(zip(defaults,healths,shields,armor,buildTimes,costMinerals,costGas,names)):
			stat = self.unit_stats[n]
			stat.default,stat.health,stat.shields,stat.armor,stat.buildTime,stat.costMinerals,stat.costGas,stat.name = values
		damage = list(struct.unpack('<%dH' % self.WEAPONS, data[o:o+self.WEAPONS*2]))
		o += self.WEAPONS*2
		damageUpgrade = list(struct.unpack('<%dH' % self.WEAPONS, data[o:o+self.WEAPONS*2]))
		for n,values in enumerate(zip(damage,damageUpgrade)):
			stat = self.weapon_stats[n]
			stat.damage,stat.damageUpgrade = values

	def save_data(self):
		defaults = []
		healths = []
		shields = []
		armor = []
		buildTimes = []
		costMinerals = []
		costGas = []
		names = []
		damage = []
		damageUpgrade = []
		for stat in self.unit_stats:
			defaults.append(stat.default)
			healths.append(stat.health)
			shields.append(stat.shields)
			armor.append(stat.armor)
			buildTimes.append(stat.buildTime)
			costMinerals.append(stat.costMinerals)
			costGas.append(stat.costGas)
			names.append(stat.name)
		for stat in self.weapon_stats:
			damage.append(stat.damage)
			damageUpgrade.append(stat.damageUpgrade)
		result = struct.pack('<%dB' % self.UNITS, *defaults)
		result += struct.pack('<%dL' % self.UNITS, *healths)
		result += struct.pack('<%dH' % self.UNITS, *shields)
		result += struct.pack('<%dB' % self.UNITS, *armor)
		result += struct.pack('<%dH' % self.UNITS, *buildTimes)
		result += struct.pack('<%dH' % self.UNITS, *costMinerals)
		result += struct.pack('<%dH' % self.UNITS, *costGas)
		result += struct.pack('<%dH' % self.UNITS, *names)
		result += struct.pack('<%dH' % self.WEAPONS, *damage)
		result += struct.pack('<%dH' % self.WEAPONS, *damageUpgrade)
		return result
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		result += '\t' + pad('#')
		for name in ['Use Defaults','Health','Shields','Armor','Build Time','Mineral Cost','Gas Cost','Name']:
			result += pad(name)
		result += '\n'
		for n,stat in enumerate(self.unit_stats):
			result += '\t' + pad('Unit%03d' % n)
			result += pad(stat.default)
			result += pad(stat.health / 256.0)
			result += pad(stat.shields)
			result += pad(stat.armor)
			result += pad(stat.buildTime)
			result += pad(stat.costMinerals)
			result += pad(stat.costGas)
			result += '%s\n' % stat.name
		result += '\t' + pad('#')
		for name in ['Damage','Damage Upgrade']:
			result += pad(name)
		result += '\n'
		for n,stat in enumerate(self.weapon_stats):
			result += '\t' + pad('Weapon%03d' % n)
			result += pad(stat.damage)
			result += '%s\n' % stat.damageUpgrade
		return result
