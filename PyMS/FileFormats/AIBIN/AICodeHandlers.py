
from .DataContext import DataContext

from ...Utilities.CodeHandlers.CodeDefs import *
from ...Utilities.CodeHandlers.ByteCodeHandler import ByteCodeHandler
from ...Utilities.CodeHandlers.SerializeContext import SerializeContext
from ...Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler
from ...Utilities.CodeHandlers.ParseContext import ParseContext
from ...Utilities.CodeHandlers.Lexer import *

import re

class AISerializeContext(SerializeContext):
	def __init__(self, definitions, data_context): # type: (str, DefinitionsHandler, DataContext) -> AISerializeContext
		SerializeContext.__init__(self, definitions)
		self.data_context = data_context

class AIParseContext(ParseContext):
	def __init__(self, definitions, data_context): # type: (str, DefinitionsHandler, DataContext) -> AIParseContext
		ParseContext.__init__(self, definitions)
		self.data_context = data_context

class ByteCodeType(IntCodeType):
	_name = 'byte'
	_bytecode_type = Struct.Type.u8()

class WordCodeType(IntCodeType):
	_name = 'word'
	_bytecode_type = Struct.Type.u16()

class DWordCodeType(IntCodeType):
	_name = 'dword'
	_bytecode_type = Struct.Type.u32()

class BlockCodeType(AddressCodeType):
	_name = 'block'
	_bytecode_type = Struct.Type.u16()

class UnitCodeType(WordCodeType):
	_name = 'unit'
	_limits = (0, 227) # TODO: Expanded DAT
	# TODO: Custom

	@classmethod
	def serialize(cls, value, context): # type: (int, AISerializeContext) -> str
		if context.definitions:
			variable = context.definitions.lookup_variable(value, cls)
			if variable:
				return variable.name
		if isinstance(context, AISerializeContext) and context.data_context:
			name = context.data_context.unit_name(value)
			if name:
				return StringCodeType.serialize(name, context)
		return str(value)

class BuildingCodeType(UnitCodeType):
	_name = 'building'
	# TODO: Custom

class MilitaryCodeType(UnitCodeType):
	_name = 'military'
	# TODO: Custom

class GGMilitaryCodeType(MilitaryCodeType):
	_name = 'gg_military'
	# TODO: Custom

class GAMilitaryCodeType(MilitaryCodeType):
	_name = 'ga_military'
	# TODO: Custom

class AGMilitaryCodeType(MilitaryCodeType):
	_name = 'ag_military'
	# TODO: Custom

class AAMilitaryCodeType(MilitaryCodeType):
	_name = 'aa_military'
	# TODO: Custom

class UpgradeCodeType(WordCodeType):
	_name = 'upgrade'
	_limits = (0, 60) # TODO: Expanded DAT
	# TODO: Custom

class TechnologyCodeType(WordCodeType):
	_name = 'technology'
	_limits = (0, 43) # TODO: Expanded DAT
	# TODO: Custom

class StringCodeType(StrCodeType):
	_name = 'string'

class CompareCodeType(EnumCodeType):
	_name = 'compare'
	_bytecode_type = Struct.Type.u8()
	_cases = {
		'GreaterThan': 1,
		'LessThan': 0
	}

class Goto(CodeCommand):
	_id = 0
	_name = 'goto'
	_param_types = [BlockCodeType]
	_ends_flow = True

class NoTownsJump(CodeCommand):
	_id = 1
	_name = 'notowns_jump'
	_param_types = [UnitCodeType, BlockCodeType]

class Wait(CodeCommand):
	_id = 2
	_name = 'wait'
	_param_types = [WordCodeType]
	_separate = True

class StartTown(CodeCommand):
	_id = 3
	_name = 'start_town'

class StartAreaTown(CodeCommand):
	_id = 4
	_name = 'start_areatown'

class Expand(CodeCommand):
	_id = 5
	_name = 'expand'
	_param_types = [ByteCodeType, BlockCodeType]

class Build(CodeCommand):
	_id = 6
	_name = 'build'
	_param_types = [ByteCodeType, BuildingCodeType, ByteCodeType]

class Upgrade(CodeCommand):
	_id = 7
	_name = 'upgrade'
	_param_types = [ByteCodeType, UpgradeCodeType, ByteCodeType]

class Tech(CodeCommand):
	_id = 8
	_name = 'tech'
	_param_types = [TechnologyCodeType, ByteCodeType]

