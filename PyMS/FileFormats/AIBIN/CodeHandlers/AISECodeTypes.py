
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

	def decompile(self, scanner: BytesScanner, context: DecompileContext) -> int:
		bytecode_type: Struct.IntField = cast(Struct.IntField, self._bytecode_type)
		if isinstance(context, AIDecompileContext) and context.aise_context.expanded:
			bytecode_type = Struct.l_u32
		return scanner.scan(bytecode_type)

Point = tuple[int, int]
class PointCodeType(CodeType.CodeType[Point, Point]):
	LOCATION = 65535
	SCRIPT_AREA = 65534

	def __init__(self, name: str = 'point', help_text: str = 'A point, either `(x, y)`, `Loc.{location id}`, or `ScriptArea`') -> None:
		super().__init__(name, help_text, Struct.l_au16(2), False)

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

UnitGroup = int | tuple[int, ...]
class UnitGroupCodeType(CodeType.CodeType[UnitGroup, UnitGroup]):
	def __init__(self) -> None:
		self._unit_id_code_type = UnitIDCodeType()
		super().__init__('unit_group', "Same as unit_id, but allows multiple with '|'", Struct.l_u16, False)

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (CodeTypes.UnitCodeType, CodeTypes.BuildingCodeType, CodeTypes.MilitaryCodeType, CodeTypes.GGMilitaryCodeType, CodeTypes.AGMilitaryCodeType, CodeTypes.GAMilitaryCodeType, CodeTypes.AAMilitaryCodeType))

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
		if isinstance(groups, int):
			groups = (groups,)
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
		if isinstance(groups, int):
			groups = (groups,)
		tokens: list[str | None] = []
		if token is not None:
			tokens = UnitGroupCodeType.RE_OR.split(token)
		while len(tokens) < len(groups):
			tokens.append(None)
		for group, group_token in zip(groups, tokens):
			self._unit_id_code_type.validate(group, parse_context, group_token)

	def serialize(self, groups: UnitGroup, context: SerializeContext) -> str:
		if isinstance(groups, int):
			groups = (groups,)
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

	def compile(self, value: AISEIdleOrder.OptionSet, context: ByteCodeBuilderType) -> None:
		value.compile_options(context)

	def serialize(self, value: AISEIdleOrder.OptionSet, context: SerializeContext) -> str:
		return value.serialize_options()

	def parse(self, parse_context: ParseContext) -> AISEIdleOrder.OptionSet:
		return AISEIdleOrder.OptionSet.parse_options(parse_context)

class AttackModeCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		super().__init__('attack_mode', 'The state of whether AI is under attack, one of: Always, Default, Never', Struct.l_u8, [
			'Always',
			'Default',
			'Never'
		], True)

class AIControlCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		super().__init__('ai_control', 'TODO', Struct.l_u8, [
			'wait_request_resources',
			'dont_wait_request_resources',
			'build_gas',
			'dont_build_gas',
			'retaliation',
			'no_retaliation',
			'focus_disabled_units',
			'dont_focus_disabled_units',
			'global_enable_spell_focus',
			'global_disable_spell_focus',
			'global_enable_acid_spore_focus',
			'global_disable_acid_spore_focus',
			'global_enable_carrier_focus',
			'global_disable_carrier_focus',
		])

class SupplyCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		super().__init__('supply', 'One of: Provided, Used, Max or InUnits', Struct.l_u8, [
			'Provided',
			'Used',
			'Max',
			'InUnits',
		])

class RaceCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		super().__init__('race', 'One of: Zerg, Terran, Protoss, Any_Total or Any_Max', Struct.l_u8, {
			'Zerg': 0,
			'Terran': 1,
			'Protoss': 2,
			'Any_Total': 16,
			'Any_Max': 17,
		})

class TimeCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		super().__init__('time_type', 'One of: Frames or Minutes', Struct.l_u8, [
			'Frames',
			'Minutes'
		])

class ResourceCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		super().__init__('resource', 'One of: Ore, Gas, or Any', Struct.l_u8, [
			'Ore',
			'Gas',
			'Any'
		])

class LayoutActionCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		super().__init__('layout_action', 'One of: Set or Remove', Struct.l_u8, [
			'Set',
			'Remove'
		])

class BoolCompareCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		super().__init__('bool_compare', 'One of: False, True, False_Wait, True_Wait, False_Call or True_Call', Struct.l_u8, {
			'False': 0,
			'True': 1,
			'False_Wait': 64,
			'True_Wait': 65,
			'False_Call': 128,
			'True_Call': 129,
		})

class AvailabilityCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		super().__init__('availability', 'One of: Disabled, Enabled or Researched', Struct.l_u8, [
			'Disabled',
			'Enabled',
			'Researched'
		])

class RevealCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		super().__init__('reveal_type', 'One of: Reveal or RevealFog', Struct.l_u8, [
			'Reveal',
			'RevealFog'
		])

class QueueFlagCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		super().__init__('queue_flags', 'One of: Local or Global', Struct.l_u8, [
			'Local',
			'Global'
		])

class DefenseTypeCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		super().__init__('defense_type', 'One of: Use or Build', Struct.l_u8, [
			'Use',
			'Build'
		])

class DefenseDirectionCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		super().__init__('defense_direction', 'One of: Ground or Air', Struct.l_u8, [
			'Ground',
			'Air'
		])

class BuildAtPointCodeType(PointCodeType):
	TOWN_CENTER = 65500

	def __init__(self) -> None:
		super().__init__('build_at_point', 'A point, either `(x, y)`, `Loc.{location id}`, `ScriptArea` or `TownCenter`')

	def serialize(self, value: Point, context: SerializeContext) -> str:
		if value[0] == BuildAtPointCodeType.TOWN_CENTER:
			return 'TownCenter'
		return super().serialize(value, context)

	def _lex(self, parse_context: ParseContext) -> Point:
		token = parse_context.lexer.next_token(peek=True)
		if token.raw_value.lower() == 'towncenter':
			_ = parse_context.lexer.next_token()
			return (BuildAtPointCodeType.TOWN_CENTER, 0)
		return super()._lex(parse_context)

class BuildAtFlagsCodeType(CodeType.FlagsCodeType):
	def __init__(self) -> None:
		help_text = """Any of the following:
	AllowUnreachableRegions,
	NotSafe,
	AnyElevation,
	NearResourceBuildings,
	NearResources,
	DontSpreadOut,
	DontPreferUnpowered,
	IgnoreExtraSpace,
	PreferUnpowered,
	Remove"""
		super().__init__('build_at_flags', help_text, Struct.l_u32, {
			'AllowUnreachableRegions': 0x1,
			'NotSafe': 0x2,
			'AnyElevation': 0x8,
			'NearResourceBuildings': 0x10,
			'NearResources': 0x20,
			'DontSpreadOut': 0x100,
			'DontPreferUnpowered': 0x200,
			'IgnoreExtraSpace': 0x400,
			'PreferUnpowered': 0x02000000,
			'Remove': 0x80000000,
		})
