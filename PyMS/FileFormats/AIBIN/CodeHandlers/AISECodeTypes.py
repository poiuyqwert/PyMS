
from __future__ import annotations

from .AIByteCodeCompiler import AIByteCodeCompiler
from .AIDecompileContext import AIDecompileContext
from . import CodeTypes
from . import AISEIdleOrder

from ....Utilities import Struct
from ....Utilities.CodeHandlers import CodeType
from ....Utilities.CodeHandlers.CodeBlock import CodeBlock
from ....Utilities.CodeHandlers.SerializeContext import SerializeContext
from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers.ByteCodeCompiler import ByteCodeBuilderType
from ....Utilities.CodeHandlers.DecompileContext import DecompileContext
from ....Utilities.CodeHandlers import Tokens
from ....Utilities.BytesScanner import BytesScanner
from ....Utilities.PyMSError import PyMSError

import re

from typing import cast, Sequence

class LongBlockCodeType(CodeTypes.BlockCodeType):
	def compile(self, block: CodeBlock, context: ByteCodeBuilderType) -> None:
		bytecode_type: Struct.IntField = cast(Struct.IntField, self._bytecode_type)
		if isinstance(context, AIByteCodeCompiler) and context.aise_context.expanded:
			bytecode_type = Struct.l_u32
		context.add_block_ref(block, bytecode_type)

	def decompile(self, scanner: BytesScanner, context: DecompileContext) -> CodeBlock:
		bytecode_type: Struct.IntField = cast(Struct.IntField, self._bytecode_type)
		if isinstance(context, AIDecompileContext) and context.aise_context.expanded:
			bytecode_type = Struct.l_u32
		return scanner.scan(bytecode_type) # type: ignore

Point = tuple[int, int]
class PointCodeType(CodeType.CodeType[Point, Point]):
	LOCATION = 65535
	SCRIPT_AREA = 65534

	def __init__(self) -> None:
		super().__init__('point', "A point, either `(x, y)`, `Loc.{location id}`, or `ScriptArea`", Struct.l_au16(2), False)

	def decompile(self, scanner: BytesScanner, context: DecompileContext) -> Point:
		return tuple(super().decompile(scanner, context)) # type: ignore

	def serialize(self, value: Point, context: SerializeContext) -> str:
		if context.definitions:
			variable = context.definitions.lookup_variable(value, self)
			if variable:
				return variable.name
		if value[0] == PointCodeType.LOCATION:
			return f'Loc.{value[1]}'
		elif value[0] == PointCodeType.SCRIPT_AREA:
			return 'ScriptArea'
		else:
			return f'({value[0]}, {value[1]})'

	def _lex(self, parse_context: ParseContext) -> Point:
		token = parse_context.lexer.next_token()
		if token.raw_value == '(':
			token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.IntegerToken):
				raise parse_context.error('Parse', f'Expected integer value in `{self.name}` x value, but got `{token.raw_value}`')
			try:
				x = int(token.raw_value)
			except:
				raise parse_context.error('Parse', f'Invalid integer value in `{self.name}` x value (got `{token.raw_value}`)')
			token = parse_context.lexer.next_token()
			if not token.raw_value == ',':
				raise parse_context.error('Parse', f'Expected comma between `{self.name}` x and y values, but got `{token.raw_value}`')
			token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.IntegerToken):
				raise parse_context.error('Parse', f'Expected integer value in `{self.name}` y value, but got `{token.raw_value}`')
			try:
				y = int(token.raw_value)
			except:
				raise parse_context.error('Parse', f'Invalid integer value in `{self.name}` y value (got `{token.raw_value}`)')
			token = parse_context.lexer.next_token()
			if not token.raw_value == ')':
				raise parse_context.error('Parse', f'Expected `)` to end `{self.name}`, but got `{token.raw_value}`')
			return (x, y)
		elif token.raw_value == 'Loc':
			token = parse_context.lexer.next_token()
			if not token.raw_value == '.':
				raise parse_context.error('Parse', f'Expected `.` after `Loc` for `{self.name}`, but got `{token.raw_value}`')
			token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.IntegerToken):
				raise parse_context.error('Parse', f'Expected integer value for `{self.name}` location id, but got `{token.raw_value}`')
			try:
				loc = int(token.raw_value)
			except:
				raise parse_context.error('Parse', f'Invalid integer value in `{self.name}` location id (got `{token.raw_value}`)')
			return (PointCodeType.LOCATION, loc)
		elif token.raw_value == 'ScriptArea':
			return (PointCodeType.SCRIPT_AREA, 0)
		raise parse_context.error('Parse', f'Expected a `{self.name}` value but got `{token.raw_value}`')

	def validate(self, value: Point, parse_context: ParseContext, token: str | None = None) -> None:
		# TODO: Do we need to validate any other cases?
		if value[0] == PointCodeType.LOCATION and value[1] > 255:
			raise PyMSError('Parse', f"Location id `{value[1]}` is not valid (must be a number from 0 to 255)")

