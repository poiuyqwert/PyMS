
from __future__ import annotations

from ....Utilities.BytesScanner import BytesScanner
from ....Utilities import Struct
from ....Utilities.PyMSError import PyMSError
from ....Utilities.CodeHandlers import CodeType
from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers import Tokens
from ....Utilities.CodeHandlers.ByteCodeCompiler import ByteCodeBuilderType

from dataclasses import dataclass

from typing import runtime_checkable, Protocol, Self, Type, cast, Sequence

@runtime_checkable
class Option(Protocol):
	TYPE_ID: int 

	@classmethod
	def decompile(cls, value: int, scanner: BytesScanner) -> Self:
		...

	def serialize(self) -> str:
		...

	def merge(self, other: Option) -> bool:
		...

	# TODO: Update complicated parsers to use CodeType parsing instead of custom parsing?
	@classmethod
	def parse(cls, parse_context: ParseContext) -> Self | None:
		...

	def compile(self, context: ByteCodeBuilderType) -> None:
		...

	@classmethod
	def keywords(cls) -> Sequence[str]:
		...

_OPTION_TYPES: dict[int, Type[Option]] = {}

def build_command_word(type: int, value: int = 0) -> int:
	return (type << 8) & OptionSet.TYPE_MASK | (value & OptionSet.VALUE_MASK)

@dataclass
class BasicFlags(Option):
	TYPE_ID = 0

	class Flag:
		not_enemies = 0x1
		own = 0x2
		allied = 0x4
		unseen = 0x8
		invisible = 0x10
		in_combat = 0x20
		deathrattle = 0x40
		remove_silent_fail = 0x4000
		remove = 0x8000

		_NAMES = {
			not_enemies: 'NotEnemies',
			own: 'Own',
			allied: 'Allied',
			unseen: 'Unseen',
			invisible: 'Invisible',
			in_combat: 'InCombat',
			deathrattle: 'Deathrattle',
			remove_silent_fail: 'RemoveSilentFail',
			remove: 'Remove',
		}
		_VALUES = dict((v.lower(), k) for k, v in _NAMES.items())

	flags: int

	@classmethod
	def decompile(cls, value: int, scanner: BytesScanner) -> Self:
		return cls(value)

	def serialize(self) -> str:
		return CodeType.FlagsCodeType.serialize_flags(self.flags, BasicFlags.Flag._NAMES, Struct.l_u16, '')

	def merge(self, other: Option) -> bool:
		if not isinstance(other, BasicFlags):
			return False
		self.flags |= other.flags
		return True

	@classmethod
	def parse(cls, parse_context: ParseContext) -> Self | None:
		token = parse_context.lexer.next_token(peek=True)
		flag = BasicFlags.Flag._VALUES.get(token.raw_value.lower())
		if flag is None:
			return None
		_ = parse_context.lexer.next_token()
		return cls(flag)

	def compile(self, context: ByteCodeBuilderType) -> None:
		context.add_data(Struct.l_u16.pack(build_command_word(BasicFlags.TYPE_ID, self.flags)))

	@classmethod
	def keywords(cls) -> Sequence[str]:
		return tuple(BasicFlags.Flag._NAMES.values())

