
from .CodeTypes import *

from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition

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

all_basic_commands: list[CodeCommandDefinition] = [
	Goto,
	NoTownsJump,
	Wait,
	StartTown,
	StartAreaTown,
	Expand,
	Build,
	Upgrade,
	Tech,
	WaitBuild,
	WaitBuildStart,
	AttackClear,
	AttackAdd,
	AttackPrepare,
	AttackDo,
	WaitSecure,
	CaptExpand,
	BuildBunkers,
	WaitBunkers,
	DefenseBuildGG,
	DefenseBuildAG,
	DefenseBuildGA,
	DefenseBuildAA,
	DefenseUseGG,
	DefenseUseAG,
	DefenseUseGA,
	DefenseUseAA,
	DefenseClearGG,
	DefenseClearAG,
	DefenseClearGA,
	DefenseClearAA,
	SendSuicide,
	PlayerEnemy,
	PlayerAlly,
	DefaultMin,
	DefaultBuildOff,
	Stop,
	SwitchRescue,
	MoveDT,
	Debug,
	FatalError,
	EnterBunker,
	ValueArea,
	TransportsOff,
	CheckTransports,
	NukeRate,
	MaxForce,
	ClearCombatData,
	RandomJump,
	TimeJump,
	FarmsNoTiming,
	FarmsTiming,
	BuildTurrets,
	WaitTurrets,
	DefaultBuild,
	HarassFactor,
	StartCampaign,
	RaceJump,
	RegionSize,
	GetOldPeons,
	GroundMapJump,
	PlaceGuard,
	WaitForce,
	GuardResources,
	Call,
	Return,
	EvalHarass,
	Creep,
	Panic,
	PlayerNeed,
	DoMorph,
	WaitUpgrades,
	MultiRun,
	Rush,
	ScoutWith,
	DefineMax,
	Train,
	TargetExpansion,
	WaitTrain,
	SetAttacks,
	SetGenCMD,
	MakePatrol,
	GiveMoney,
	PrepDown,
	ResourcesJump,
	EnterTransport,
	ExitTransport,
	SharedVisionOn,
	SharedVisionOff,
	NukeLocation,
	HarassLocation,
	Implode,
	GuardAll,
	EnemyownsJump,
	EnemyResourcesJump,
	IfDif,
	EasyAttack,
	KillThread,
	Killable,
	WaitFinishAttack,
	QuickAttack,
	JunkyardDog,
	FakeNuke,
	DisruptionWeb,
	RecallLocation,
	SetRandomSeed,
	IfOwned,
	CreateNuke,
	CreateUnit,
	NukePos,
	HelpIfTrouble,
	AlliesWatch,
	TryTownPoint,
	IfTowns,
]

# Commands used by header

HeaderNameString = CodeCommandDefinition('name_string', None, (TBLStringCodeType(),), ephemeral=True)
HeaderBinFile = CodeCommandDefinition('bin_file', None, (BinFileCodeType(),), ephemeral=True)
BroodwarOnly = CodeCommandDefinition('broodwar_only', None, (BoolCodeType(),), ephemeral=True)
StarEditHidden = CodeCommandDefinition('staredit_hidden', None, (BoolCodeType(),), ephemeral=True)
RequiresLocation = CodeCommandDefinition('requires_location', None, (BoolCodeType(),), ephemeral=True)
EntryPoint = CodeCommandDefinition('entry_point', None, (BlockCodeType(),), ephemeral=True)

all_header_commands: list[CodeCommandDefinition] = [
	HeaderNameString,
	HeaderBinFile,
	BroodwarOnly,
	StarEditHidden,
	RequiresLocation,
	EntryPoint
]