class OrderCodeType(CodeType.EnumCodeType):
	ORDER_NAMES = [
			'Die',
			'Stop',
			'Guard',
			'PlayerGuard',
			'TurretGuard',
			'BunkerGuard',
			'Move',
			'ReaverStop',
			'Attack',
			'AttackObscured',
			'AttackUnit',
			'AttackFixedRange',
			'AttackTile',
			'Hover',
			'AttackMove',
			'BeingInfested',
			'UnusedNothing',
			'UnusedPowerup',
			'TowerGuard',
			'TowerAttack',
			'SpiderMine',
			'StayInRange',
			'TurretAttack',
			'Nothing',
			'Nothing3',
			'DroneStartBuild',
			'DroneBuild',
			'MoveToInfest',
			'InfestObscured',
			'InfestMine4',
			'BuildTerran',
			'BuildProtoss1',
			'BuildProtoss2',
			'ConstructingBuilding',
			'Repair',
			'RepairObscured',
			'PlaceAddon',
			'BuildAddon',
			'Train',
			'RallyPointUnit',
			'RallyPointTile',
			'Birth',
			'UnitMorph',
			'BuildingMorph',
			'TerranBuildSelf',
			'ZergBuildSelf',
			'BuildNydusExit',
			'EnterNydus',
			'ProtossBuildSelf',
			'Follow',
			'Carrier',
			'ReaverCarrierMove',
			'CarrierStop',
			'CarrierAttack',
			'CarrierAttackObscured',
			'CarrierIgnore2',
			'CarrierFight',
			'CarrierHoldPosition',
			'Reaver',
			'ReaverAttack',
			'ReaverAttackObscured',
			'ReaverFight',
			'ReaverHoldPosition',
			'TrainFighter',
			'Interceptor',
			'Scarab',
			'RechargeShieldsUnit',
			'RechargeShieldsBattery',
			'ShieldBattery',
			'InterceptorReturn',
			'DroneLand',
			'Land',
			'LiftOff',
			'DroneLiftOff',
			'LiftingOff',
			'Tech',
			'Upgrade',
			'Larva',
			'SpawningLarva',
			'Harvest',
			'HarvestObscured',
			'MoveToGas',
			'WaitForGas',
			'HarvestGas',
			'ReturnGas',
			'MoveToMinerals',
			'WaitForMinerals',
			'MiningMinerals',
			'MineralHarvestInterrupted',
			'StopHarvest',
			'ReturnMinerals',
			'Interrupted',
			'EnterTransport',
			'TransportIdle',
			'PickupTransport',
			'PickupBunker',
			'Pickup4',
			'PowerupIdle',
			'SiegeMode',
			'TankMode',
			'WatchTarget',
			'InitCreepGrowth',
			'SpreadCreep',
			'StoppingCreepGrowth',
			'GuardianAspect',
			'WarpingArchon',
			'CompletingArchonSummon',
			'HoldPosition',
			'QueenHoldPosition',
			'Cloak',
			'Decloak',
			'Unload',
			'MoveUnload',
			'YamatoGun',
			'YamatoGunObscured',
			'Lockdown',
			'Burrow',
			'Burrowed',
			'Unburrow',
			'DarkSwarm',
			'Parasite',
			'SpawnBroodlings',
			'EmpShockwave',
			'NukeWait',
			'NukeTrain',
			'NukeLaunch',
			'NukePaint',
			'NukeUnit',
			'NukeGround',
			'NukeTrack',
			'InitArbiter',
			'CloakNearbyUnits',
			'PlaceMine',
			'RightClick',
			'SapUnit',
			'SapLocation',
			'SuicideHoldPosition',
			'Recall',
			'BeingRecalled',
			'Scan',
			'ScannerSweep',
			'DefensiveMatrix',
			'PsiStorm',
			'Irradiate',
			'Plague',
			'Consume',
			'Ensnare',
			'StasisField',
			'Hallucination',
			'Hallucinated',
			'ResetCollision1',
			'ResetCollision2',
			'Patrol',
			'CtfCopInit',
			'CtfCopStarted',
			'CtfCop2',
			'ComputerAi',
			'AiAttackMove',
			'HarassMove',
			'AiPatrol',
			'AiGuard',
			'RescuePassive',
			'Neutral',
			'ComputerReturn',
			'InitPylon',
			'SelfDestructing',
			'Critter',
			'Trap',
			'OpenDoor',
			'CloseDoor',
			'HideTrap',
			'RevealTrap',
			'EnableDoodad',
			'DisableDoodad',
			'WarpIn',
			'Medic',
			'Heal',
			'HealMove',
			'MedicHoldPosition',
			'HealToIdle',
			'Restoration',
			'DisruptionWeb',
			'MindControl',
			'WarpingDarkArchon',
			'Feedback',
			'OpticalFlare',
			'Maelstrom',
			'JunkYardDog',
			'Fatal',
		]

	def __init__(self) -> None:
		super().__init__('order', 'An order ID from 0 to 188, or a [hardcoded] order name', Struct.l_u8, OrderCodeType.ORDER_NAMES, allow_integer=True)