@dataclass
class SpellEffects(Option):
	TYPE_ID = 1

	class Flag:
		ensnare = 0x1
		plague = 0x2
		lockdown = 0x4
		irradiate = 0x8
		parasite = 0x10
		blind = 0x20
		matrix = 0x40
		maelstrom = 0x80
		stim = 0x4000

		_NAMES = {
			ensnare: 'Ensnare',
			plague: 'Plague',
			lockdown: 'Lockdown',
			irradiate: 'Irradiate',
			parasite: 'Parasite',
			blind: 'Blind',
			matrix: 'Matrix',
			maelstrom: 'Maelstrom',
			stim: 'Stim',
		}
		_VALUES = dict((v.lower(), k) for k, v in _NAMES.items())

	flags: int

	@classmethod
	def decompile(cls, value: int, scanner: BytesScanner) -> Self:
		return cls(value)

	def serialize(self) -> str:
		return f'{self.__class__.__name__}({CodeType.FlagsCodeType.serialize_flags(self.flags, SpellEffects.Flag._NAMES, Struct.l_u16)})'

	def merge(self, other: Option) -> bool:
		if not isinstance(other, self.__class__):
			return False
		self.flags |= other.flags
		return True

	@classmethod
	def parse(cls, parse_context: ParseContext) -> Self | None:
		token = parse_context.lexer.next_token(peek=True)
		if not token.raw_value == cls.__name__:
			return None
		_ = parse_context.lexer.next_token()
		token = parse_context.lexer.next_token()
		if not token.raw_value == '(':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `(` after `{cls.__name__}` to start flags)')
		flags = CodeType.FlagsCodeType.lex_flags(parse_context, SpellEffects.Flag._VALUES, cls.__name__, Struct.l_u16, case_sensitive=False)
		invalid_flags = (flags & OptionSet.TYPE_MASK)
		if invalid_flags:
			raise parse_context.error('Parse', f'Invalid flags `0x{invalid_flags:X}` for `{cls.__name__}`')
		token = parse_context.lexer.next_token()
		if not token.raw_value == ')':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `)` to end `{cls.__name__}` flags)')
		return cls(flags)

	def compile(self, context: ByteCodeBuilderType) -> None:
		context.add_data(Struct.l_u16.pack(build_command_word(self.TYPE_ID, self.flags)))

	@classmethod
	def keywords(cls) -> Sequence[str]:
		return (cls.__name__,) + tuple(SpellEffects.Flag._NAMES.values())

class WithoutSpellEffects(SpellEffects):
	TYPE_ID = 2

@dataclass
class UnitProps(Option):
	TYPE_ID = 3

	class Field:
		hp = 0
		shields = 1
		health = 2
		energy = 3
		hangar = 4
		cargo = 5

		_NAMES = {
			hp: 'Hp',
			shields: 'Shields',
			health: 'Health',
			energy: 'Energy',
			hangar: 'Hangar',
			cargo: 'Cargo',
		}
		_VALUES = dict((v.lower(), k) for k, v in _NAMES.items())

	class Comparison:
		less_than = 0
		greater_than = 1
		less_than_percent = 2
		greater_than_percent = 3

		_NAMES = {
			less_than: 'LessThan',
			greater_than: 'GreaterThan',
			less_than_percent: 'LessThanPercent',
			greater_than_percent: 'GreaterThanPercent',
		}
		_VALUES = dict((v.lower(), k) for k, v in _NAMES.items())

	field: int
	comparison: int
	amount: int

	@classmethod
	def decompile(cls, value: int, scanner: BytesScanner) -> Self:
		field = (value >> 4) & 0xF
		if not field in UnitProps.Field._NAMES:
			raise PyMSError('Decompile', f'`{field}` is not a valid `idle_order_flags` `{cls.__name__}` field')
		comparison = value & 0xF
		if not comparison in UnitProps.Comparison._NAMES:
			raise PyMSError('Decompile', f'`{comparison}` is not a valid `idle_order_flags` `{cls.__name__}` comparison type')
		return cls(field, comparison, scanner.scan(Struct.l_u32))

	@staticmethod
	def uses_fixed_point_decimal(field: int, comparison: int) -> bool:
		return field < UnitProps.Field.hangar and (comparison == UnitProps.Comparison.less_than or comparison == UnitProps.Comparison.greater_than)

	def serialize(self) -> str:
		amount: float = self.amount
		if UnitProps.uses_fixed_point_decimal(self.field, self.comparison):
			amount = amount / 256.0
		return f'{UnitProps.Field._NAMES[self.field]}({UnitProps.Comparison._NAMES[self.comparison]}, {amount:g})'

	def merge(self, other: Option) -> bool:
		if other == self:
			return True
		return False

	@classmethod
	def parse(cls, parse_context: ParseContext) -> Self | None:
		token = parse_context.lexer.next_token(peek=True)
		field_name = token.raw_value
		field = UnitProps.Field._VALUES.get(field_name.lower())
		if field is None:
			return None
		_ = parse_context.lexer.next_token()
		token = parse_context.lexer.next_token()
		if not token.raw_value == '(':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `(` after `{field_name}` to start `{cls.__name__}` option)')
		token = parse_context.lexer.next_token()
		comparison = UnitProps.Comparison._VALUES.get(token.raw_value.lower())
		if comparison is None:
			raise parse_context.error('Parse', f'Invalid comparison `{token.raw_value}` for `{cls.__name__}` option')
		token = parse_context.lexer.next_token()
		if not token.raw_value == ',':
			raise parse_context.error('Parse', f'Expected comma between `{cls.__name__}` comparison and amount, but got `{token.raw_value}`')
		uses_fixed_point_decimal = UnitProps.uses_fixed_point_decimal(field, comparison)
		allowed = 'integer'
		if uses_fixed_point_decimal:
			allowed += ' or float'
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IntegerToken) and (not uses_fixed_point_decimal or not isinstance(token, Tokens.FloatToken)):
			raise parse_context.error('Parse', f'Expected an {allowed} amount for `{cls.__name__}` but got `{token.raw_value}`')
		try:
			amount = float(token.raw_value)
		except:
			raise PyMSError('Parse', f'Invalid value `{token.raw_value}` for `{cls.__name__}` amount (expected an {allowed})')
		# TODO: Validate amount
		token = parse_context.lexer.next_token()
		if not token.raw_value == ')':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `)` to end `{field_name}` `{cls.__name__}` option)')
		if uses_fixed_point_decimal:
			amount *= 256
		return cls(field, comparison, int(amount))

	def compile(self, context: ByteCodeBuilderType) -> None:
		value = (self.field & 0xF) << 4 | (self.comparison & 0xF)
		context.add_data(Struct.l_u16.pack(build_command_word(UnitProps.TYPE_ID, value)))
		context.add_data(Struct.l_u32.pack(self.amount))

	@classmethod
	def keywords(cls) -> Sequence[str]:
		return tuple(UnitProps.Field._NAMES.values()) + tuple(UnitProps.Comparison._NAMES.values())

