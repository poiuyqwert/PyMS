
from __future__ import annotations

from ...Utilities import Struct
from ...Utilities import IO

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

class PropertyDefinition:
	def __init__(self, name: str):
		self.name = name

class PropertyFieldDefinition(PropertyDefinition):
	def __init__(self, name: str, attr: str, parameter: Struct.IntField, flag: int):
		super().__init__(name)
		self.attr = attr
		self.parameter = parameter
		self.flag = flag

class PropertyStateDefinition(PropertyDefinition):
	def __init__(self, name: str, flag: int):
		super().__init__(name)
		self.flag = flag

properties_definitions: tuple[PropertyDefinition, ...] = (
	PropertyFieldDefinition('Owner', 'owner', Struct.l_u8, FieldFlag.owner),
	PropertyFieldDefinition('Health', 'hit_points', Struct.l_u8, FieldFlag.hit_points),
	PropertyFieldDefinition('Shields', 'shield_points', Struct.l_u8, FieldFlag.shield_points),
	PropertyFieldDefinition('Energy', 'energy', Struct.l_u8, FieldFlag.energy),
	PropertyFieldDefinition('Resources', 'resources', Struct.l_u32, FieldFlag.resources),
	PropertyFieldDefinition('HangerCount', 'hanger_count', Struct.l_u16, FieldFlag.hanger_count),
	PropertyStateDefinition('Cloaked', StateFlag.cloaked),
	PropertyStateDefinition('Burrowed', StateFlag.burrowed),
	PropertyStateDefinition('InTransit', StateFlag.in_transit),
	PropertyStateDefinition('Hallucinated', StateFlag.hallucinated),
	PropertyStateDefinition('Invincible', StateFlag.invincible)
)

class UnitProperties(Struct.Struct):
	states_available_flags: int
	fields_available_flags: int
	owner: int
	hit_points: int
	shield_points: int
	energy: int
	resources: int
	hanger_count: int
	state_flags: int

	_fields = (
		('states_available_flags', Struct.t_u16),
		('fields_available_flags', Struct.t_u16),
		('owner', Struct.t_u8),
		('hit_points', Struct.t_u8),
		('shield_points', Struct.t_u8),
		('energy', Struct.t_u8),
		('resources', Struct.t_u32),
		('hanger_count', Struct.t_u16),
		('state_flags', Struct.t_u16),
		Struct.t_pad(4)
	)

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

	def decompile(self, id: int, output: IO.AnyOutputText) -> None:
		with IO.OutputText(output) as f:
			f.write(f'UnitProperties({id}):')
			for definition in properties_definitions:
				if isinstance(definition, PropertyFieldDefinition) and self.fields_available_flags & definition.flag:
					f.write(f'\n  {definition.name}({getattr(self, definition.attr)})')
				elif isinstance(definition, PropertyStateDefinition) and self.state_flags & definition.flag:
					f.write(f'\n  {definition.name}()')

	def __eq__(self, other) -> bool:
		if not isinstance(other, UnitProperties):
			return False
		if other.fields_available_flags != self.fields_available_flags:
			return False
		if other.state_flags != self.state_flags:
			return False
		if other.fields_available_flags & FieldFlag.owner and other.owner != self.owner:
			return False
		if other.fields_available_flags & FieldFlag.hit_points and other.hit_points != self.hit_points:
			return False
		if other.fields_available_flags & FieldFlag.shield_points and other.shield_points != self.shield_points:
			return False
		if other.fields_available_flags & FieldFlag.energy and other.energy != self.energy:
			return False
		if other.fields_available_flags & FieldFlag.resources and other.resources != self.resources:
			return False
		if other.fields_available_flags & FieldFlag.hanger_count and other.hanger_count != self.hanger_count:
			return False
		return True