class UnitIDCodeType(CodeTypes.UnitCodeType, CodeType.HasKeywords):
	def __init__(self, name: str = 'unit_id', help_text: str = 'Same as unit type, but also accepts: 228/None, 229/Any, 230/Group_Men, 231/Group_Buildings, 232/Group_Factories') -> None:
		super().__init__(name, help_text)

	def _lex(self, parse_context: ParseContext) -> int:
		rollback = parse_context.lexer.get_rollback()
		token = parse_context.lexer.next_token()
		if isinstance(token, Tokens.IdentifierToken):
			group = token.raw_value.lower()
			if group == 'none':
				return 228
			elif group == 'any':
				return 229
			elif group == 'group_men':
				return 230
			elif group == 'group_buildings':
				return 231
			elif group == 'group_factories':
				return 232
		parse_context.lexer.rollback(rollback)
		return super()._lex(parse_context)

	def validate(self, num: int, parse_context: ParseContext | None, token: str | None = None) -> None:
		if num >= 228 and num <= 232:
			return
		super().validate(num, parse_context, token)

	def serialize(self, value: int, context: SerializeContext) -> str:
		if value == 228:
			return 'None'
		elif value == 229:
			return 'Any'
		elif value == 230:
			return 'Group_Men'
		elif value == 231:
			return 'Group_Buildings'
		elif value == 232:
			return 'Group_Factories'
		return super().serialize(value, context)

	def keywords(self) -> Sequence[str]:
		return ('None', 'Any', 'Group_Men', 'Group_Buildings', 'Group_Factories')

