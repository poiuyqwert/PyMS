
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKUnitStats(object):
	def __init__(self):
		self.default = True
		self.health = 0
		self.shields = 0
		self.armor = 0
		self.buildTime = 0
		self.costMinerals = 0
		self.costGas = 0
		self.name = 0

class CHKWeaponStats(object):
	def __init__(self):
		self.damage = 0
		self.damageUpgrade = 0

class CHKSectionUNIS(CHKSection):
	NAME = 'UNIS'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_VANILLA_HYBRID, CHKRequirements.MODE_UMS)

	UNITS = 228
	WEAPONS = 100
	
	def __init__(self, chk: CHK) -> None:
		CHKSection.__init__(self, chk)
		self.unit_stats: list[CHKUnitStats] = []
		for _ in range(self.UNITS):
			self.unit_stats.append(CHKUnitStats())
		self.weapon_stats: list[CHKWeaponStats] = []
		for _ in range(self.WEAPONS):
			self.weapon_stats.append(CHKWeaponStats())
	
	def load_data(self, data: bytes) -> None:
		o = 0
		defaults = list(bool(v) for v in struct.unpack('<%dB' % self.UNITS, data[o:o+self.UNITS]))
		o += self.UNITS
		healths = list(int(v) for v in struct.unpack('<%dL' % self.UNITS, data[o:o+self.UNITS*4]))
		o += self.UNITS*4
		shields = list(int(v) for v in struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		armor = list(int(v) for v in struct.unpack('<%dB' % self.UNITS, data[o:o+self.UNITS]))
		o += self.UNITS
		buildTimes = list(int(v) for v in struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		costMinerals = list(int(v) for v in struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		costGas = list(int(v) for v in struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		names = list(int(v) for v in struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		for n,values in enumerate(zip(defaults,healths,shields,armor,buildTimes,costMinerals,costGas,names)):
			unit_stat = self.unit_stats[n]
			unit_stat.default,unit_stat.health,unit_stat.shields,unit_stat.armor,unit_stat.buildTime,unit_stat.costMinerals,unit_stat.costGas,unit_stat.name = values
		damage = list(int(v) for v in struct.unpack('<%dH' % self.WEAPONS, data[o:o+self.WEAPONS*2]))
		o += self.WEAPONS*2
		damageUpgrade = list(int(v) for v in struct.unpack('<%dH' % self.WEAPONS, data[o:o+self.WEAPONS*2]))
		for n,values in enumerate(zip(damage,damageUpgrade)):
			weapon_stat = self.weapon_stats[n]
			weapon_stat.damage,weapon_stat.damageUpgrade = values

	def save_data(self) -> bytes:
		defaults: list[bool] = []
		healths: list[int] = []
		shields: list[int] = []
		armor: list[int] = []
		buildTimes: list[int] = []
		costMinerals: list[int] = []
		costGas: list[int] = []
		names: list[int] = []
		damage: list[int] = []
		damageUpgrade: list[int] = []
		for unit_stats in self.unit_stats:
			defaults.append(unit_stats.default)
			healths.append(unit_stats.health)
			shields.append(unit_stats.shields)
			armor.append(unit_stats.armor)
			buildTimes.append(unit_stats.buildTime)
			costMinerals.append(unit_stats.costMinerals)
			costGas.append(unit_stats.costGas)
			names.append(unit_stats.name)
		for weapon_stats in self.weapon_stats:
			damage.append(weapon_stats.damage)
			damageUpgrade.append(weapon_stats.damageUpgrade)
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
	
	def decompile(self) -> str:
		result = '%s:\n' % (self.NAME)
		result += '\t' + pad('#')
		for name in ['Use Defaults','Health','Shields','Armor','Build Time','Mineral Cost','Gas Cost','Name']:
			result += pad(name)
		result += '\n'
		for n,unit_stats in enumerate(self.unit_stats):
			result += '\t' + pad('Unit%03d' % n)
			result += pad(unit_stats.default)
			result += pad(unit_stats.health / 256.0)
			result += pad(unit_stats.shields)
			result += pad(unit_stats.armor)
			result += pad(unit_stats.buildTime)
			result += pad(unit_stats.costMinerals)
			result += pad(unit_stats.costGas)
			result += '%s\n' % unit_stats.name
		result += '\t' + pad('#')
		for name in ['Damage','Damage Upgrade']:
			result += pad(name)
		result += '\n'
		for n,weapon_stats in enumerate(self.weapon_stats):
			result += '\t' + pad('Weapon%03d' % n)
			result += pad(weapon_stats.damage)
			result += '%s\n' % weapon_stats.damageUpgrade
		return result