@dataclass
class OptionSet(Option):
	TYPE_ID = 4

	TYPE_MASK = 0x2F00
	VALUE_MASK = 0xC0FF

	options: tuple[Option, ...]

	def simplify(self) -> None:
		options: dict[int, list[Option]] = {}
		for option in self.options:
			if not option.TYPE_ID in options:
				options[option.TYPE_ID] = []
			existing_options = options[option.TYPE_ID]
			if isinstance(option, OptionSet):
				option.simplify()
				existing_options.append(option)
			else:
				for existing_option in existing_options:
					if existing_option.merge(option):
						break
				else:
					existing_options.append(option)
		if len(options) == 1 and OptionSet.TYPE_ID in options and len(options[OptionSet.TYPE_ID]) == 1:
			self.options = cast(OptionSet, options[OptionSet.TYPE_ID][0]).options
		else:
			self.options = tuple(option for options in options.values() for option in options)

	@classmethod
	def decompile(cls, value: int, scanner: BytesScanner) -> Self:
		option_set: list[Option] = []
		while True:
			command = scanner.scan(Struct.l_u16)
			type = (command & OptionSet.TYPE_MASK) >> 8
			value = command & OptionSet.VALUE_MASK
			option_type = _OPTION_TYPES.get(type)
			if not option_type:
				raise PyMSError('Decompile', f'`{type}` is not a valid `idle_order_flags` option type')
			option_set.append(option_type.decompile(value, scanner))
			if type == BasicFlags.TYPE_ID:
				break
		result = cls(tuple(option_set))
		result.simplify()
		return result

	def serialize_options(self) -> str:
		count = len(self.options)
		return ' | '.join(option.serialize() for option in self.options if not isinstance(option, BasicFlags) or option.flags or count == 1)

	def serialize(self) -> str:
		return f'Self({self.serialize_options()})'

	def merge(self, other: Option) -> bool:
		if other == self:
			return True
		return False

	@classmethod
	def parse_options(cls, parse_context: ParseContext, is_root: bool = True) -> Self:
		option_set: list[Option] = []
		while True:
			if is_root:
				token = parse_context.lexer.next_token(peek=True)
				if token.raw_value == ',':
					break
			for option_type in _option_types:
				option = option_type.parse(parse_context)
				if option is not None:
					option_set.append(option)
					break
			else:
				token = parse_context.lexer.next_token()
				raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected an `idle_order_flags` option)')
			token = parse_context.lexer.next_token(peek=True)
			if token.raw_value == '|':
				_ = parse_context.lexer.next_token()
			else:
				break
		result = cls(tuple(option_set))
		result.simplify()
		return result

	@classmethod
	def parse(cls, parse_context: ParseContext) -> Self | None:
		token = parse_context.lexer.next_token(peek=True)
		if not token.raw_value == 'Self':
			return None
		_ = parse_context.lexer.next_token()
		token = parse_context.lexer.next_token()
		if not token.raw_value == '(':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `(` after `Self` to start option set)')
		option_set = cls.parse_options(parse_context, False)
		token = parse_context.lexer.next_token()
		if not token.raw_value == ')':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `)` to end `Self` option set)')
		return option_set

	def compile_options(self, context: ByteCodeBuilderType) -> None:
		self.simplify()
		options: list[Option] = []
		basic_flags: BasicFlags | None = None
		for option in self.options:
			if isinstance(option, BasicFlags):
				basic_flags = option
			else:
				options.append(option)
		if basic_flags is None:
			options.append(BasicFlags(0))
		else:
			options.append(basic_flags)
		
		for option in options:
			option.compile(context)

	def compile(self, context: ByteCodeBuilderType) -> None:
		context.add_data(Struct.l_u16.pack(build_command_word(OptionSet.TYPE_ID)))
		self.compile_options(context)

	@classmethod
	def keywords(cls) -> Sequence[str]:
		return ('Self',)

