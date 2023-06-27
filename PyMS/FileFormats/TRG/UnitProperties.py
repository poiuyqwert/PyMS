
from ...Utilities.BytesScanner import BytesScanner
from ...Utilities import Serialize
from ...Utilities import IO

import struct

class StateFlag:
	cloaked = (1 << 0)
	burrowed = (1 << 1)
	in_transit = (1 << 2)
	hallucinated = (1 << 3)
	invincible = (1 << 4)

class FieldFlag:
	owner = (1 << 0)
	hit_points = (1 << 1)
	shield_points = (1 << 2)
	energy = (1 << 3)
	resources = (1 << 4)
	hanger_count = (1 << 5)

class UnitProperties:
	def __init__(self) -> None:
		self.states_available_flags = 0
		self.fields_available_flags = 0
		self.owner = 0
		self.hit_points = 0
		self.shield_points = 0
		self.energy = 0
		self.resources = 0
		self.hanger_count = 0
		self.state_flags = 0

	STRUCT = struct.Struct('<2L4BH2LH')
	def load_data(self, scanner: BytesScanner) -> None:
		self.states_available_flags,self.fields_available_flags,self.owner,self.hit_points,self.shield_points,self.energy,self.resources,self.hanger_count,self.state_flags = scanner.scan_ints(UnitProperties.STRUCT)

	def save_data(self, output: IO.AnyOutputBytes):
		data = UnitProperties.STRUCT.pack(self.states_available_flags,self.fields_available_flags,self.owner,self.hit_points,self.shield_points,self.energy,self.resources,self.hanger_count,self.state_flags)
		with IO.OutputBytes(output) as f:
			f.write(data)

UnitPropertiesDefinition = Serialize.Definition('Properties', Serialize.IDMode.header, {
	'states_available_flags': Serialize.IntFlagEncoder({
		'cloaked': StateFlag.cloaked,
		'burrowed': StateFlag.burrowed,
		'in_transit': StateFlag.in_transit,
		'hallucinated': StateFlag.hallucinated,
		'invincible': StateFlag.invincible,
	}),
	'fields_available_flags': Serialize.IntFlagEncoder({
		'owner': FieldFlag.owner,
		'hit_points': FieldFlag.hit_points,
		'shield_points': FieldFlag.shield_points,
		'energy': FieldFlag.energy,
		'resources': FieldFlag.resources,
		'hanger_count': FieldFlag.hanger_count,
	}),
	'owner': Serialize.IntEncoder(),
	'hit_points': Serialize.IntEncoder(),
	'shield_points': Serialize.IntEncoder(),
	'energy': Serialize.IntEncoder(),
	'resources': Serialize.IntEncoder(),
	'hanger_count': Serialize.IntEncoder(),
	'states_flags': Serialize.IntFlagEncoder({
		'cloaked': StateFlag.cloaked,
		'burrowed': StateFlag.burrowed,
		'in_transit': StateFlag.in_transit,
		'hallucinated': StateFlag.hallucinated,
		'invincible': StateFlag.invincible,
	}),
})