class WaitBuild(CodeCommand):
	_id = 9
	_name = 'wait_build'
	_param_types = [ByteCodeType, BuildingCodeType]

class WaitBuildStart(CodeCommand):
	_id = 10
	_name = 'wait_buildstart'
	_param_types = [ByteCodeType, UnitCodeType]

class AttackClear(CodeCommand):
	_id = 11
	_name = 'attack_clear'

class AttackAdd(CodeCommand):
	_id = 12
	_name = 'attack_add'
	_param_types = [ByteCodeType, MilitaryCodeType]
	
class AttackPrepare(CodeCommand):
	_id = 13
	_name = 'attack_prepare'

class AttackDo(CodeCommand):
	_id = 14
	_name = 'attack_do'

class WaitSecure(CodeCommand):
	_id = 15
	_name = 'wait_secure'

class CaptExpand(CodeCommand):
	_id = 16
	_name = 'capt_expand'

class BuildBunkers(CodeCommand):
	_id = 17
	_name = 'build_bunkers'

class WaitBunkers(CodeCommand):
	_id = 18
	_name = 'wait_bunkers'

class DefenseBuildGG(CodeCommand):
	_id = 19
	_name = 'defensebuild_gg'
	_param_types = [ByteCodeType, GGMilitaryCodeType]

class DefenseBuildAG(CodeCommand):
	_id = 20
	_name = 'defensebuild_ag'
	_param_types = [ByteCodeType, AGMilitaryCodeType]

class DefenseBuildGA(CodeCommand):
	_id = 21
	_name = 'defensebuild_ga'
	_param_types = [ByteCodeType, GAMilitaryCodeType]

class DefenseBuildAA(CodeCommand):
	_id = 22
	_name = 'defensebuild_aa'
	_param_types = [ByteCodeType, AAMilitaryCodeType]

class DefenseUseGG(CodeCommand):
	_id = 23
	_name = 'defenseuse_gg'
	_param_types = [ByteCodeType, GGMilitaryCodeType]

class DefenseUseAG(CodeCommand):
	_id = 24
	_name = 'defenseuse_ag'
	_param_types = [ByteCodeType, AGMilitaryCodeType]

class DefenseUseGA(CodeCommand):
	_id = 25
	_name = 'defenseuse_ga'
	_param_types = [ByteCodeType, GAMilitaryCodeType]

class DefenseUseAA(CodeCommand):
	_id = 26
	_name = 'defenseuse_aa'
	_param_types = [ByteCodeType, AAMilitaryCodeType]

class DefenseClearGG(CodeCommand):
	_id = 27
	_name = 'defenseclear_gg'

class DefenseClearAG(CodeCommand):
	_id = 28
	_name = 'defenseclear_ag'

class DefenseClearGA(CodeCommand):
	_id = 29
	_name = 'defenseclear_ga'

class DefenseClearAA(CodeCommand):
	_id = 30
	_name = 'defenseclear_aa'

class SendSuicide(CodeCommand):
	_id = 31
	_name = 'send_suicide'
	_param_types = [ByteCodeType]

class PlayerEnemy(CodeCommand):
	_id = 32
	_name = 'player_enemy'

class PlayerAlly(CodeCommand):
	_id = 33
	_name = 'player_ally'

class DefaultMin(CodeCommand):
	_id = 34
	_name = 'default_min'
	_param_types = [ByteCodeType]

class DefaultBuildOff(CodeCommand):
	_id = 35
	_name = 'defaultbuild_off'

class Stop(CodeCommand):
	_id = 36
	_name = 'stop'
	_ends_flow = True

class SwitchRescue(CodeCommand):
	_id = 37
	_name = 'switch_rescue'

class MoveDT(CodeCommand):
	_id = 38
	_name = 'move_dt'

class Debug(CodeCommand):
	_id = 39
	_name = 'debug'
	_param_types = [BlockCodeType,StringCodeType]
	_ends_flow = True

class FatalError(CodeCommand):
	_id = 40
	_name = 'fatal_error'

class EnterBunker(CodeCommand):
	_id = 41
	_name = 'enter_bunker'

class ValueArea(CodeCommand):
	_id = 42
	_name = 'value_area'

class TransportsOff(CodeCommand):
	_id = 43
	_name = 'transports_off'

class CheckTransports(CodeCommand):
	_id = 44
	_name = 'check_transports'

class NukeRate(CodeCommand):
	_id = 45
	_name = 'nuke_rate'
	_param_types = [ByteCodeType]

class MaxForce(CodeCommand):
	_id = 46
	_name = 'max_force'
	_param_types = [WordCodeType]