@dataclass
class Order(Option):
	TYPE_ID = 5

	order_id: int

	@classmethod
	def decompile(cls, value: int, scanner: BytesScanner) -> Self:
		return cls(value)

	def serialize(self) -> str:
		from .AISECodeTypes import OrderCodeType
		return f'Order({OrderCodeType().serialize_basic(self.order_id)})'

	def merge(self, other: Option) -> bool:
		if other == self:
			return True
		return False

	@classmethod
	def parse(cls, parse_context: ParseContext) -> Self | None:
		from .AISECodeTypes import OrderCodeType
		token = parse_context.lexer.next_token(peek=True)
		if not token.raw_value == 'Order':
			return None
		_ = parse_context.lexer.next_token()
		token = parse_context.lexer.next_token()
		if not token.raw_value == '(':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `(` after `{cls.__name__}`)')
		order_id = OrderCodeType().parse(parse_context)
		token = parse_context.lexer.next_token()
		if not token.raw_value == ')':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `)` to end `{cls.__name__}`)')
		return cls(order_id)

	def compile(self, context: ByteCodeBuilderType) -> None:
		context.add_data(Struct.l_u16.pack(build_command_word(Order.TYPE_ID, self.order_id)))

	@classmethod
	def keywords(cls) -> Sequence[str]:
		from .AISECodeTypes import OrderCodeType
		return ('Order',) + tuple(OrderCodeType().keywords())

