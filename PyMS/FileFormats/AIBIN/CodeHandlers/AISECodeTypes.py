
from .AIByteCodeCompiler import AIByteCodeCompiler
from .AIDecompileContext import AIDecompileContext
from . import CodeTypes

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

	def lex_token(self, parse_context: ParseContext) -> str:
		raw_token = ''
		token = parse_context.lexer.next_token()
		if token.raw_value == '(':
			raw_token += token.raw_value
			token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.IntegerToken):
				raise parse_context.error('Parse', f"Expected integer value in 'point' x value, but got '{token.raw_value}'")
			raw_token += token.raw_value
			token = parse_context.lexer.next_token()
			if not token.raw_value == ',':
				raise parse_context.error('Parse', f"Expected comma between 'point' x and y values, but got '{token.raw_value}'")
			raw_token += token.raw_value
			token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.IntegerToken):
				raise parse_context.error('Parse', f"Expected integer value in 'point' y value, but got '{token.raw_value}'")
			raw_token += token.raw_value
			token = parse_context.lexer.next_token()
			if not token.raw_value == ')':
				raise parse_context.error('Parse', f"Expected ')' to end 'point`, but got '{token.raw_value}'")
			raw_token += token.raw_value
		elif token.raw_value == 'Loc':
			raw_token += token.raw_value
			token = parse_context.lexer.next_token()
			if not token.raw_value == '.':
				raise parse_context.error('Parse', f"Expected '.' after 'Loc' for 'point`, but got '{token.raw_value}'")
			raw_token += token.raw_value
			token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.IntegerToken):
				raise parse_context.error('Parse', f"Expected integer value for 'point' location id, but got '{token.raw_value}'")
			raw_token += token.raw_value
		elif token.raw_value == 'ScriptArea':
			raw_token = token.raw_value
		else:
			raise parse_context.error('Parse', f"Expected a 'point' value but got '{token.raw_value}'")
		return raw_token

	RE_COORDS = re.compile(r'\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*')
	RE_LOCATION = re.compile(r'\s*Loc\.(\d+)\s*')
	def parse_token(self, token: str, parse_context: ParseContext) -> Point:
		if token == 'ScriptArea':
			return (PointCodeType.SCRIPT_AREA, 0)
		if match := PointCodeType.RE_COORDS.match(token):
			return (int(match.group(1)), int(match.group(2)))
		if match := PointCodeType.RE_LOCATION.match(token):
			return (PointCodeType.LOCATION, int(match.group(1)))
		raise PyMSError('Parse', "Invalid value '%s' for '%s'" % (token, self.name))

	def validate(self, value: Point, parse_context: ParseContext, token: str | None = None) -> None:
		# TODO: Do we need to validate any other cases?
		if value[0] == PointCodeType.LOCATION and value[1] > 255:
			raise PyMSError('Parse', f"Location id '{value[1]}' is not valid (must be a number from 0 to 255)")

class OrderCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		super().__init__('order', 'An order ID from 0 to 188, or a [hardcoded] order name', Struct.l_u8, [
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
		])

class UnitIDCodeType(CodeTypes.UnitCodeType, CodeType.HasKeywords):
	def __init__(self, name: str = 'unit_id', help_text: str = 'Same as unit type, but also accepts: 228/None, 229/Any, 230/Group_Men, 231/Group_Buildings, 232/Group_Factories') -> None:
		super().__init__(name, help_text)

	def lex_token(self, parse_context: ParseContext) -> str:
		rollback = parse_context.lexer.get_rollback()
		token = parse_context.lexer.next_token()
		if isinstance(token, Tokens.IdentifierToken):
			value = token.raw_value.lower()
			if value in ('none', 'any', 'group_men', 'group_buildings', 'group_factories'):
				return value
		parse_context.lexer.rollback(rollback)
		return super().lex_token(parse_context)

	def parse_token(self, token: str, parse_context: ParseContext) -> int:
		group = token.lower()
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
		return super().parse_token(token, parse_context)

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

class UnitGroupCodeType(CodeType.CodeType[tuple[int, ...], tuple[int, ...]]):
	def __init__(self) -> None:
		self._unit_id_code_type = UnitIDCodeType()
		super().__init__('unit_group', "Same as unit_id, but allows multiple with '|'", Struct.l_u16, False)

	def decompile(self, scanner: BytesScanner, context: DecompileContext) -> tuple[int, ...]:
		value = scanner.scan(Struct.l_u16)
		if value < 0xFF00:
			return (value,)
		count = value & 0xFF
		groups: list[int] = []
		for _ in range(count):
			groups.append(scanner.scan(Struct.l_u16))
		return tuple(groups)

	def compile(self, groups: tuple[int, ...], context: ByteCodeBuilderType) -> None:
		count = len(groups)
		if count > 1:
			assert count <= 0xFF
			context.add_data(Struct.l_u16.pack(0xFF00 | count))
		for group in groups:
			context.add_data(Struct.l_u16.pack(group))

	def lex_token(self, parse_context: ParseContext) -> str:
		groups: list[str] = []
		while True:
			groups.append(self._unit_id_code_type.lex_token(parse_context))
			token = parse_context.lexer.next_token(peek=True)
			if token.raw_value == '|':
				_ = parse_context.lexer.next_token()
			else:
				break
		return ' | '.join(groups)

	RE_OR = re.compile(r'\s*\|\s*')
	def parse_token(self, token: str, parse_context: ParseContext) -> tuple[int, ...]:
		return tuple(self._unit_id_code_type.parse_token(raw_group, parse_context) for raw_group in UnitGroupCodeType.RE_OR.split(token))

	def validate(self, groups: tuple[int, ...], parse_context: ParseContext, token: str | None = None):
		tokens: list[str | None] = []
		if token is not None:
			tokens = UnitGroupCodeType.RE_OR.split(token)
		while len(tokens) < len(groups):
			tokens.append(None)
		for group, group_token in zip(groups, tokens):
			self._unit_id_code_type.validate(group, parse_context, group_token)

	def serialize(self, groups: tuple[int, ...], context: SerializeContext) -> str:
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

	def lex_token(self, parse_context: ParseContext) -> str:
		raw_token = self._point_code_type.lex_token(parse_context)
		token = parse_context.lexer.next_token(peek=True)
		if token.raw_value == '~':
			_ = parse_context.lexer.next_token()
			token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.IntegerToken):
				raise parse_context.error('Parse', f"Expected integer value for 'area' radius value, but got '{token.raw_value}'")
			raw_token += f' ~ {token.raw_value}'
		return raw_token

	RE_TILDE = re.compile(r'\s*\~\s*')
	def parse_token(self, token: str, parse_context: ParseContext) -> Area:
		tokens = AreaCodeType.RE_TILDE.split(token, 1)
		point = self._point_code_type.parse_token(tokens[0], parse_context)
		radius = 0
		if len(tokens) > 1:
			try:
				radius = int(tokens[1])
			except:
				raise PyMSError('Parse', f"Invalid integer value for 'area' radius value, got '{tokens[1]}'")
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