class ClearCombatData(CodeCommand):
	_id = 47
	_name = 'clear_combatdata'

class RandomJump(CodeCommand):
	_id = 48
	_name = 'random_jump'
	_param_types = [ByteCodeType, BlockCodeType]

class TimeJump(CodeCommand):
	_id = 49
	_name = 'time_jump'
	_param_types = [ByteCodeType, BlockCodeType]

class FarmsNoTiming(CodeCommand):
	_id = 50
	_name = 'farms_notiming'

class FarmsTiming(CodeCommand):
	_id = 51
	_name = 'farms_timing'

class BuildTurrets(CodeCommand):
	_id = 52
	_name = 'build_turrets'

class WaitTurrets(CodeCommand):
	_id = 53
	_name = 'wait_turrets'

class DefaultBuild(CodeCommand):
	_id = 54
	_name = 'default_build'

class HarassFactor(CodeCommand):
	_id = 55
	_name = 'harass_factor'
	_param_types = [WordCodeType]

class StartCampaign(CodeCommand):
	_id = 56
	_name = 'start_campaign'

class RaceJump(CodeCommand):
	_id = 57
	_name = 'race_jump'
	_param_types = [BlockCodeType, BlockCodeType, BlockCodeType]
	_ends_flow = True

class RegionSize(CodeCommand):
	_id = 58
	_name = 'region_size'
	_param_types = [ByteCodeType, BlockCodeType]

class GetOldPeons(CodeCommand):
	_id = 59
	_name = 'get_oldpeons'
	_param_types = [ByteCodeType]

class GroundMapJump(CodeCommand):
	_id = 60
	_name = 'groundmap_jump'
	_param_types = [BlockCodeType]

class PlaceGuard(CodeCommand):
	_id = 61
	_name = 'place_guard'
	_param_types = [UnitCodeType, ByteCodeType]

class WaitForce(CodeCommand):
	_id = 62
	_name = 'wait_force'
	_param_types = [ByteCodeType, MilitaryCodeType]

class GuardResources(CodeCommand):
	_id = 63
	_name = 'guard_resources'
	_param_types = [MilitaryCodeType]

class Call(CodeCommand):
	_id = 64
	_name = 'call'
	_param_types = [BlockCodeType]

class Return(CodeCommand):
	_id = 65
	_name = 'return'
	_ends_flow = True

class EvalHarass(CodeCommand):
	_id = 66
	_name = 'eval_harass'
	_param_types = [BlockCodeType]

class Creep(CodeCommand):
	_id = 67
	_name = 'creep'
	_param_types = [ByteCodeType]

class Panic(CodeCommand):
	_id = 68
	_name = 'panic'
	_param_types = [BlockCodeType]

class PlayerNeed(CodeCommand):
	_id = 69
	_name = 'player_need'
	_param_types = [ByteCodeType,BuildingCodeType]

class DoMorph(CodeCommand):
	_id = 70
	_name = 'do_morph'
	_param_types = [ByteCodeType, MilitaryCodeType]

class WaitUpgrades(CodeCommand):
	_id = 71
	_name = 'wait_upgrades'

class MultiRun(CodeCommand):
	_id = 72
	_name = 'multirun'
	_param_types = [BlockCodeType]

class Rush(CodeCommand):
	_id = 73
	_name = 'rush'
	_param_types = [ByteCodeType, BlockCodeType]

class ScoutWith(CodeCommand):
	_id = 74
	_name = 'scout_with'
	_param_types = [MilitaryCodeType]

class DefineMax(CodeCommand):
	_id = 75
	_name = 'define_max'
	_param_types = [ByteCodeType, UnitCodeType]

class Train(CodeCommand):
	_id = 76
	_name = 'train'
	_param_types = [ByteCodeType, MilitaryCodeType]

class TargetExpansion(CodeCommand):
	_id = 77
	_name = 'target_expansion'

class WaitTrain(CodeCommand):
	_id = 78
	_name = 'wait_train'
	_param_types = [ByteCodeType, UnitCodeType]

class SetAttacks(CodeCommand):
	_id = 79
	_name = 'set_attacks'
	_param_types = [ByteCodeType]

class SetGenCMD(CodeCommand):
	_id = 80
	_name = 'set_gencmd'

class MakePatrol(CodeCommand):
	_id = 81
	_name = 'make_patrol'

class GiveMoney(CodeCommand):
	_id = 82
	_name = 'give_money'