@dataclass
class UnitFlags(Option):
	TYPE_ID = 6

	class Flag:
		building = 0x1
		addon = 0x2
		air = 0x4
		worker = 0x8
		turret = 0x10
		flying_building = 0x20
		hero = 0x40
		regeneration = 0x80
		animated_overlay = 0x100
		cloakable = 0x200
		dual_birth = 0x400
		powerup = 0x800
		resource_depot = 0x1000
		resource_container = 0x2000
		robotic = 0x4000
		detector = 0x8000
		organic = 0x10000
		requires_creep = 0x20000
		unk40000 = 0x40000
		requires_psi = 0x80000
		burrower = 0x100000
		spellcaster = 0x200000
		permanently_cloaked = 0x400000
		carryable = 0x800000
		ignore_supply_check = 0x1000000
		medium_overlays = 0x2000000
		large_overlays = 0x4000000
		can_move = 0x8000000
		full_auto_attack = 0x10000000
		invincible = 0x20000000
		mechanical = 0x40000000
		unk_produces_units = 0x80000000
		
		_NAMES = {
			building: 'Building',
			addon: 'Addon',
			air: 'Air',
			worker: 'Worker',
			turret: 'Turret',
			flying_building: 'FlyingBuilding',
			hero: 'Hero',
			regeneration: 'Regeneration',
			animated_overlay: 'AnimatedOverlay',
			cloakable: 'Cloakable',
			dual_birth: 'DualBirth',
			powerup: 'Powerup',
			resource_depot: 'ResourceDepot',
			resource_container: 'ResourceContainer',
			robotic: 'Robotic',
			detector: 'Detector',
			organic: 'Organic',
			requires_creep: 'RequiresCreep',
			unk40000: 'Unk40000',
			requires_psi: 'RequiresPsi',
			burrower: 'Burrower',
			spellcaster: 'Spellcaster',
			permanently_cloaked: 'PermanentlyCloaked',
			carryable: 'Carryable',
			ignore_supply_check: 'IgnoreSupplyCheck',
			medium_overlays: 'MediumOverlays',
			large_overlays: 'LargeOverlays',
			can_move: 'CanMove',
			full_auto_attack: 'FullAutoAttack',
			invincible: 'Invincible',
			mechanical: 'Mechanical',
			unk_produces_units: 'UnkProducesUnits',
		}
		_VALUES = {
			'building': building,
			'addon': addon,
			'air': air,
			'worker': worker,
			'turret': turret,
			'flyingbuilding': flying_building,
			'hero': hero,
			'regeneration': regeneration,
			'animatedoverlay': animated_overlay,
			'cloakable': cloakable,
			'dualbirth': dual_birth,
			'powerup': powerup,
			'resourcedepot': resource_depot,
			'resourcecontainer': resource_container,
			'robotic': robotic,
			'detector': detector,
			'organic': organic,
			'requirescreep': requires_creep,
			'unk40000': unk40000,
			'requirespsi': requires_psi,
			'burrower': burrower,
			'spellcaster': spellcaster,
			'permanentlycloaked': permanently_cloaked,
			'permamentlycloaked': permanently_cloaked, # Old AISE had a typo here, so we accept both names
			'carryable': carryable,
			'ignoresupplycheck': ignore_supply_check,
			'mediumoverlays': medium_overlays,
			'largeoverlays': large_overlays,
			'canmove': can_move,
			'fullautoattack': full_auto_attack,
			'invincible': invincible,
			'mechanical': mechanical,
			'unkproducesunits': unk_produces_units,
		}

	without: bool
	flags: int

	@classmethod
	def decompile(cls, value: int, scanner: BytesScanner) -> Self:
		return cls(value == 1, scanner.scan(Struct.l_u32))

	def serialize(self) -> str:
		return f'{"Without" if self.without else ""}UnitFlags({CodeType.FlagsCodeType.serialize_flags(self.flags, UnitFlags.Flag._NAMES, Struct.l_u32)})'

	def merge(self, other: Option) -> bool:
		if not isinstance(other, UnitFlags) or other.without != self.without:
			return False
		self.flags |= other.flags
		return True

	@classmethod
	def parse(cls, parse_context: ParseContext) -> Self | None:
		token = parse_context.lexer.next_token(peek=True)
		name = token.raw_value
		if not name in ('UnitFlags', 'WithoutUnitFlags'):
			return None
		_ = parse_context.lexer.next_token()
		without = name.startswith('Without')
		token = parse_context.lexer.next_token()
		if not token.raw_value == '(':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `(` after `{cls.__name__}` to start flags)')
		flags = CodeType.FlagsCodeType.lex_flags(parse_context, UnitFlags.Flag._VALUES, cls.__name__, Struct.l_u32, case_sensitive=False)
		invalid_flags = (flags & OptionSet.TYPE_MASK)
		if invalid_flags:
			raise parse_context.error('Parse', f'Invalid flags `0x{invalid_flags:X}` for `{cls.__name__}`')
		token = parse_context.lexer.next_token()
		if not token.raw_value == ')':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `)` to end `{cls.__name__}` flags)')
		return cls(without, flags)

	def compile(self, context: ByteCodeBuilderType) -> None:
		context.add_data(Struct.l_u16.pack(build_command_word(UnitFlags.TYPE_ID, self.without)))
		context.add_data(Struct.l_u32.pack(self.flags))

	@classmethod
	def keywords(cls) -> Sequence[str]:
		return ('UnitFlags', 'WithoutUnitFlags') + tuple(UnitFlags.Flag._NAMES.values())

