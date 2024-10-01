
from .CodeTypes import *

from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition

Goto = CodeCommandDefinition('goto', 'Jump to {1}.', 0, (BlockCodeType(),), ends_flow=True)
NoTownsJump = CodeCommandDefinition('notowns_jump', 'If computer doesn\'t have a {1}, jump to {2}.', 1, (UnitCodeType(), BlockCodeType(),))
Wait = CodeCommandDefinition('wait', 'Wait for {1} tenths of second in normal game speed.', 2, (WordCodeType(),), separate=True)
StartTown = CodeCommandDefinition('start_town', 'Starts the AI Script for town management.', 3)
StartAreaTown = CodeCommandDefinition('start_areatown', 'Starts the AI Script for area town management.', 4)
Expand = CodeCommandDefinition('expand', 'Run code at {2} for expansion number {1}.', 5, (ByteCodeType(), BlockCodeType(),))
Build = CodeCommandDefinition('build', 'Build {2} until it commands {1} of them, at priority {3}.', 6, (ByteCodeType(), BuildingCodeType(), ByteCodeType(),))
Upgrade = CodeCommandDefinition('upgrade', 'Research upgrade {2} up to level {1}, at priority {3}.', 7, (ByteCodeType(), UpgradeCodeType(), ByteCodeType(),))
Tech = CodeCommandDefinition('tech', 'Research technology {1}, at priority {2}.', 8, (TechnologyCodeType(), ByteCodeType(),))
WaitBuild = CodeCommandDefinition('wait_build', 'Wait until computer commands {1} number of {2}.', 9, (ByteCodeType(), BuildingCodeType(),))
WaitBuildStart = CodeCommandDefinition('wait_buildstart', 'Wait until construction of {1} number of {2} has started.', 10, (ByteCodeType(), UnitCodeType(),))
AttackClear = CodeCommandDefinition('attack_clear', 'Clear the attack data.', 11)
AttackAdd = CodeCommandDefinition('attack_add', 'Add {1} number of {2} to the current attacking party.', 12, (ByteCodeType(), MilitaryCodeType(),))	
AttackPrepare = CodeCommandDefinition('attack_prepare', 'Prepare the attack.', 13)
AttackDo = CodeCommandDefinition('attack_do', 'Attack the enemy with the current prepared attacking party.', 14)
WaitSecure = CodeCommandDefinition('wait_secure', "Waits until the AI player trains a defense unit with defensebuild of any type. Is usable again after going through within about 7 seconds earlygame or 37 seconds later in the game (likely after 1500 frames).", 15)
CaptExpand = CodeCommandDefinition('capt_expand', "Creates state 4 regions around the AI's state 5 regions and other state 4 regions. If default_min is greater than 0, causes the AI to train first of its defensebuild_gg and _aa units until it hits a supply cap, define_max limit or has no resources left, at low priority. The AI then tries to distribute these units over state 4 regions, as evenly as possible.", 16)
BuildBunkers = CodeCommandDefinition('build_bunkers', 'Builds up to 3 bunkers around the base. Requests a Siege Tank guard in places where a bunker is built.', 17)
WaitBunkers = CodeCommandDefinition('wait_bunkers', 'Waits for the command build_bunkers to finish.', 18)
DefenseBuildGG = CodeCommandDefinition('defensebuild_gg', 'Build {1} number of {2} to defend against enemy attacking ground units, when ground units are attacked.', 19, (ByteCodeType(), GGMilitaryCodeType(),))
DefenseBuildAG = CodeCommandDefinition('defensebuild_ag', 'Build {1} number of {2} to defend against enemy attacking air units, when ground units are attacked.', 20, (ByteCodeType(), AGMilitaryCodeType(),))
DefenseBuildGA = CodeCommandDefinition('defensebuild_ga', 'Build {1} number of {2} to defend against enemy attacking ground units, when air units are attacked.', 21, (ByteCodeType(), GAMilitaryCodeType(),))
DefenseBuildAA = CodeCommandDefinition('defensebuild_aa', 'Build {1} number of {2} to defend against enemy attacking air units, when air units are attacked.', 22, (ByteCodeType(), AAMilitaryCodeType(),))
DefenseUseGG = CodeCommandDefinition('defenseuse_gg', 'Use {1} number of {2} to defend against enemy attacking ground units, when ground units are attacked.', 23, (ByteCodeType(), GGMilitaryCodeType(),))
DefenseUseAG = CodeCommandDefinition('defenseuse_ag', 'Use {1} number of {2} to defend against enemy attacking air units, when ground units are attacked.', 24, (ByteCodeType(), AGMilitaryCodeType(),))
DefenseUseGA = CodeCommandDefinition('defenseuse_ga', 'Use {1} number of {2} to defend against enemy attacking ground units, when air units are attacked.', 25, (ByteCodeType(), GAMilitaryCodeType(),))
DefenseUseAA = CodeCommandDefinition('defenseuse_aa', 'Use {1} number of {2} to defend against enemy attacking air units, when air units are attacked.', 26, (ByteCodeType(), AAMilitaryCodeType(),))
DefenseClearGG = CodeCommandDefinition('defenseclear_gg', 'Clear defense against enemy attacking ground units, when ground units are attacked.', 27)
DefenseClearAG = CodeCommandDefinition('defenseclear_ag', 'Clear defense against enemy attacking air units, when ground units are attacked.', 28)
DefenseClearGA = CodeCommandDefinition('defenseclear_ga', 'Clear defense against enemy attacking ground units, when air units are attacked.', 29)
DefenseClearAA = CodeCommandDefinition('defenseclear_aa', 'Clear defense against enemy attacking air units, when air units are attacked.', 30)
SendSuicide = CodeCommandDefinition('send_suicide', 'Send all units to suicide mission. {1} determines which type, 0 = Strategic suicide; 1 = Random suicide.', 31, (ByteCodeType(),)) # TODO: Custom type?
PlayerEnemy = CodeCommandDefinition('player_enemy', 'Makes all players in the specified location an enemy of the trigger owner. (STAREDIT)', 32)
PlayerAlly = CodeCommandDefinition('player_ally', 'Makes all players in the specified location an ally of the trigger owner. (STAREDIT)', 33)
DefaultMin = CodeCommandDefinition('default_min', 'Sets the default needed force value for state 4 and state 6 regions to {1}.', 34, (ByteCodeType(),))
DefaultBuildOff = CodeCommandDefinition('defaultbuild_off', 'Turns off default_build. default_build should realistically always be turned off.', 35)
Stop = CodeCommandDefinition('stop', 'Stop script code execution. Often used to close script blocks called simultaneously.', 36, ends_flow=True)
SwitchRescue = CodeCommandDefinition('switch_rescue', 'Switch computer to rescuable passive mode.', 37)
MoveDT = CodeCommandDefinition('move_dt', 'Orders the computer to move all Dark Templars, campaign and unit, to selected location. Crashes if a Dark Templar is being trained. (STAREDIT)', 38)
Debug = CodeCommandDefinition('debug', 'Show debug string {2} and continue in {1}.', 39, (BlockCodeType(),StringCodeType(),), ends_flow=True)
FatalError = CodeCommandDefinition('fatal_error', 'Crashes Starcraft with a fatal error and the message "Illegal AI script executed".', 40)
EnterBunker = CodeCommandDefinition('enter_bunker', 'Orders infantry units in selected location to attempt entering Bunkers in the same location. (STAREDIT)', 41)
ValueArea = CodeCommandDefinition('value_area', "Value this area higher. Causes the computer to consider the specified region for defense. If the AI doesn't control any buildings in the region, it will only be defended once. Doesn't do anything if the region already has enemy units in it. (STAREDIT)", 42)
TransportsOff = CodeCommandDefinition('transports_off', 'Tells the AI to not worry about managing transports until check_transports is called.', 43)
CheckTransports = CodeCommandDefinition('check_transports', 'Used in combination with header command transports_off, the AI will build and keep as many transports as was set by the define_max (max 5?) and use them for drops and expanding.', 44)
NukeRate = CodeCommandDefinition('nuke_rate', 'Tells the AI to launch nukes every {1} minutes.', 45, (ByteCodeType(),))
MaxForce = CodeCommandDefinition('max_force', "Lets the AI use up to {1} worth of units to defend any given defensible region. Force is determined for every unit using the standard calculation (see PyDAT's AI Actions tab under units.dat).", 46, (WordCodeType(),))
ClearCombatData = CodeCommandDefinition('clear_combatdata', 'Clear previous combat data.', 47)
RandomJump = CodeCommandDefinition('random_jump', 'There is {1} chances out of 256 to jump to {2}.', 48, (ByteCodeType(), BlockCodeType(),))
TimeJump = CodeCommandDefinition('time_jump', 'Jumps to {2} if {1} normal game minutes have passed in the game.', 49, (ByteCodeType(), BlockCodeType(),))
FarmsNoTiming = CodeCommandDefinition('farms_notiming', 'Build necessary farms only when it hits the maximum supply available.', 50)
FarmsTiming = CodeCommandDefinition('farms_timing', 'Build necessary farms with a correct timing, so nothing is paused by a maximum supply limit hit.', 51)
BuildTurrets = CodeCommandDefinition('build_turrets', 'Builds up to 6 missile turrets around the base. Requests a Ghost guard in places where a turret is built.', 52)
WaitTurrets = CodeCommandDefinition('wait_turrets', 'Waits for the command build_turrets to finish.', 53)
DefaultBuild = CodeCommandDefinition('default_build', 'Alters the behaviour of the AI so that if the AI has more than 600 minerals and 300 gas and no other requests, it will continuously train race specific units until it reaches the define_max value or gets supply capped. Usually should be disabled with defaultbuild_off.', 54)
HarassFactor = CodeCommandDefinition('harass_factor', """This command can be used to scale attacks based on enemy strength. It calculates the total strength of all enemy units (including buildings), then multiplies the current attack force by
((enemy_strength - 1) / Word) - 1
Division is rounded down, multiplication is limited to range from 1 (no change) to 3.""", 55, (WordCodeType(),))
StartCampaign = CodeCommandDefinition('start_campaign', 'Starts the AI Script for Campaign.', 56)
RaceJump = CodeCommandDefinition('race_jump', 'According to the enemy race, jump to {1} if enemy is Terran, {2} if Zerg, or {3} if Protoss.', 57, (BlockCodeType(), BlockCodeType(), BlockCodeType(),), ends_flow=True)
RegionSize = CodeCommandDefinition('region_size', 'Jump to {2} if the town this command is used in has a pathfinder region count (meaning the sum of pathfinder regions connected and pathable by ground) below 32 times {1}.', 58, (ByteCodeType(), BlockCodeType(),))
GetOldPeons = CodeCommandDefinition('get_oldpeons', 'Pull {1} existing workers from the main base to the expansion, but the main base will train the workers to replace the ones you took. Useful if you need workers as quickly as possible at the expansion.', 59, (ByteCodeType(),))
GroundMapJump = CodeCommandDefinition('groundmap_jump', 'If it is a ground map (in other words, if the enemy is reachable without transports), jump to {1}.', 60, (BlockCodeType(),))
PlaceGuard = CodeCommandDefinition('place_guard', 'Place one {1} to guard town at strategic location {2}, at priority 60. 0 is town location center, 1 is at the mineral line, 2 and up is the vespene geyser.', 61, (UnitCodeType(), ByteCodeType(),)) # TODO: Custom type?
WaitForce = CodeCommandDefinition('wait_force', "Wait until computer commands {1} of {2}, while training them as long as it's waiting. The request is checked every 30 frames. Waits for 16 frames whenever the requirement is not fulfilled.", 62, (ByteCodeType(), MilitaryCodeType(),))
GuardResources = CodeCommandDefinition('guard_resources', 'Send units of type {1} to guard as many resources spots as possible (1 per spot).', 63, (MilitaryCodeType(),))
Call = CodeCommandDefinition('call', 'Call {1} as a sub-routine.', 64, (BlockCodeType(),))
Return = CodeCommandDefinition('return', 'Return to the flow point of the call command.', 65, ends_flow=True)
EvalHarass = CodeCommandDefinition('eval_harass', """This command will initiate an attack if it has not (without waiting for grouping), and then it will calculate the strength of its own attack force and enemy units in 32-tile range around the target region. If either the ground or air strength of the attack force is larger than the respective enemy strength, the script will jump to {1}.

eval_harass will cause the grouping and attack to commence as usual, but it also can be canceled with attack_clear if you just want to use it for control flow instead of causing attacks.""", 66, (BlockCodeType(),))
Creep = CodeCommandDefinition('creep', 'Effects the placement of towers (blizzard always uses 3 or 4 for {1})', 67, (ByteCodeType(),))
Panic = CodeCommandDefinition('panic', "If AI has not expanded yet and total unmined minerals in the mineral line are less than 7500, then it will expand using {1}. If the AI has expanded before, the command triggers every time there are less than 7500 unmined minerals total in all owned bases, or there are less than 2 owned Refineries that are not depleted. Can cause crashes if any of the map's free resareas have no resources and never had them.", 68, (BlockCodeType(),))
PlayerNeed = CodeCommandDefinition('player_need', "Adds a request to the town so that if the player does not own {1} number of {2} anywhere, then it rebuilds them in this town at priority 80.", 69, (ByteCodeType(),BuildingCodeType(),))
DoMorph = CodeCommandDefinition('do_morph', 'Train {2} if it commands less than {1} of them.', 70, (ByteCodeType(), MilitaryCodeType(),))
WaitUpgrades = CodeCommandDefinition('wait_upgrades', 'Waits until all upgrade (not techs) requests have begun researching. Only works in campaign scripts. You should wait about 30 seconds (wait 480) before setting the requests and calling wait_upgrades, so that the request log has enough time to update.', 71)
MultiRun = CodeCommandDefinition('multirun', 'Run simultaneously code (so in another thread) at {1}.', 72, (BlockCodeType(),), separate=True)
Rush = CodeCommandDefinition('rush', 'Depending on {1}, it detects combinations of units and buildings either built or building, and jumps to {2}', 73, (ByteCodeType(), BlockCodeType(),))
ScoutWith = CodeCommandDefinition('scout_with', 'This command is unused.', 74, (MilitaryCodeType(),))
DefineMax = CodeCommandDefinition('define_max', 'Define maximum number of {2} to {1}. 255 is none.', 75, (ByteCodeType(), UnitCodeType(),))
Train = CodeCommandDefinition('train', 'Train {2} until it commands {1} of them.', 76, (ByteCodeType(), MilitaryCodeType(),))
TargetExpansion = CodeCommandDefinition('target_expansion', 'Executes an expansion attack with a deadline of 1 second (requires the units to be trained beforehand and practically has no grouping). Expansion attacks never choose bases built around start locations before 1500 in-game seconds. They can acquire those bases as targets afterwards, but they will still prefer to target expansions.', 77)
WaitTrain = CodeCommandDefinition('wait_train', 'Wait until computer commands {1} of {2}.', 78, (ByteCodeType(), UnitCodeType(),))
SetAttacks = CodeCommandDefinition('set_attacks', 'Sets the number of attacks possible to execute with target_expansion to {1}. Cannot be used if the campaign flag is set.', 79, (ByteCodeType(),))
SetGenCMD = CodeCommandDefinition('set_gencmd', 'Set the location as the generic command target to be used by other commands (like make_patrol). (STAREDIT)', 80)
MakePatrol = CodeCommandDefinition('make_patrol', 'Make units in selected location patrol to the location set using the set_gencmd command. (STAREDIT)', 81)
GiveMoney = CodeCommandDefinition('give_money', 'Give 2000 ore and gas if owned resources are low. Should only be used in campaign scripts.', 82)
PrepDown = CodeCommandDefinition('prep_down', """This command is similar to attack_add, but it can be used to add more units if the AI commands more of them. It is essentially:
attack_add max(unit_count({3}) - {1}, {2}) {3}""", 83, (ByteCodeType(), ByteCodeType(), MilitaryCodeType(),))
ResourcesJump = CodeCommandDefinition('resources_jump', 'If computer has at least {1} minerals and {2} gas then jump in {3}.', 84, (WordCodeType(), WordCodeType(), BlockCodeType(),))
EnterTransport = CodeCommandDefinition('enter_transport', 'Orders units in the location to enter the closest transport. (STAREDIT)', 85)
ExitTransport = CodeCommandDefinition('exit_transport', 'Orders transports in the location to unload the units within. (STAREDIT)', 86)
SharedVisionOn = CodeCommandDefinition('sharedvision_on', 'Player number {1} gives vision to the player executing the script. Players are 0-based. (STAREDIT)', 87, (ByteCodeType(),))  # TODO: Custom type?
SharedVisionOff = CodeCommandDefinition('sharedvision_off', 'Player number {1} stops giving vision to the player executing the script. Players are 0-based. (STAREDIT)', 88, (ByteCodeType(),))  # TODO: Custom type?
NukeLocation = CodeCommandDefinition('nuke_location', 'Nuke at selected location. Must have a ghost and a loaded nuke silo. (STAREDIT)', 89)
HarassLocation = CodeCommandDefinition('harass_location', 'AI Harass at selected location. (STAREDIT)', 90)
Implode = CodeCommandDefinition('implode', "Changes the state of AI regions: for any region which has state 0, 1, 2 or 3 that is connected to at most one pathfinding region by ground, the region's state is changed to 4.", 91)
GuardAll = CodeCommandDefinition('guard_all', 'Sets all regions with self-owned units in them to state 5, identical on melee.', 92)
EnemyownsJump = CodeCommandDefinition('enemyowns_jump', 'If enemy has a {1}, jump to {2}.', 93, (UnitCodeType(), BlockCodeType(),))
EnemyResourcesJump = CodeCommandDefinition('enemyresources_jump', 'If enemy has at least {1} minerals and {2} gas then jump in {3}.', 94, (WordCodeType(), WordCodeType(), BlockCodeType(),))
IfDif = CodeCommandDefinition('if_dif', """This command will jump to {3} if the "AI Difficulty" is LessThan/GreaterThan ({1}) {2}.
It seems that AI difficulty is mostly an unused concept. The AI Difficulty now is always 1, unless the AI has never started a town, in which case it is 0. There is also some unused functionality which would allow AI to mine more than 8 resources per trip if the difficulty was ever 2.""", 95, (CompareCodeType(), ByteCodeType(), BlockCodeType(),))
EasyAttack = CodeCommandDefinition('easy_attack', """This command functions the same as attack_add {1} {2}, but only if the "AI Diffiulty" value is 0. Otherwise it doesn't do anything.
It seems that AI difficulty is mostly an unused concept. The AI Difficulty now is always 1, unless the AI has never started a town, in which case it is 0. There is also some unused functionality which would allow AI to mine more than 8 resources per trip if the difficulty was ever 2.""", 96, (ByteCodeType(), MilitaryCodeType(),))
KillThread = CodeCommandDefinition('kill_thread', 'Kill the current thread.', 97, ends_flow=True)
Killable = CodeCommandDefinition('killable', 'Allows the current thread to be killed by another one.', 98)
WaitFinishAttack = CodeCommandDefinition('wait_finishattack', 'Wait until attacking party has finished to attack.', 99)
QuickAttack = CodeCommandDefinition('quick_attack', 'Sets the starting attack point back far enough in time so that the deadline goes down to 5 seconds. Never use this if it would set the starting point to before the first 16 frames of the game.', 100)
JunkyardDog = CodeCommandDefinition('junkyard_dog', 'Orders units in the selected location to Junkyard Dog (movement similar to that of a critter, but attacks nearby enemies if possible). (STAREDIT)', 101)
FakeNuke = CodeCommandDefinition('fake_nuke', 'Resets the AI nuke timer.', 102)
DisruptionWeb = CodeCommandDefinition('disruption_web', 'Cast a Disruption Web at the selected location. Player must have a Corsair with researched tech. (STAREDIT)', 103)
RecallLocation = CodeCommandDefinition('recall_location', 'Recall at the selected location. Player must have an Arbiter (not Danimoth) with researched tech. (STAREDIT)', 104)
SetRandomSeed = CodeCommandDefinition('set_randomseed', 'Set random seed to {1}.', 105, (DWordCodeType(),))
IfOwned = CodeCommandDefinition('if_owned', 'If the player owns {1} (includes incomplete) then jump to {2}.', 106, (UnitCodeType(),BlockCodeType(),))
CreateNuke = CodeCommandDefinition('create_nuke', 'Creates a nuke in a free silo. Should only be used in campaign scripts. Can be used multiple times as long as there are empty silos.', 107)
CreateUnit = CodeCommandDefinition('create_unit', 'Create {1} at map position (x,y) where x = {2} and y = {3}. Should only be used in campaign scripts.', 108, (UnitCodeType(), WordCodeType(), WordCodeType(),))
NukePos = CodeCommandDefinition('nuke_pos', 'Launch a nuke at map position (x,y) where x = {1} and y = {2}. Should only be used in campaign scripts.', 109, (WordCodeType(), WordCodeType(),))
HelpIfTrouble = CodeCommandDefinition('help_iftrouble', 'Ask allies for help if ever in trouble.', 110)
AlliesWatch = CodeCommandDefinition('allies_watch', "Expands at resource area number {1} using {2}. If {1} is below 9, it is a player's start location, otherwise it's a map's base location. Does nothing if resarea is occupied.", 111, (ByteCodeType(), BlockCodeType(),))
TryTownPoint = CodeCommandDefinition('try_townpoint', "Jump to {2} if the AI doesn't own at least {1} expansions (Includes areatowns). Ignored otherwise. Used in conjunction with expand or allies_watch.", 112, (ByteCodeType(), BlockCodeType(),))
IfTowns = CodeCommandDefinition('if_towns', 'Does not exist in memory.', 113)

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

HeaderNameString = CodeCommandDefinition('name_string', 'Set the name displayed in StarEdit for this script to string with index {1} in stat_txt.tbl', None, (TBLStringCodeType(),))
HeaderBinFile = CodeCommandDefinition('bin_file', 'Set which file this script is saved in to {1}', None, (BinFileCodeType(),))
BroodwarOnly = CodeCommandDefinition('broodwar_only', 'Set the flag for if this script is only available in BroodWar to {1}', None, (BoolCodeType(),))
StarEditHidden = CodeCommandDefinition('staredit_hidden', 'Set the flag for if this script is hidden in StarEdit to {1}', None, (BoolCodeType(),))
RequiresLocation = CodeCommandDefinition('requires_location', 'Set the flag for if this script requires a locaiton to {1}', None, (BoolCodeType(),))
EntryPoint = CodeCommandDefinition('entry_point', 'Set where the script will start to {1}', None, (BlockCodeType(),))

all_header_commands: list[CodeCommandDefinition] = [
	HeaderNameString,
	HeaderBinFile,
	BroodwarOnly,
	StarEditHidden,
	RequiresLocation,
	EntryPoint
]