class PrepDown(CodeCommand):
	_id = 83
	_name = 'prep_down'
	_param_types = [ByteCodeType, ByteCodeType, MilitaryCodeType]

class ResourcesJump(CodeCommand):
	_id = 84
	_name = 'resources_jump'
	_param_types = [WordCodeType, WordCodeType, BlockCodeType]

class EnterTransport(CodeCommand):
	_id = 85
	_name = 'enter_transport'

class ExitTransport(CodeCommand):
	_id = 86
	_name = 'exit_transport'

class SharedVisionOn(CodeCommand):
	_id = 87
	_name = 'sharedvision_on'
	_param_types = [ByteCodeType]

class SharedVisionOff(CodeCommand):
	_id = 88
	_name = 'sharedvision_off'
	_param_types = [ByteCodeType]

class NukeLocation(CodeCommand):
	_id = 89
	_name = 'nuke_location'

class HarassLocation(CodeCommand):
	_id = 90
	_name = 'harass_location'

class Implode(CodeCommand):
	_id = 91
	_name = 'implode'

class GuardAll(CodeCommand):
	_id = 92
	_name = 'guard_all'

class EnemyownsJump(CodeCommand):
	_id = 93
	_name = 'enemyowns_jump'
	_param_types = [UnitCodeType, BlockCodeType]

class EnemyResourcesJump(CodeCommand):
	_id = 94
	_name = 'enemyresources_jump'
	_param_types = [WordCodeType, WordCodeType, BlockCodeType]

class IfDif(CodeCommand):
	_id = 95
	_name = 'if_dif'
	_param_types = [CompareCodeType, ByteCodeType, BlockCodeType]

class EasyAttack(CodeCommand):
	_id = 96
	_name = 'easy_attack'
	_param_types = [ByteCodeType, MilitaryCodeType]

class KillThread(CodeCommand):
	_id = 97
	_name = 'kill_thread'
	_ends_flow = True

class Killable(CodeCommand):
	_id = 98
	_name = 'killable'

class WaitFinishAttack(CodeCommand):
	_id = 99
	_name = 'wait_finishattack'

class QuickAttack(CodeCommand):
	_id = 100
	_name = 'quick_attack'

class JunkyardDog(CodeCommand):
	_id = 101
	_name = 'junkyard_dog'

class FakeNuke(CodeCommand):
	_id = 102
	_name = 'fake_nuke'

class DisruptionWeb(CodeCommand):
	_id = 103
	_name = 'disruption_web'

class RecallLocation(CodeCommand):
	_id = 104
	_name = 'recall_location'

class SetRandomSeed(CodeCommand):
	_id = 105
	_name = 'set_randomseed'
	_param_types = [DWordCodeType]

class IfOwned(CodeCommand):
	_id = 106
	_name = 'if_owned'
	_param_types = [UnitCodeType,BlockCodeType]

class CreateNuke(CodeCommand):
	_id = 107
	_name = 'create_nuke'

class CreateUnit(CodeCommand):
	_id = 108
	_name = 'create_unit'
	_param_types = [UnitCodeType, WordCodeType, WordCodeType]

class NukePos(CodeCommand):
	_id = 109
	_name = 'nuke_pos'
	_param_types = [WordCodeType, WordCodeType]

class HelpIfTrouble(CodeCommand):
	_id = 110
	_name = 'help_iftrouble'

class AlliesWatch(CodeCommand):
	_id = 111
	_name = 'allies_watch'
	_param_types = [ByteCodeType, BlockCodeType]

class TryTownPoint(CodeCommand):
	_id = 112
	_name = 'try_townpoint'
	_param_types = [ByteCodeType, BlockCodeType]

class IfTowns(CodeCommand):
	_id = 113
	_name = 'if_towns'

class AIByteCodeHandler(ByteCodeHandler):
	def __init__(self, data):
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
	class SymbolToken(LiteralsToken):
		_literals = ('=', '@', '(', ')', ',', '{', '}')

	class ScriptIDToken(RegexToken):
		_regexp = re.compile(r'\S{4}')

	def __init__(self, code): # type: (str) -> AILexer
		Lexer.__init__(self, code)
		self.register_token_type(WhitespaceToken, skip=True)
		self.register_token_type(CommentToken, skip=True)
		self.register_token_type(AILexer.SymbolToken)
		self.register_token_type(IntegerToken)
		self.register_token_type(BooleanToken)
		self.register_token_type(IdentifierToken)
		self.register_token_type(StringToken)
		self.register_token_type(NewlineToken)