@dataclass
class Targetting(Option):
	TYPE_ID = 7

	class Flag:
		other_unit = 0x1
		enemy = 0x2
		ally = 0x4
		own = 0x8
		nothing = 0x10

		_NAMES = {
			other_unit: 'OtherUnit',
			enemy: 'Enemy',
			ally: 'Ally',
			own: 'Own',
			nothing: 'Nothing',
		}
		_VALUES = dict((v.lower(), k) for k, v in _NAMES.items())

	flags: int

	@classmethod
	def decompile(cls, value: int, scanner: BytesScanner) -> Self:
		return cls(value)

	def serialize(self) -> str:
		return f'Targetting({CodeType.FlagsCodeType.serialize_flags(self.flags, Targetting.Flag._NAMES, Struct.l_u32)})'

	def merge(self, other: Option) -> bool:
		if not isinstance(other, Targetting):
			return False
		self.flags |= other.flags
		return True

	@classmethod
	def parse(cls, parse_context: ParseContext) -> Self | None:
		token = parse_context.lexer.next_token(peek=True)
		if not token.raw_value == 'Targetting':
			return None
		_ = parse_context.lexer.next_token()
		token = parse_context.lexer.next_token()
		if not token.raw_value == '(':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `(` after `{cls.__name__}` to start flags)')
		flags = CodeType.FlagsCodeType.lex_flags(parse_context, Targetting.Flag._VALUES, 'Targetting', Struct.l_u8, case_sensitive=False)
		invalid_flags = (flags & OptionSet.TYPE_MASK)
		if invalid_flags:
			raise parse_context.error('Parse', f'Invalid flags `0x{invalid_flags:X}` for `{cls.__name__}`')
		token = parse_context.lexer.next_token()
		if not token.raw_value == ')':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `)` to end `{cls.__name__}` flags)')
		return cls(flags)

	def compile(self, context: ByteCodeBuilderType) -> None:
		context.add_data(Struct.l_u16.pack(build_command_word(Targetting.TYPE_ID, self.flags)))

	@classmethod
	def keywords(cls) -> Sequence[str]:
		return ('Targetting',) + tuple(Targetting.Flag._NAMES.values())

@dataclass
class RandomRate(Option):
	TYPE_ID = 8

	low: int
	high: int

	@classmethod
	def decompile(cls, value: int, scanner: BytesScanner) -> Self:
		return cls(scanner.scan(Struct.l_u16), scanner.scan(Struct.l_u16))

	def serialize(self) -> str:
		return f'RandomRate({self.low}, {self.high})'

	def merge(self, other: Option) -> bool:
		if other == self:
			return True
		return False

	@classmethod
	def parse(cls, parse_context: ParseContext) -> Self | None:
		token = parse_context.lexer.next_token(peek=True)
		if not token.raw_value == 'RandomRate':
			return None
		_ = parse_context.lexer.next_token()
		token = parse_context.lexer.next_token()
		if not token.raw_value == '(':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `(` after `{cls.__name__}`)')
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IntegerToken):
			raise parse_context.error('Parse', f'Expected an integer for `{cls.__name__}` low but got `{token.raw_value}`')
		try:
			low = int(token.raw_value)
		except:
			raise PyMSError('Parse', f'Invalid value `{token.raw_value}` for `{cls.__name__}` low (expected an integer)')
		# TODO: Validate low
		token = parse_context.lexer.next_token()
		if not token.raw_value == ',':
			raise parse_context.error('Parse', f'Expected comma between `{cls.__name__}` low and high, but got `{token.raw_value}`')
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IntegerToken):
			raise parse_context.error('Parse', f'Expected an integer for `{cls.__name__}` high but got `{token.raw_value}`')
		try:
			high = int(token.raw_value)
		except:
			raise PyMSError('Parse', f'Invalid value `{token.raw_value}` for `{cls.__name__}` high (expected an integer)')
		# TODO: Validate high
		token = parse_context.lexer.next_token()
		if not token.raw_value == ')':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `)` to end `{cls.__name__}`)')
		return cls(low, high)

	def compile(self, context: ByteCodeBuilderType) -> None:
		context.add_data(Struct.l_u16.pack(build_command_word(RandomRate.TYPE_ID)))
		context.add_data(Struct.l_u16.pack(self.low))
		context.add_data(Struct.l_u16.pack(self.high))

	@classmethod
	def keywords(cls) -> Sequence[str]:
		return ('RandomRate',)

