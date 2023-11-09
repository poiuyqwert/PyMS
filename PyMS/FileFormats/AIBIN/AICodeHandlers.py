
from __future__ import annotations

from .AIFlag import AIFlag

from ...Utilities.CodeHandlers import CodeType
from ...Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ...Utilities.CodeHandlers.ByteCodeHandler import ByteCodeHandler
from ...Utilities.CodeHandlers.SerializeContext import SerializeContext, Formatters
from ...Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler
from ...Utilities.CodeHandlers.ParseContext import ParseContext, BlockReferenceResolver
from ...Utilities.CodeHandlers.Lexer import Lexer
from ...Utilities.CodeHandlers import Tokens
from ...Utilities.CodeHandlers.SourceCodeHandler import SourceCodeHandler
from ...Utilities.CodeHandlers.CodeBlock import CodeBlock
from ...Utilities import Struct
from ...Utilities.PyMSError import PyMSError

import re

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from .DataContext import DataContext

class AISerializeContext(SerializeContext):
	def __init__(self, definitions: DefinitionsHandler, formatters: Formatters, data_context: DataContext) -> None:
		SerializeContext.__init__(self, definitions, formatters)
		self.data_context = data_context

class AIParseContext(ParseContext):
	def __init__(self, definitions: DefinitionsHandler, data_context: DataContext) -> None:
		ParseContext.__init__(self, definitions)
		self.data_context = data_context

class ByteCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		CodeType.IntCodeType.__init__(self, 'byte', Struct.l_u8)

class WordCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		CodeType.IntCodeType.__init__(self, 'word', Struct.l_u16)

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (WordCodeType, ByteCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match type(other_type):
			case WordCodeType():
				return 2
			case ByteCodeType():
				return 1
			case _:
				return 0

class DWordCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		CodeType.IntCodeType.__init__(self, 'dword', Struct.l_u32)

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (DWordCodeType, WordCodeType, ByteCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match other_type:
			case DWordCodeType():
				return 3
			case WordCodeType():
				return 2
			case ByteCodeType():
				return 1
			case _:
				return 0

class BlockCodeType(CodeType.AddressCodeType):
	def __init__(self) -> None:
		CodeType.AddressCodeType.__init__(self, 'block', Struct.l_u16)

class UnitCodeType(CodeType.IntCodeType):
	def __init__(self, name: str = 'unit') -> None:
		# TODO: Expanded DAT
		CodeType.IntCodeType.__init__(self, name, bytecode_type=Struct.l_u16, limits=(0, 227))

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (UnitCodeType, BuildingCodeType, MilitaryCodeType, GGMilitaryCodeType, AGMilitaryCodeType, GAMilitaryCodeType, AAMilitaryCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		return isinstance(other_type, UnitCodeType)

	def serialize(self, value: int, context: SerializeContext) -> str:
		if context.definitions:
			variable = context.definitions.lookup_variable(value, self)
			if variable:
				return variable.name
		if isinstance(context, AISerializeContext) and context.data_context:
			name = context.data_context.unit_name(value)
			if name:
				return StringCodeType.serialize_string(name)
		return str(value)

class BuildingCodeType(UnitCodeType):
	def __init__(self) -> None:
		UnitCodeType.__init__(self, 'building')
	# TODO: Custom

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(self, BuildingCodeType)

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match other_type:
			case BuildingCodeType():
				return 2
			case UnitCodeType():
				return 1
			case _:
				return 0

class MilitaryCodeType(UnitCodeType):
	def __init__(self, name: str = 'military') -> None:
		UnitCodeType.__init__(self, name)
	# TODO: Custom

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (MilitaryCodeType, GGMilitaryCodeType, AGMilitaryCodeType, GAMilitaryCodeType, AAMilitaryCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match other_type:
			case MilitaryCodeType():
				return 2
			case UnitCodeType():
				return 1
			case _:
				return 0

class GGMilitaryCodeType(MilitaryCodeType):
	def __init__(self) -> None:
		MilitaryCodeType.__init__(self, 'gg_military')
	# TODO: Custom

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (GGMilitaryCodeType, GAMilitaryCodeType, MilitaryCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match other_type:
			case GGMilitaryCodeType():
				return 4
			case GAMilitaryCodeType():
				return 3
			case MilitaryCodeType():
				return 2
			case UnitCodeType():
				return 1
			case _:
				return 0

class GAMilitaryCodeType(MilitaryCodeType):
	def __init__(self) -> None:
		MilitaryCodeType.__init__(self, 'ga_military')
	# TODO: Custom

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (GAMilitaryCodeType, GGMilitaryCodeType, MilitaryCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match other_type:
			case GAMilitaryCodeType():
				return 4
			case GGMilitaryCodeType():
				return 3
			case MilitaryCodeType():
				return 2
			case UnitCodeType():
				return 1
			case _:
				return 0

class AGMilitaryCodeType(MilitaryCodeType):
	def __init__(self) -> None:
		MilitaryCodeType.__init__(self, 'ag_military')
	# TODO: Custom

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (AGMilitaryCodeType, AAMilitaryCodeType, MilitaryCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match other_type:
			case AGMilitaryCodeType():
				return 4
			case AAMilitaryCodeType():
				return 3
			case MilitaryCodeType():
				return 2
			case UnitCodeType():
				return 1
			case _:
				return 0

class AAMilitaryCodeType(MilitaryCodeType):
	def __init__(self) -> None:
		MilitaryCodeType.__init__(self, 'aa_military')
	# TODO: Custom

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (AAMilitaryCodeType, AGMilitaryCodeType, MilitaryCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match other_type:
			case AAMilitaryCodeType():
				return 4
			case AGMilitaryCodeType():
				return 3
			case MilitaryCodeType():
				return 2
			case UnitCodeType():
				return 1
			case _:
				return 0

class UpgradeCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		# TODO: Expanded DAT
		CodeType.IntCodeType.__init__(self, 'upgrade', Struct.l_u16, limits=(0, 60))
	# TODO: Custom

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, UpgradeCodeType)

	def compatible(self, other_type: CodeType.CodeType) -> int:
		return isinstance(other_type, UpgradeCodeType)

class TechnologyCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		# TODO: Expanded DAT
		CodeType.IntCodeType.__init__(self, 'technology', Struct.l_u16, limits=(0, 43))
	# TODO: Custom

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, TechnologyCodeType)

	def compatible(self, other_type: CodeType.CodeType) -> int:
		return isinstance(other_type, TechnologyCodeType)

class StringCodeType(CodeType.StrCodeType):
	def __init__(self) -> None:
		CodeType.StrCodeType.__init__(self, 'string')

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, StringCodeType)

	def compatible(self, other_type: CodeType.CodeType) -> int:
		return isinstance(other_type, StringCodeType)

class CompareCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		cases = {
			'GreaterThan': 1,
			'LessThan': 0
		}
		CodeType.EnumCodeType.__init__(self, 'compare', Struct.l_u8, cases)

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, CompareCodeType)

	def compatible(self, other_type: CodeType.CodeType) -> int:
		return isinstance(other_type, CompareCodeType)

Goto = CodeCommandDefinition('goto', 0, (BlockCodeType(),), ends_flow=True)
NoTownsJump = CodeCommandDefinition('notowns_jump', 1, (UnitCodeType(), BlockCodeType(),))
Wait = CodeCommandDefinition('wait', 2, (WordCodeType(),), separate=True)
StartTown = CodeCommandDefinition('start_town', 3)
StartAreaTown = CodeCommandDefinition('start_areatown', 4)
Expand = CodeCommandDefinition('expand', 5, (ByteCodeType(), BlockCodeType(),))
Build = CodeCommandDefinition('build', 6, (ByteCodeType(), BuildingCodeType(), ByteCodeType(),))
Upgrade = CodeCommandDefinition('upgrade', 7, (ByteCodeType(), UpgradeCodeType(), ByteCodeType(),))
Tech = CodeCommandDefinition('tech', 8, (TechnologyCodeType(), ByteCodeType(),))
WaitBuild = CodeCommandDefinition('wait_build', 9, (ByteCodeType(), BuildingCodeType(),))
WaitBuildStart = CodeCommandDefinition('wait_buildstart', 10, (ByteCodeType(), UnitCodeType(),))
AttackClear = CodeCommandDefinition('attack_clear', 11)
AttackAdd = CodeCommandDefinition('attack_add', 12, (ByteCodeType(), MilitaryCodeType(),))	
AttackPrepare = CodeCommandDefinition('attack_prepare', 13)
AttackDo = CodeCommandDefinition('attack_do', 14)
WaitSecure = CodeCommandDefinition('wait_secure', 15)
CaptExpand = CodeCommandDefinition('capt_expand', 16)
BuildBunkers = CodeCommandDefinition('build_bunkers', 17)
WaitBunkers = CodeCommandDefinition('wait_bunkers', 18)
DefenseBuildGG = CodeCommandDefinition('defensebuild_gg', 19, (ByteCodeType(), GGMilitaryCodeType(),))
DefenseBuildAG = CodeCommandDefinition('defensebuild_ag', 20, (ByteCodeType(), AGMilitaryCodeType(),))
DefenseBuildGA = CodeCommandDefinition('defensebuild_ga', 21, (ByteCodeType(), GAMilitaryCodeType(),))
DefenseBuildAA = CodeCommandDefinition('defensebuild_aa', 22, (ByteCodeType(), AAMilitaryCodeType(),))
DefenseUseGG = CodeCommandDefinition('defenseuse_gg', 23, (ByteCodeType(), GGMilitaryCodeType(),))
DefenseUseAG = CodeCommandDefinition('defenseuse_ag', 24, (ByteCodeType(), AGMilitaryCodeType(),))
DefenseUseGA = CodeCommandDefinition('defenseuse_ga', 25, (ByteCodeType(), GAMilitaryCodeType(),))
DefenseUseAA = CodeCommandDefinition('defenseuse_aa', 26, (ByteCodeType(), AAMilitaryCodeType(),))
DefenseClearGG = CodeCommandDefinition('defenseclear_gg', 27)
DefenseClearAG = CodeCommandDefinition('defenseclear_ag', 28)
DefenseClearGA = CodeCommandDefinition('defenseclear_ga', 29)
DefenseClearAA = CodeCommandDefinition('defenseclear_aa', 30)
SendSuicide = CodeCommandDefinition('send_suicide', 31, (ByteCodeType(),))
PlayerEnemy = CodeCommandDefinition('player_enemy', 32)
PlayerAlly = CodeCommandDefinition('player_ally', 33)
DefaultMin = CodeCommandDefinition('default_min', 34, (ByteCodeType(),))
DefaultBuildOff = CodeCommandDefinition('defaultbuild_off', 35)
Stop = CodeCommandDefinition('stop', 36, ends_flow=True)
SwitchRescue = CodeCommandDefinition('switch_rescue', 37)
MoveDT = CodeCommandDefinition('move_dt', 38)
Debug = CodeCommandDefinition('debug', 39, (BlockCodeType(),StringCodeType(),), ends_flow=True)
FatalError = CodeCommandDefinition('fatal_error', 40)
EnterBunker = CodeCommandDefinition('enter_bunker', 41)
ValueArea = CodeCommandDefinition('value_area', 42)
TransportsOff = CodeCommandDefinition('transports_off', 43)
CheckTransports = CodeCommandDefinition('check_transports', 44)
NukeRate = CodeCommandDefinition('nuke_rate', 45, (ByteCodeType(),))
MaxForce = CodeCommandDefinition('max_force', 46, (WordCodeType(),))
ClearCombatData = CodeCommandDefinition('clear_combatdata', 47)
RandomJump = CodeCommandDefinition('random_jump', 48, (ByteCodeType(), BlockCodeType(),))
TimeJump = CodeCommandDefinition('time_jump', 49, (ByteCodeType(), BlockCodeType(),))
FarmsNoTiming = CodeCommandDefinition('farms_notiming', 50)
FarmsTiming = CodeCommandDefinition('farms_timing', 51)
BuildTurrets = CodeCommandDefinition('build_turrets', 52)
WaitTurrets = CodeCommandDefinition('wait_turrets', 53)
DefaultBuild = CodeCommandDefinition('default_build', 54)
HarassFactor = CodeCommandDefinition('harass_factor', 55, (WordCodeType(),))
StartCampaign = CodeCommandDefinition('start_campaign', 56)
RaceJump = CodeCommandDefinition('race_jump', 57, (BlockCodeType(), BlockCodeType(), BlockCodeType(),), ends_flow=True)
RegionSize = CodeCommandDefinition('region_size', 58, (ByteCodeType(), BlockCodeType(),))
GetOldPeons = CodeCommandDefinition('get_oldpeons', 59, (ByteCodeType(),))
GroundMapJump = CodeCommandDefinition('groundmap_jump', 60, (BlockCodeType(),))
PlaceGuard = CodeCommandDefinition('place_guard', 61, (UnitCodeType(), ByteCodeType(),))
WaitForce = CodeCommandDefinition('wait_force', 62, (ByteCodeType(), MilitaryCodeType(),))
GuardResources = CodeCommandDefinition('guard_resources', 63, (MilitaryCodeType(),))
Call = CodeCommandDefinition('call', 64, (BlockCodeType(),))
Return = CodeCommandDefinition('return', 65, ends_flow=True)
EvalHarass = CodeCommandDefinition('eval_harass', 66, (BlockCodeType(),))
Creep = CodeCommandDefinition('creep', 67, (ByteCodeType(),))
Panic = CodeCommandDefinition('panic', 68, (BlockCodeType(),))
PlayerNeed = CodeCommandDefinition('player_need', 69, (ByteCodeType(),BuildingCodeType(),))
DoMorph = CodeCommandDefinition('do_morph', 70, (ByteCodeType(), MilitaryCodeType(),))
WaitUpgrades = CodeCommandDefinition('wait_upgrades', 71)
MultiRun = CodeCommandDefinition('multirun', 72, (BlockCodeType(),), separate=True)
Rush = CodeCommandDefinition('rush', 73, (ByteCodeType(), BlockCodeType(),))
ScoutWith = CodeCommandDefinition('scout_with', 74, (MilitaryCodeType(),))
DefineMax = CodeCommandDefinition('define_max', 75, (ByteCodeType(), UnitCodeType(),))
Train = CodeCommandDefinition('train', 76, (ByteCodeType(), MilitaryCodeType(),))
TargetExpansion = CodeCommandDefinition('target_expansion', 77)
WaitTrain = CodeCommandDefinition('wait_train', 78, (ByteCodeType(), UnitCodeType(),))
SetAttacks = CodeCommandDefinition('set_attacks', 79, (ByteCodeType(),))
SetGenCMD = CodeCommandDefinition('set_gencmd', 80)
MakePatrol = CodeCommandDefinition('make_patrol', 81)
GiveMoney = CodeCommandDefinition('give_money', 82)
PrepDown = CodeCommandDefinition('prep_down', 83, (ByteCodeType(), ByteCodeType(), MilitaryCodeType(),))
ResourcesJump = CodeCommandDefinition('resources_jump', 84, (WordCodeType(), WordCodeType(), BlockCodeType(),))
EnterTransport = CodeCommandDefinition('enter_transport', 85)
ExitTransport = CodeCommandDefinition('exit_transport', 86)
SharedVisionOn = CodeCommandDefinition('sharedvision_on', 87, (ByteCodeType(),))
SharedVisionOff = CodeCommandDefinition('sharedvision_off', 88, (ByteCodeType(),))
NukeLocation = CodeCommandDefinition('nuke_location', 89)
HarassLocation = CodeCommandDefinition('harass_location', 90)
Implode = CodeCommandDefinition('implode', 91)
GuardAll = CodeCommandDefinition('guard_all', 92)
EnemyownsJump = CodeCommandDefinition('enemyowns_jump', 93, (UnitCodeType(), BlockCodeType(),))
EnemyResourcesJump = CodeCommandDefinition('enemyresources_jump', 94, (WordCodeType(), WordCodeType(), BlockCodeType(),))
IfDif = CodeCommandDefinition('if_dif', 95, (CompareCodeType(), ByteCodeType(), BlockCodeType(),))
EasyAttack = CodeCommandDefinition('easy_attack', 96, (ByteCodeType(), MilitaryCodeType(),))
KillThread = CodeCommandDefinition('kill_thread', 97, ends_flow=True)
Killable = CodeCommandDefinition('killable', 98)
WaitFinishAttack = CodeCommandDefinition('wait_finishattack', 99)
QuickAttack = CodeCommandDefinition('quick_attack', 100)
JunkyardDog = CodeCommandDefinition('junkyard_dog', 101)
FakeNuke = CodeCommandDefinition('fake_nuke', 102)
DisruptionWeb = CodeCommandDefinition('disruption_web', 103)
RecallLocation = CodeCommandDefinition('recall_location', 104)
SetRandomSeed = CodeCommandDefinition('set_randomseed', 105, (DWordCodeType(),))
IfOwned = CodeCommandDefinition('if_owned', 106, (UnitCodeType(),BlockCodeType(),))
CreateNuke = CodeCommandDefinition('create_nuke', 107)
CreateUnit = CodeCommandDefinition('create_unit', 108, (UnitCodeType(), WordCodeType(), WordCodeType(),))
NukePos = CodeCommandDefinition('nuke_pos', 109, (WordCodeType(), WordCodeType(),))
HelpIfTrouble = CodeCommandDefinition('help_iftrouble', 110)
AlliesWatch = CodeCommandDefinition('allies_watch', 111, (ByteCodeType(), BlockCodeType(),))
TryTownPoint = CodeCommandDefinition('try_townpoint', 112, (ByteCodeType(), BlockCodeType(),))
IfTowns = CodeCommandDefinition('if_towns', 113)

class AIByteCodeHandler(ByteCodeHandler):
	def __init__(self, data: bytes) -> None:
		ByteCodeHandler.__init__(self, data)
		self.register_command(Goto)
		self.register_command(NoTownsJump)
		self.register_command(Wait)
		self.register_command(StartTown)
		self.register_command(StartAreaTown)
		self.register_command(Expand)
		self.register_command(Build)
		self.register_command(Upgrade)
		self.register_command(Tech)
		self.register_command(WaitBuild)
		self.register_command(WaitBuildStart)
		self.register_command(AttackClear)
		self.register_command(AttackAdd)
		self.register_command(AttackPrepare)
		self.register_command(AttackDo)
		self.register_command(WaitSecure)
		self.register_command(CaptExpand)
		self.register_command(BuildBunkers)
		self.register_command(WaitBunkers)
		self.register_command(DefenseBuildGG)
		self.register_command(DefenseBuildAG)
		self.register_command(DefenseBuildGA)
		self.register_command(DefenseBuildAA)
		self.register_command(DefenseUseGG)
		self.register_command(DefenseUseAG)
		self.register_command(DefenseUseGA)
		self.register_command(DefenseUseAA)
		self.register_command(DefenseClearGG)
		self.register_command(DefenseClearAG)
		self.register_command(DefenseClearGA)
		self.register_command(DefenseClearAA)
		self.register_command(SendSuicide)
		self.register_command(PlayerEnemy)
		self.register_command(PlayerAlly)
		self.register_command(DefaultMin)
		self.register_command(DefaultBuildOff)
		self.register_command(Stop)
		self.register_command(SwitchRescue)
		self.register_command(MoveDT)
		self.register_command(Debug)
		self.register_command(FatalError)
		self.register_command(EnterBunker)
		self.register_command(ValueArea)
		self.register_command(TransportsOff)
		self.register_command(CheckTransports)
		self.register_command(NukeRate)
		self.register_command(MaxForce)
		self.register_command(ClearCombatData)
		self.register_command(RandomJump)
		self.register_command(TimeJump)
		self.register_command(FarmsNoTiming)
		self.register_command(FarmsTiming)
		self.register_command(BuildTurrets)
		self.register_command(WaitTurrets)
		self.register_command(DefaultBuild)
		self.register_command(HarassFactor)
		self.register_command(StartCampaign)
		self.register_command(RaceJump)
		self.register_command(RegionSize)
		self.register_command(GetOldPeons)
		self.register_command(GroundMapJump)
		self.register_command(PlaceGuard)
		self.register_command(WaitForce)
		self.register_command(GuardResources)
		self.register_command(Call)
		self.register_command(Return)
		self.register_command(EvalHarass)
		self.register_command(Creep)
		self.register_command(Panic)
		self.register_command(PlayerNeed)
		self.register_command(DoMorph)
		self.register_command(WaitUpgrades)
		self.register_command(MultiRun)
		self.register_command(Rush)
		self.register_command(ScoutWith)
		self.register_command(DefineMax)
		self.register_command(Train)
		self.register_command(TargetExpansion)
		self.register_command(WaitTrain)
		self.register_command(SetAttacks)
		self.register_command(SetGenCMD)
		self.register_command(MakePatrol)
		self.register_command(GiveMoney)
		self.register_command(PrepDown)
		self.register_command(ResourcesJump)
		self.register_command(EnterTransport)
		self.register_command(ExitTransport)
		self.register_command(SharedVisionOn)
		self.register_command(SharedVisionOff)
		self.register_command(NukeLocation)
		self.register_command(HarassLocation)
		self.register_command(Implode)
		self.register_command(GuardAll)
		self.register_command(EnemyownsJump)
		self.register_command(EnemyResourcesJump)
		self.register_command(IfDif)
		self.register_command(EasyAttack)
		self.register_command(KillThread)
		self.register_command(Killable)
		self.register_command(WaitFinishAttack)
		self.register_command(QuickAttack)
		self.register_command(JunkyardDog)
		self.register_command(FakeNuke)
		self.register_command(DisruptionWeb)
		self.register_command(RecallLocation)
		self.register_command(SetRandomSeed)
		self.register_command(IfOwned)
		self.register_command(CreateNuke)
		self.register_command(CreateUnit)
		self.register_command(NukePos)
		self.register_command(HelpIfTrouble)
		self.register_command(AlliesWatch)
		self.register_command(TryTownPoint)
		self.register_command(IfTowns)

class AILexer(Lexer):
	class SymbolToken(Tokens.LiteralsToken):
		_literals = (':', '=', '@', '(', ')', ',', '{', '}', '--')

	class ScriptIDToken(Tokens.RegexToken):
		_regexp = re.compile(r'\S{4}')

	def __init__(self, code: str) -> None:
		Lexer.__init__(self, code)
		self.register_token_type(Tokens.WhitespaceToken, skip=True)
		self.register_token_type(Tokens.CommentToken, skip=True)
		self.register_token_type(AILexer.SymbolToken)
		self.register_token_type(Tokens.IntegerToken)
		self.register_token_type(Tokens.BooleanToken)
		self.register_token_type(Tokens.IdentifierToken)
		self.register_token_type(Tokens.StringToken)
		self.register_token_type(Tokens.NewlineToken)

class TBLStringCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		CodeType.IntCodeType.__init__(self, 'tbl_string', Struct.l_u32)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if not isinstance(context, AISerializeContext):
			return None
		return context.data_context.stattxt_string(value - 1)

class BinFileCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		cases = {
			'aiscript': 0,
			'bwscript': 1
		}
		CodeType.EnumCodeType.__init__(self, 'bin_file', Struct.l_u8, cases) # TODO: bytecode_type

class BoolCodeType(CodeType.BooleanCodeType):
	def __init__(self) -> None:
		CodeType.BooleanCodeType.__init__(self, 'bool', Struct.l_u8) # TODO: bytecode_type

HeaderNameString = CodeCommandDefinition('name_string', None, (TBLStringCodeType(),), ephemeral=True)
HeaderBinFile = CodeCommandDefinition('bin_file', None, (BinFileCodeType(),), ephemeral=True)
BroodwarOnly = CodeCommandDefinition('broodwar_only', None, (BoolCodeType(),), ephemeral=True)
StarEditHidden = CodeCommandDefinition('staredit_hidden', None, (BoolCodeType(),), ephemeral=True)
RequiresLocation = CodeCommandDefinition('requires_location', None, (BoolCodeType(),), ephemeral=True)
EntryPoint = CodeCommandDefinition('entry_point', None, (BlockCodeType(),), ephemeral=True)

class AIHeaderEntryPointBlockReferenceResolver(BlockReferenceResolver):
	def __init__(self, header: AIHeaderSourceCodeHandler.AIScriptHeader, source_line: int | None) -> None:
		BlockReferenceResolver.__init__(self, source_line)
		self.header = header

	def block_defined(self, block):
		self.header.entry_point = block

class AIHeaderSourceCodeHandler(SourceCodeHandler):
	class AIScriptHeader(object):
		def __init__(self) -> None:
			self.string_id: int | None = None
			self.bwscript: bool | None = None
			self.broodwar_only: bool | None = None
			self.staredit_hidden: bool | None = None
			self.requires_location: bool | None = None
			self.entry_point_name: str | None = None
			self.entry_point: CodeBlock | None = None
		
		@property
		def flags(self) -> int:
			return (AIFlag.requires_location if self.requires_location else 0) | (AIFlag.staredit_hidden if self.staredit_hidden else 0) | (AIFlag.broodwar_only if self.broodwar_only else 0)

	def __init__(self, lexer: AILexer) -> None:
		SourceCodeHandler.__init__(self, lexer)
		self.register_command(HeaderNameString)
		self.register_command(HeaderBinFile)
		self.register_command(BroodwarOnly)
		self.register_command(StarEditHidden)
		self.register_command(RequiresLocation)
		self.register_command(EntryPoint)
		self.script_header: AIHeaderSourceCodeHandler.AIScriptHeader | None = None

	def parse(self, parse_context: ParseContext) -> None:
		script_header = AIHeaderSourceCodeHandler.AIScriptHeader()
		token = self.lexer.next_token()
		if not isinstance(token, AILexer.SymbolToken) or token.raw_value != '{':
			raise PyMSError('Parse', "Expected a '{' to start the script header, got '%s' instead" % token.raw_value, line=self.lexer.line)
		token = self.lexer.next_token()
		if not isinstance(token, Tokens.NewlineToken):
			raise PyMSError('Parse', "Unexpected token '%s' (expected end of line)" % token.raw_value, line=self.lexer.line)
		while True:
			token = self.lexer.next_token()
			line = self.lexer.line
			if isinstance(token, AILexer.SymbolToken) and token.raw_value == '}':
				break
			if not isinstance(token, Tokens.IdentifierToken):
				raise PyMSError('Parse', "Expected a script header command, got '%s' instead" % token.raw_value, line=self.lexer.line)
			command = self.parse_command(token, parse_context)
			if command.definition == HeaderNameString:
				# TODO: Overwrite warning
				script_header.string_id = command.params[0]
			elif command.definition == HeaderBinFile:
				# TODO: Overwrite warning
				script_header.bwscript = bool(command.params[0])
			elif command.definition == BroodwarOnly:
				# TODO: Overwrite warning
				script_header.broodwar_only = command.params[0]
			elif command.definition == StarEditHidden:
				# TODO: Overwrite warning
				script_header.staredit_hidden = command.params[0]
			elif command.definition == RequiresLocation:
				# TODO: Overwrite warning
				script_header.requires_location = command.params[0]
			elif command.definition == EntryPoint:
				# TODO: Overwrite warning
				entry_point_name: str = command.params[0]
				script_header.entry_point_name = entry_point_name
				if entry_point := parse_context.lookup_block(entry_point_name):
					script_header.entry_point = entry_point
				else:
					parse_context.missing_block(entry_point_name, AIHeaderEntryPointBlockReferenceResolver(script_header, line))
		self.script_header = script_header

class AISourceCodeHandler(SourceCodeHandler):
	def __init__(self, lexer: AILexer) -> None:
		SourceCodeHandler.__init__(self, lexer)
		self.script_headers: dict[str, tuple[AIHeaderSourceCodeHandler.AIScriptHeader, int]] = {}
		self.register_command(Goto)
		self.register_command(NoTownsJump)
		self.register_command(Wait)
		self.register_command(StartTown)
		self.register_command(StartAreaTown)
		self.register_command(Expand)
		self.register_command(Build)
		self.register_command(Upgrade)
		self.register_command(Tech)
		self.register_command(WaitBuild)
		self.register_command(WaitBuildStart)
		self.register_command(AttackClear)
		self.register_command(AttackAdd)
		self.register_command(AttackPrepare)
		self.register_command(AttackDo)
		self.register_command(WaitSecure)
		self.register_command(CaptExpand)
		self.register_command(BuildBunkers)
		self.register_command(WaitBunkers)
		self.register_command(DefenseBuildGG)
		self.register_command(DefenseBuildAG)
		self.register_command(DefenseBuildGA)
		self.register_command(DefenseBuildAA)
		self.register_command(DefenseUseGG)
		self.register_command(DefenseUseAG)
		self.register_command(DefenseUseGA)
		self.register_command(DefenseUseAA)
		self.register_command(DefenseClearGG)
		self.register_command(DefenseClearAG)
		self.register_command(DefenseClearGA)
		self.register_command(DefenseClearAA)
		self.register_command(SendSuicide)
		self.register_command(PlayerEnemy)
		self.register_command(PlayerAlly)
		self.register_command(DefaultMin)
		self.register_command(DefaultBuildOff)
		self.register_command(Stop)
		self.register_command(SwitchRescue)
		self.register_command(MoveDT)
		self.register_command(Debug)
		self.register_command(FatalError)
		self.register_command(EnterBunker)
		self.register_command(ValueArea)
		self.register_command(TransportsOff)
		self.register_command(CheckTransports)
		self.register_command(NukeRate)
		self.register_command(MaxForce)
		self.register_command(ClearCombatData)
		self.register_command(RandomJump)
		self.register_command(TimeJump)
		self.register_command(FarmsNoTiming)
		self.register_command(FarmsTiming)
		self.register_command(BuildTurrets)
		self.register_command(WaitTurrets)
		self.register_command(DefaultBuild)
		self.register_command(HarassFactor)
		self.register_command(StartCampaign)
		self.register_command(RaceJump)
		self.register_command(RegionSize)
		self.register_command(GetOldPeons)
		self.register_command(GroundMapJump)
		self.register_command(PlaceGuard)
		self.register_command(WaitForce)
		self.register_command(GuardResources)
		self.register_command(Call)
		self.register_command(Return)
		self.register_command(EvalHarass)
		self.register_command(Creep)
		self.register_command(Panic)
		self.register_command(PlayerNeed)
		self.register_command(DoMorph)
		self.register_command(WaitUpgrades)
		self.register_command(MultiRun)
		self.register_command(Rush)
		self.register_command(ScoutWith)
		self.register_command(DefineMax)
		self.register_command(Train)
		self.register_command(TargetExpansion)
		self.register_command(WaitTrain)
		self.register_command(SetAttacks)
		self.register_command(SetGenCMD)
		self.register_command(MakePatrol)
		self.register_command(GiveMoney)
		self.register_command(PrepDown)
		self.register_command(ResourcesJump)
		self.register_command(EnterTransport)
		self.register_command(ExitTransport)
		self.register_command(SharedVisionOn)
		self.register_command(SharedVisionOff)
		self.register_command(NukeLocation)
		self.register_command(HarassLocation)
		self.register_command(Implode)
		self.register_command(GuardAll)
		self.register_command(EnemyownsJump)
		self.register_command(EnemyResourcesJump)
		self.register_command(IfDif)
		self.register_command(EasyAttack)
		self.register_command(KillThread)
		self.register_command(Killable)
		self.register_command(WaitFinishAttack)
		self.register_command(QuickAttack)
		self.register_command(JunkyardDog)
		self.register_command(FakeNuke)
		self.register_command(DisruptionWeb)
		self.register_command(RecallLocation)
		self.register_command(SetRandomSeed)
		self.register_command(IfOwned)
		self.register_command(CreateNuke)
		self.register_command(CreateUnit)
		self.register_command(NukePos)
		self.register_command(HelpIfTrouble)
		self.register_command(AlliesWatch)
		self.register_command(TryTownPoint)
		self.register_command(IfTowns)

	def parse_custom(self, token: Tokens.Token, parse_context: ParseContext) -> bool:
		if isinstance(token, Tokens.IdentifierToken) and token.raw_value == 'script':
			token = self.lexer.check_token(AILexer.ScriptIDToken)
			if not isinstance(token, AILexer.ScriptIDToken):
				raise PyMSError('Parse', "Expected script ID, got '%s' instead" % token.raw_value, line=self.lexer.line)
			line = self.lexer.line
			script_id = token.raw_value
			if script_id in self.script_headers:
				_,existing_line = self.script_headers[script_id]
				raise PyMSError('Parse', "A script with id '%s' is already defined on line %d" % (script_id, existing_line), line=self.lexer.line)
			code_handler = AIHeaderSourceCodeHandler(cast(AILexer, self.lexer))
			code_handler.parse(parse_context)
			# TODO: Validate header
			if not code_handler.script_header:
				raise PyMSError('Parse', "No script header found")
			if not code_handler.script_header.entry_point_name:
				raise PyMSError('Parse', "Script with ID '%s' is missing an 'entry_point'" % script_id, line=self.lexer.line)
			self.script_headers[script_id] = (code_handler.script_header, line)
			return True
		return False

class AIDefinitionsHandler(DefinitionsHandler):
	def __init__(self):
		super().__init__()
		self.register_type(MilitaryCodeType())
		self.register_type(BuildingCodeType())
		self.register_type(UpgradeCodeType())
		self.register_type(TechnologyCodeType())

		self.register_annotation('spellcaster')