UnitGroup = tuple[int, ...]
class UnitGroupCodeType(CodeType.CodeType[UnitGroup, UnitGroup]):
	def __init__(self) -> None:
		self._unit_id_code_type = UnitIDCodeType()
		super().__init__('unit_group', "Same as unit_id, but allows multiple with '|'", Struct.l_u16, False)

	def decompile(self, scanner: BytesScanner, context: DecompileContext) -> UnitGroup:
		value = scanner.scan(Struct.l_u16)
		if value < 0xFF00:
			return (value,)
		count = value & 0xFF
		groups: list[int] = []
		for _ in range(count):
			groups.append(scanner.scan(Struct.l_u16))
		return tuple(groups)

	def compile(self, groups: UnitGroup, context: ByteCodeBuilderType) -> None:
		count = len(groups)
		if count > 1:
			assert count <= 0xFF
			context.add_data(Struct.l_u16.pack(0xFF00 | count))
		for group in groups:
			context.add_data(Struct.l_u16.pack(group))

	def _lex(self, parse_context: ParseContext) -> UnitGroup:
		groups: list[int] = []
		while True:
			groups.append(self._unit_id_code_type._lex(parse_context))
			token = parse_context.lexer.next_token(peek=True)
			if token.raw_value == '|':
				_ = parse_context.lexer.next_token()
			else:
				break
		return tuple(groups)

	RE_OR = re.compile(r'\s*\|\s*')
	def validate(self, groups: UnitGroup, parse_context: ParseContext, token: str | None = None):
		tokens: list[str | None] = []
		if token is not None:
			tokens = UnitGroupCodeType.RE_OR.split(token)
		while len(tokens) < len(groups):
			tokens.append(None)
		for group, group_token in zip(groups, tokens):
			self._unit_id_code_type.validate(group, parse_context, group_token)

	def serialize(self, groups: UnitGroup, context: SerializeContext) -> str:
		return ' | '.join(self._unit_id_code_type.serialize(group, context) for group in groups)

Area = tuple[Point, int]
class AreaCodeType(CodeType.CodeType[Area, Area]):
	def __init__(self) -> None:
		self._point_code_type = PointCodeType()
		super().__init__('area', "An area in form 'point [~ radius]'", Struct.l_u16, False)

	def decompile(self, scanner: BytesScanner, context: DecompileContext) -> Area:
		point = self._point_code_type.decompile(scanner, context)
		radius = scanner.scan(Struct.l_u16)
		return (point, radius)

	def compile(self, value: Area, context: ByteCodeBuilderType) -> None:
		self._point_code_type.compile(value[0], context)
		context.add_data(Struct.l_u16.pack(value[1]))

	def _lex(self, parse_context: ParseContext) -> Area:
		point = self._point_code_type._lex(parse_context)
		radius = 0
		token = parse_context.lexer.next_token(peek=True)
		if token.raw_value == '~':
			_ = parse_context.lexer.next_token()
			token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.IntegerToken):
				raise parse_context.error('Parse', f'Expected integer value for `{self.name}` radius value, but got `{token.raw_value}`')
			try:
				radius = int(token.raw_value)
			except:
				raise PyMSError('Parse', f'Invalid integer value for `{self.name}` radius value, got `{token.raw_value}`')
		return (point, radius)

	def validate(self, value: Area, parse_context: ParseContext, token: str | None = None) -> None:
		self._point_code_type.validate(value[0], parse_context, token)

	def serialize(self, value: Area, context: SerializeContext) -> str:
		code = self._point_code_type.serialize(value[0], context)
		if value[1] > 0:
			code += f' ~ {value[1]}'
		return code

class IssueOrderFlagsCodeType(CodeType.FlagsCodeType):
	def __init__(self) -> None:
		help_text = """An integer/hex flag, or any of the following:
	Enemies
	Own
	Allied
	SingleUnit
	EachAtMostOnce
	IgnoreDatReqs"""
		super().__init__('issue_order_flags', help_text, Struct.l_u16, {
			'Enemies': 0x01,
			'Own': 0x02,
			'Allied': 0x04,
			'SingleUnit': 0x08,
			'EachAtMostOnce': 0x10,
			'IgnoreDatReqs': 0x40,
		})

class CompareTrigCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		help_text = """One of:
	AtLeast
	AtMost
	Set
	Add
	Subtract
	Exactly
	Randomize
	AtLeast_Call
	AtMost_Call
	Exactly_Call
	AtLeast_Wait
	AtMost_Wait
	Exactly_Wait"""
		super().__init__('compare_trig', help_text, Struct.l_u8, {
			'AtLeast': 0,
			'AtMost': 1,
			'Set': 7,
			'Add': 8,
			'Subtract': 9,
			'Exactly': 10,
			'Randomize': 11,
			'AtLeast_Call': 128,
			'AtMost_Call': 129,
			'Exactly_Call': 138,
			'AtLeast_Wait': 64,
			'AtMost_Wait': 65,
			'Exactly_Wait': 74,
		})

class IdleOrderCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		cases: dict[str, int] = {}
		for n, order_name in enumerate(OrderCodeType.ORDER_NAMES):
			cases[order_name] = n
		cases['EnableBuiltin'] = 254
		cases['DisableBuiltin'] = 255
		super().__init__('idle_order', 'An order ID from 0 to 188, a [hardcoded] order name, or DisableBuiltin/EnableBuiltin',Struct.l_u8, cases, allow_integer=True)

class IdleOrderFlagsCodeType(CodeType.CodeType[AISEIdleOrder.OptionSet, AISEIdleOrder.OptionSet]):
	def __init__(self) -> None:
		help_text = """Any of the following:
	NotEnemies
	Own
	Allied
	Unseen
	Invisible
	RemoveSilentFail
	Remove"""
		super().__init__('idle_order_flags', help_text, Struct.l_u16, False)

	def decompile(self, scanner: BytesScanner, context: DecompileContext) -> AISEIdleOrder.OptionSet:
		return AISEIdleOrder.OptionSet.decompile(0, scanner)

	def serialize(self, value: AISEIdleOrder.OptionSet, context: SerializeContext) -> str:
		return value.serialize_options()

# Not sure if it's easy to decipher or not but the few main points in the binary encoding there were
# - The data was originally just u16 bitflags, but then got extended to have more complex settings that didn't fit in a single u16
# - So it became list of u16 that contains a 'parameter type' and has some bits for the parameter data, but some parameters needed more data so they have extra bytes (not necessarily u16) before a new parameter starts with a u16
# - The list is terminated with the u16 parameter that has type 0, the non-type bits there still are used for bitflags
# - Type 4 is Self(...) opcode that contains an entire another idle_order_flags-encoded sequence 😇
# - I seem to have written pyms side to allow nesting Self(flag1 | Self(Self(flag2))) but that is not really meaningful thing and the plugin side seems to parse it as just Self(flag1)

	# def ai_idle_order_flags(self, data, stage=0):
	# 	"""idle_order_flags        - Any of the following:
	# 		NotEnemies
	# 		Own
	# 		Allied
	# 		Unseen
	# 		Invisible
	# 		RemoveSilentFail
	# 		Remove
	# 	"""
	# 	if stage == 0:
	# 		pos = 0
	# 		current = []
	# 		stack = []
	# 		depth = 0
	# 		while True:
	# 			v, = struct.unpack('<H', data[pos:pos + 2])
	# 			if (v & 0x2f00) >> 8 == 3:
	# 				# i32 amount
	# 				amt, = struct.unpack('<I', data[pos + 2:pos + 6])
	# 				current += [(v, amt)]
	# 				pos += 6
	# 			elif (v & 0x2f00) >> 8 == 4:
	# 				depth += 1
	# 				current += [(v,)]
	# 				stack.append(current)
	# 				current = []
	# 				pos += 2
	# 			elif (v & 0x2f00) >> 8 == 6:
	# 				# u32 units.dat flags
	# 				amt, = struct.unpack('<I', data[pos + 2:pos + 6])
	# 				current += [(v, amt)]
	# 				pos += 6
	# 			elif (v & 0x2f00) >> 8 == 8:
	# 				# u16 low, u16 high
	# 				vars = struct.unpack('<HH', data[pos + 2:pos + 6])
	# 				current += [(v, vars)]
	# 				pos += 6
	# 			elif (v & 0x2f00) >> 8 == 9:
	# 				#u8,u8,u16,u16
	# 				vars = struct.unpack('<BHHB',data[pos+2:pos+8])
	# 				current += [(v,vars)]
	# 				pos += 8
	# 			elif (v & 0x2f00) >> 8 == 10:
	# 				# u8 tile flags
	# 				amt, = struct.unpack('<B', data[pos + 2:pos + 3])
	# 				current += [(v, amt)]
	# 				pos += 3
	# 			else:
	# 				current += [(v,)]
	# 				pos += 2
	# 			if v & 0x2f00 == 0:
	# 				if depth == 0:
	# 					result = current
	# 					return [pos, result]
	# 				else:
	# 					depth -= 1
	# 					finished = current
	# 					current = stack.pop()
	# 					current[-1] = (current[-1][0], finished)
	# 	elif stage == 1:
	# 		size, basic_flags = (
	# 			self.flags(data[-1][0], stage, idle_order_flag_names, idle_order_flag_reverse)
	# 		)
	# 		result = '' if basic_flags == '0' else basic_flags
	# 		for extended in data[:-1]:
	# 			if result != '':
	# 				result += ' | '
	# 			ty = (extended[0] & 0x2f00) >> 8
	# 			val = extended[0] & 0xc0ff
	# 			if ty == 1:
	# 				result += 'SpellEffects(%s)' % flags_to_str(val, spell_effect_names)
	# 			elif ty == 2:
	# 				result += 'WithoutSpellEffects(%s)' % flags_to_str(val, spell_effect_names)
	# 			elif ty == 3:
	# 				# Maybe it's actually fine to just show BROKEN if the script is broken
	# 				# instead of erroring? Users can give better error reports =)
	# 				ty = 'BROKEN'
	# 				compare = 'BROKEN'
	# 				c_id = val & 0xf
	# 				ty_id = (val >> 4) & 0xf
	# 				# Raw Hp/shield/etc values are converted to displayed values
	# 				fixed_point_decimal = (c_id == 0 or c_id == 1) and (ty_id < 4)
	# 				if fixed_point_decimal:
	# 					amount = str(float(extended[1]) / 256)
	# 				else:
	# 					amount = str(int(extended[1]))
	# 				if c_id == 0:
	# 					compare = 'LessThan'
	# 				elif c_id == 1:
	# 					compare = 'GreaterThan'
	# 				elif c_id == 2:
	# 					compare = 'LessThanPercent'
	# 				elif c_id == 3:
	# 					compare = 'GreaterThanPercent'
	# 				if ty_id == 0:
	# 					ty = 'Hp'
	# 				elif ty_id == 1:
	# 					ty = 'Shields'
	# 				elif ty_id == 2:
	# 					ty = 'Health'
	# 				elif ty_id == 3:
	# 					ty = 'Energy'
	# 				elif ty_id == 4:
	# 					ty = 'Hangar'
	# 				elif ty_id == 5:
	# 					ty = 'Cargo'
	# 				result += '%s(%s, %s)' % (ty, compare, amount)
	# 				size += 4
	# 			elif ty == 4:
	# 				subgroup = extended[1]
	# 				sz, self_flags = self.ai_idle_order_flags(subgroup, 1)
	# 				result += 'Self(' + self_flags + ')'
	# 				size += sz
	# 			elif ty == 5:
	# 				_, order_name = self.ai_order(val, 1)
	# 				result += 'Order(%s)' % order_name
	# 			elif ty == 6:
	# 				flags = extended[1]
	# 				if val == 0:
	# 					result += 'UnitFlags(%s)' % flags_to_str(flags, units_dat_flags)
	# 				elif val == 1:
	# 					result += 'WithoutUnitFlags(%s)' % flags_to_str(flags, units_dat_flags)
	# 				size += 4
	# 			elif ty == 7:
	# 				result += 'Targeting(%s)' % flags_to_str(val, idle_orders_targeting_flags)
	# 			elif ty == 8:
	# 				result += "RandomRate(%s, %s)" % (extended[1][0],extended[1][1])
	# 				size += 4
	# 			elif ty == 9:
	# 				compare = 'BROKEN'
	# 				c_id = extended[1][0]
	# 				if c_id == 0:
	# 					compare = 'AtLeast'
	# 				elif c_id == 1:
	# 					compare = 'AtMost'
	# 				elif c_id == 10:
	# 					compare = 'Exactly'
	# 				result += "Count(%s, %s, %s, %s)" % (compare, extended[1][1], extended[1][2], extended[1][3])
	# 				size += 6
	# 			elif ty == 10:
	# 				flags = extended[1]
	# 				if val == 0:
	# 					result += 'TileFlags(%s)' % flags_to_str(flags, tile_flags)
	# 				elif val == 1:
	# 					result += 'WithoutTileFlags(%s)' % flags_to_str(flags, tile_flags)
	# 				size += 1
	# 			else:
	# 				raise PyMSError('Parameter', 'Invalid idle_orders encoding')
	# 			size += 2
	# 		if result == '':
	# 			result = '0'
	# 		return [size, result]
	# 	elif stage == 2:
	# 		result = ''
	# 		size = 0
	# 		for x in data:
	# 			result += struct.pack('<H', x[0])
	# 			size += 2
	# 			if (x[0] & 0x2f00) >> 8 == 3:
	# 				result += struct.pack('<I', x[1])
	# 				size += 4
	# 			if (x[0] & 0x2f00) >> 8 == 4:
	# 				sz, res = self.ai_idle_order_flags(x[1], 2)
	# 				size += sz
	# 				result += res
	# 			if (x[0] & 0x2f00) >> 8 == 6:
	# 				result += struct.pack('<I', x[1])
	# 				size += 4
	# 			if (x[0] & 0x2f00) >> 8 == 8:
	# 				result += struct.pack('<HH', x[1][0], x[1][1])
	# 				size += 4
	# 			if(x[0] & 0x2f00) >> 8 == 9:
	# 				result += struct.pack('<BHHB',x[1][0],x[1][1],x[1][2],x[1][3])
	# 				size += 6
	# 			if(x[0] & 0x2f00) >> 8 == 10:
	# 				result += struct.pack('B',x[1])
	# 				size += 1
	# 		return [size, result]
	# 	elif stage == 3:
	# 		result = []
	# 		size = 0

	# 		data = data.lower()
	# 		# Finds a subgroup and returns the text with the subgroup removed and subgroup
	# 		# not including the name/parens
	# 		def find_subgroup(text, match):
	# 			assert match.isalpha()
	# 			match = re.search(match + r'\s*[([{]', text)
	# 			if match is None:
	# 				return (text, '')

	# 			pos = match.end()
	# 			open_char = text[pos - 1]
	# 			if open_char == '(':
	# 			    end_char = ')'
	# 			elif open_char == '[':
	# 			    end_char = ']'
	# 			elif open_char == '{':
	# 			    end_char = '}'
	# 			depth = 0
	# 			while pos < len(text):
	# 				if text[pos] == end_char:
	# 					if depth == 0:
	# 						rest = text[:match.start()] + text[pos + 1:]
	# 						subgroup = text[match.end():pos]
	# 						return (rest, subgroup)
	# 					else:
	# 						depth -= 1
	# 				if text[pos] == open_char:
	# 					depth += 1
	# 				pos += 1
	# 			return (text, '')

	# 		while True:
	# 			data, self_flags = find_subgroup(data, 'self')
	# 			if self_flags != '':
	# 				sz, self_flags_bin = self.ai_idle_order_flags(self_flags, 3)
	# 				size += sz + 2
	# 				result += [(0x400, self_flags_bin)]
	# 			else:
	# 				break
	# 		parts = [x.lower().strip() for x in data.split('|')]
	# 		parts = [x for x in parts if x != '']
	# 		parts = [x for x in parts if not x.isspace()]
	# 		simple = []
	# 		extended = []
	# 		depth = 0
	# 		for x in parts:
	# 			old_depth = depth
	# 			depth += x.count('(')
	# 			depth += x.count('[')
	# 			depth += x.count('{')
	# 			depth -= x.count(')')
	# 			depth -= x.count(']')
	# 			depth -= x.count('}')
	# 			if old_depth == 0 and not ('(' in x or '[' in x or '{' in x):
	# 				simple.append(x)
	# 			else:
	# 				if old_depth == 0:
	# 					extended.append(x)
	# 				else:
	# 					extended[-1] = extended[-1] + '|' + x

	# 		for e in extended:
	# 			match = re.match(r'(\w*)\((.*)\)', e)
	# 			if match:
	# 				name = match.group(1)
	# 				if name == 'spelleffects' or name == 'withoutspelleffects':
	# 					flags = match.group(2)
	# 					val = flags_from_str(flags, spell_effect_names_reverse)
	# 					if (val & 0x2f00) != 0:
	# 						raise PyMSError('Parameter', 'Invalid idle_orders flag %s' % e)
	# 					if name == 'spelleffects':
	# 						result += [(0x100 | val,)]
	# 					else:
	# 						result += [(0x200 | val,)]
	# 				elif name in ('hp', 'shields', 'health', 'energy', 'hangar','cargo'):
	# 					params = match.group(2).split(',')
	# 					if len(params) != 2:
	# 						raise PyMSError('Parameter', 'Invalid idle_orders flag %s' % e)
	# 					compare = params[0]
	# 					amount = float(params[1])
	# 					if name == 'hp':
	# 						ty_id = 0x0
	# 					elif name == 'shields':
	# 						ty_id = 0x1
	# 					elif name == 'health':
	# 						ty_id = 0x2
	# 					elif name == 'energy':
	# 						ty_id = 0x3
	# 					elif name == 'hangar':
	# 						ty_id = 0x4
	# 					elif name == 'cargo':
	# 						ty_id = 0x5
	# 					else:
	# 						raise PyMSError('Parameter', 'Invalid idle_orders flag %s' % e)
	# 					if compare == 'lessthan':
	# 						compare_id = 0x0
	# 					elif compare == 'greaterthan':
	# 						compare_id = 0x1
	# 					elif compare == 'lessthanpercent':
	# 						compare_id = 0x2
	# 					elif compare == 'greaterthanpercent':
	# 						compare_id = 0x3
	# 					else:
	# 						raise PyMSError('Parameter', 'Invalid idle_orders flag %s' % e)
	# 					val = compare_id | (ty_id << 4)
	# 					# Raw Hp/shield/etc values are converted from displayed values
	# 					fixed_point_decimal = (compare_id == 0 or compare_id == 1) and (ty_id < 4)
	# 					if fixed_point_decimal:
	# 						amount *= 256
	# 					result += [(0x300 | val, int(amount))]
	# 					size += 4
	# 				elif name == 'order':
	# 					_, val = self.ai_order(match.group(2).strip(), 3)
	# 					result += [(0x500 | val,)]
	# 				elif name == 'unitflags' or name == 'withoutunitflags':
	# 					flags = match.group(2)
	# 					val = flags_from_str(flags, units_dat_flags_reverse)
	# 					if name == 'unitflags':
	# 						result += [(0x600, val)]
	# 					else:
	# 						result += [(0x601, val)]
	# 					size += 4
	# 				elif name == 'targeting':
	# 					flags = match.group(2)
	# 					val = flags_from_str(flags, idle_orders_targeting_flags_reverse)
	# 					if val >= 0x100:
	# 						raise PyMSError('Parameter', 'Invalid idle_orders targeting flag %s' % e)
	# 					result += [(0x700 | val,)]
	# 				elif name == 'randomrate':
	# 					params = match.group(2).split(',')
	# 					arg1 = int(params[0])
	# 					arg2 = int(params[1])
	# 					result += [(0x800, (arg1,arg2))]
	# 					size += 4
	# 				elif name == 'count':
	# 					params = match.group(2).split(',')
	# 					compare = params[0]
	# 					val = 0
	# 					if compare == 'atleast':
	# 						val |= 0x0
	# 					elif compare == 'atmost':
	# 						val |= 0x1
	# 					elif compare == 'exactly':
	# 						val |= 0xa
	# 					arg1 = int(val)
	# 					arg2 = int(params[1])
	# 					arg3 = int(params[2])
	# 					arg4 = int(params[3])
	# 					result += [(0x900, (arg1,arg2,arg3,arg4))]
	# 				elif name == 'tileflags' or name == 'withouttileflags':
	# 					flags = match.group(2)
	# 					val = flags_from_str(flags, tile_flags_reverse)
	# 					if name == 'tileflags':
	# 						result += [(0xa00, val)]
	# 					else:
	# 						result += [(0xa01, val)]
	# 					size += 1
	# 					size += 6
	# 				else:
	# 					raise PyMSError('Parameter', 'Invalid idle_orders flag %s' % e)
	# 				size += 2
	# 			else:
	# 				raise PyMSError('Parameter', 'Invalid idle_orders flag %s' % e)
	# 		basic_size, basic_result = (
	# 			self.flags('|'.join(simple), stage, idle_order_flag_names, idle_order_flag_reverse)
	# 		)
	# 		if basic_result & 0x2f00 != 0:
	# 			raise PyMSError('Parameter', 'Invalid idle_orders flag %s' % str(simple))
	# 		size += basic_size
	# 		result += [(basic_result,)]
	# 		return [size, result]