@dataclass
class UnitCount(Option):
	TYPE_ID = 9

	class Comparison:
		at_least = 0
		at_most = 1
		exactly = 10

		_NAMES = {
			at_least: 'AtLeast',
			at_most: 'AtMost',
			exactly: 'Exactly',
		}
		_VALUES = dict((v.lower(), k) for k, v in _NAMES.items())

	comparison: int
	amount: int
	radius: int
	players: int

	@classmethod
	def decompile(cls, value: int, scanner: BytesScanner) -> Self:
		comparison = scanner.scan(Struct.l_u8)
		if not comparison in UnitCount.Comparison._NAMES:
			raise PyMSError('Decompile', f'`{comparison}` is not a valid `idle_order_flags` `{cls.__name__}` comparison type')
		return cls(comparison, scanner.scan(Struct.l_u16), scanner.scan(Struct.l_u16), scanner.scan(Struct.l_u8))

	def serialize(self) -> str:
		return f'Count({UnitCount.Comparison._NAMES[self.comparison]}, {self.amount}, {self.radius}, {self.players})'

	def merge(self, other: Option) -> bool:
		if other == self:
			return True
		return False

	@classmethod
	def parse(cls, parse_context: ParseContext) -> Self | None:
		token = parse_context.lexer.next_token(peek=True)
		if not token.raw_value == 'Count':
			return None
		_ = parse_context.lexer.next_token()
		token = parse_context.lexer.next_token()
		if not token.raw_value == '(':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `(` after `{cls.__name__}`)')
		token = parse_context.lexer.next_token()
		comparison = UnitCount.Comparison._VALUES.get(token.raw_value.lower())
		if comparison is None:
			raise parse_context.error('Parse', f'Invalid comparison `{token.raw_value}` for `{cls.__name__}` option')
		token = parse_context.lexer.next_token()
		if not token.raw_value == ',':
			raise parse_context.error('Parse', f'Expected comma between `{cls.__name__}` comparison and amount, but got `{token.raw_value}`')
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IntegerToken):
			raise parse_context.error('Parse', f'Expected an integer for `{cls.__name__}` amount but got `{token.raw_value}`')
		try:
			amount = int(token.raw_value)
		except:
			raise PyMSError('Parse', f'Invalid value `{token.raw_value}` for `{cls.__name__}` amount (expected an integer)')
		# TODO: Validate amount
		token = parse_context.lexer.next_token()
		if not token.raw_value == ',':
			raise parse_context.error('Parse', f'Expected comma between `{cls.__name__}` amount and radius, but got `{token.raw_value}`')
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IntegerToken):
			raise parse_context.error('Parse', f'Expected an integer for `{cls.__name__}` radius but got `{token.raw_value}`')
		try:
			radius = int(token.raw_value)
		except:
			raise PyMSError('Parse', f'Invalid value `{token.raw_value}` for `{cls.__name__}` radius (expected an integer)')
		# TODO: Validate radius
		token = parse_context.lexer.next_token()
		if not token.raw_value == ',':
			raise parse_context.error('Parse', f'Expected comma between `{cls.__name__}` radius and players, but got `{token.raw_value}`')
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IntegerToken):
			raise parse_context.error('Parse', f'Expected an integer for `{cls.__name__}` players but got `{token.raw_value}`')
		try:
			players = int(token.raw_value)
		except:
			raise PyMSError('Parse', f'Invalid value `{token.raw_value}` for `{cls.__name__}` players (expected an integer)')
		# TODO: Validate players
		token = parse_context.lexer.next_token()
		if not token.raw_value == ')':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `)` to end `{cls.__name__}`)')
		return cls(comparison, amount, radius, players)

	def compile(self, context: ByteCodeBuilderType) -> None:
		context.add_data(Struct.l_u16.pack(build_command_word(UnitCount.TYPE_ID)))
		context.add_data(Struct.l_u8.pack(self.comparison))
		context.add_data(Struct.l_u16.pack(self.amount))
		context.add_data(Struct.l_u16.pack(self.radius))
		context.add_data(Struct.l_u8.pack(self.players))

	@classmethod
	def keywords(cls) -> Sequence[str]:
		return ('Count',) + tuple(UnitCount.Comparison._NAMES.values())

@dataclass
class TileFlags(Option):
	TYPE_ID = 10

	class Flag:
		walkable = 0x1
		unbuildable = 0x2
		creep = 0x4
		ramp = 0x8

		_NAMES = {
			walkable: 'Walkable',
			unbuildable: 'Unbuildable',
			creep: 'Creep',
			ramp: 'Ramp',
		}
		_VALUES = dict((v.lower(), k) for k, v in _NAMES.items())

	without: bool
	flags: int

	@classmethod
	def decompile(cls, value: int, scanner: BytesScanner) -> Self:
		return cls(value == 1, scanner.scan(Struct.l_u8))

	def serialize(self) -> str:
		return f'{"Without" if self.without else ""}TileFlags({CodeType.FlagsCodeType.serialize_flags(self.flags, TileFlags.Flag._NAMES, Struct.l_u8)})'

	def merge(self, other: Option) -> bool:
		if not isinstance(other, UnitFlags) or other.without != self.without:
			return False
		self.flags |= other.flags
		return True

	@classmethod
	def parse(cls, parse_context: ParseContext) -> Self | None:
		token = parse_context.lexer.next_token(peek=True)
		name = token.raw_value
		if not name in ('TileFlags', 'WithoutTileFlags'):
			return None
		_ = parse_context.lexer.next_token()
		without = name.startswith('Without')
		token = parse_context.lexer.next_token()
		if not token.raw_value == '(':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `(` after `{name}` to start flags)')
		flags = CodeType.FlagsCodeType.lex_flags(parse_context, TileFlags.Flag._VALUES, name, Struct.l_u8, case_sensitive=False)
		invalid_flags = (flags & OptionSet.TYPE_MASK)
		if invalid_flags:
			raise parse_context.error('Parse', f'Invalid flags `0x{invalid_flags:X}` for `{name}`')
		token = parse_context.lexer.next_token()
		if not token.raw_value == ')':
			raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `)` to end `{name}` flags)')
		return cls(without, flags)

	def compile(self, context: ByteCodeBuilderType) -> None:
		context.add_data(Struct.l_u16.pack(build_command_word(TileFlags.TYPE_ID, self.without)))
		context.add_data(Struct.l_u8.pack(self.flags))

	@classmethod
	def keywords(cls) -> Sequence[str]:
		return ('TileFlags', 'WithoutTileFlags') + tuple(TileFlags.Flag._NAMES.values())

_option_types: list[Type[Option]] = [
	BasicFlags,
	SpellEffects, WithoutSpellEffects,
	UnitProps,
	OptionSet,
	Order,
	UnitFlags,
	Targetting,
	RandomRate,
	UnitCount,
	TileFlags,
]
for option_type in _option_types:
	_OPTION_TYPES[option_type.TYPE_ID] = option_type
