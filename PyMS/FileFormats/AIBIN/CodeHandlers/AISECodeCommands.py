
from . import CodeTypes
from . import AISECodeTypes

from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition

AttackTo = CodeCommandDefinition('attack_to', 'Prepare attack at region of {1} and attack to region of {2}', 0x71, (AISECodeTypes.PointCodeType(), AISECodeTypes.PointCodeType()))
AttackTimeout = CodeCommandDefinition('attack_timeout', 'TODO', 0x72, (CodeTypes.DWordCodeType(),))
IssueOrder = CodeCommandDefinition('ai_order', 'Issue order {1} for at most {2} units owned by current player matching type {3} at area {4}, targeting area {5} with target unit type {6} and flags {7}.', 0x73, (AISECodeTypes.OrderCodeType(), CodeTypes.WordCodeType(), AISECodeTypes.UnitGroupCodeType(), AISECodeTypes.AreaCodeType(), AISECodeTypes.AreaCodeType(), AISECodeTypes.UnitGroupCodeType(), AISECodeTypes.IssueOrderFlagsCodeType()))
Deaths = CodeCommandDefinition('deaths', 'Either jump to {5} based on comparing {2} deaths suffered by Player {1} of {4} to {3}, or modify the said deaths', 0x74, (CodeTypes.ByteCodeType(), AISECodeTypes.CompareTrigCodeType(), CodeTypes.DWordCodeType(), AISECodeTypes.UnitGroupCodeType(), AISECodeTypes.LongBlockCodeType()))
IdleOrders = CodeCommandDefinition('idle_orders', 'Set idle order {1} for the AI controlled unit {4} targeting {6}, executed every {2} frames with maximum of {3} units targeting a single unit and maximum distance of {5}. {6} sets the priority relative to other {1}.', 0x75, (AISECodeTypes.IdleOrderCodeType(), CodeTypes.WordCodeType(), CodeTypes.WordCodeType(), AISECodeTypes.UnitGroupCodeType(), CodeTypes.WordCodeType(), AISECodeTypes.UnitGroupCodeType(), CodeTypes.ByteCodeType(), AISECodeTypes.IdleOrderFlagsCodeType()))
IfAttacking = CodeCommandDefinition('if_attacking', 'Jumps to {1} if the AI is currently preparing an attack.', 0x76, (AISECodeTypes.LongBlockCodeType(),))
UnstartCampaign = CodeCommandDefinition('unstart_campaign', 'Clears the campaign flag', 0x77)
MaxWorkers = CodeCommandDefinition('max_workers', 'Sets maximum workers for the current town. 255 to restore default logic', 0x78, (CodeTypes.ByteCodeType(),))
UnderAttack = CodeCommandDefinition('under_attack', 'Sets mode for the AI-under-attack variable to {1}', 0x79, (AISECodeTypes.AttackModeCodeType(),))
AIControl = CodeCommandDefinition('aicontrol', 'TODO', 0x7A, (AISECodeTypes.AIControlCodeType(),))
BringJump = CodeCommandDefinition('bring_jump', 'Identical to bring trigger condition, jumps as action', 0x7B, (CodeTypes.ByteCodeType(), AISECodeTypes.CompareTrigCodeType(), CodeTypes.DWordCodeType(), AISECodeTypes.UnitGroupCodeType(), AISECodeTypes.AreaCodeType(), AISECodeTypes.LongBlockCodeType()))
CreateScript = CodeCommandDefinition('create_script', 'Creates a new thread, arguments are "block, player, area, town, resarea". To use values from current thread, pass player = 255, area = (65534, 65534), town = 255, resarea = 255', 0x7C, (AISECodeTypes.LongBlockCodeType(), CodeTypes.ByteCodeType(), AISECodeTypes.AreaCodeType(), CodeTypes.ByteCodeType(), CodeTypes.ByteCodeType())) # TODO: Custom types
PlayerJump = CodeCommandDefinition('player_jump', 'TODO', 0x7D, (CodeTypes.StringCodeType(), AISECodeTypes.LongBlockCodeType()))
AISEKills = CodeCommandDefinition('aise_kills', 'TODO', 0x7E, (CodeTypes.ByteCodeType(), CodeTypes.ByteCodeType(), AISECodeTypes.CompareTrigCodeType(), CodeTypes.DWordCodeType(), AISECodeTypes.UnitGroupCodeType(), AISECodeTypes.LongBlockCodeType())) # TODO: Custom types?
WaitRand = CodeCommandDefinition('wait_rand', 'TODO', 0x7F, (CodeTypes.DWordCodeType(), CodeTypes.DWordCodeType()), separate=True)
UpgradeJump = CodeCommandDefinition('upgrade_jump', 'TODO', 0x80, (CodeTypes.ByteCodeType(), AISECodeTypes.CompareTrigCodeType(), CodeTypes.UpgradeCodeType(), CodeTypes.ByteCodeType(), AISECodeTypes.LongBlockCodeType()))
TechJump = CodeCommandDefinition('tech_jump', 'TODO', 0x81, (CodeTypes.ByteCodeType(), AISECodeTypes.CompareTrigCodeType(), CodeTypes.TechnologyCodeType(), CodeTypes.ByteCodeType(), AISECodeTypes.LongBlockCodeType()))
RandomCall = CodeCommandDefinition('random_call', 'TODO', 0x82, (CodeTypes.ByteCodeType(), AISECodeTypes.LongBlockCodeType()))
AttackRand = CodeCommandDefinition('attack_rand', 'TODO', 0x83, (CodeTypes.ByteCodeType(), CodeTypes.ByteCodeType(), CodeTypes.MilitaryCodeType()))
Supply = CodeCommandDefinition('supply', 'TODO', 0x84, (CodeTypes.ByteCodeType(), AISECodeTypes.CompareTrigCodeType(), CodeTypes.WordCodeType(), AISECodeTypes.SupplyCodeType(), AISECodeTypes.UnitGroupCodeType(), AISECodeTypes.RaceCodeType(), AISECodeTypes.LongBlockCodeType()))
Time = CodeCommandDefinition('time', 'TODO', 0x85, (AISECodeTypes.CompareTrigCodeType(), CodeTypes.DWordCodeType(), AISECodeTypes.TimeCodeType(), AISECodeTypes.LongBlockCodeType()))
Resources = CodeCommandDefinition('resources', 'TODO', 0x86, (CodeTypes.ByteCodeType(), AISECodeTypes.CompareTrigCodeType(), AISECodeTypes.ResourceCodeType(), CodeTypes.DWordCodeType(), AISECodeTypes.LongBlockCodeType()))
SetID = CodeCommandDefinition('set_id', 'TODO', 0x87, (CodeTypes.ByteCodeType(),))
RemoveBuild = CodeCommandDefinition('remove_build', 'TODO', 0x88, (CodeTypes.ByteCodeType(), AISECodeTypes.UnitGroupCodeType(), CodeTypes.ByteCodeType()))
Guard = CodeCommandDefinition('guard', 'TODO', 0x89, (CodeTypes.UnitCodeType(), AISECodeTypes.PointCodeType(), CodeTypes.ByteCodeType(), CodeTypes.ByteCodeType(), CodeTypes.ByteCodeType()))
BaseLayoutOld = CodeCommandDefinition('base_layout_old', 'TODO', 0x8A, (CodeTypes.UnitCodeType(), AISECodeTypes.LayoutActionCodeType(), AISECodeTypes.AreaCodeType(), CodeTypes.ByteCodeType(), CodeTypes.ByteCodeType()))
Print = CodeCommandDefinition('print', 'Print {1}', 0x8B, (CodeTypes.StringCodeType(),))
Attacking = CodeCommandDefinition('attacking', 'TODO', 0x8C, (AISECodeTypes.BoolCompareCodeType(), AISECodeTypes.LongBlockCodeType()))
BaseLayout = CodeCommandDefinition('base_layout', 'TODO', 0x8D, (CodeTypes.UnitCodeType(), AISECodeTypes.LayoutActionCodeType(), AISECodeTypes.AreaCodeType(), CodeTypes.ByteCodeType(), CodeTypes.ByteCodeType(), CodeTypes.ByteCodeType()))
UnitAvailability = CodeCommandDefinition('unit_avail', 'TODO', 0x8E, (CodeTypes.ByteCodeType(), AISECodeTypes.CompareTrigCodeType(), AISECodeTypes.AvailabilityCodeType(), CodeTypes.UnitCodeType(), AISECodeTypes.LongBlockCodeType()))
LoadBunkers = CodeCommandDefinition('load_bunkers', 'TODO', 0x8F, (AISECodeTypes.AreaCodeType(), CodeTypes.UnitCodeType(), CodeTypes.ByteCodeType(), CodeTypes.UnitCodeType(), CodeTypes.ByteCodeType(), CodeTypes.ByteCodeType()))
Ping = CodeCommandDefinition('ping', 'TODO', 0x90, (CodeTypes.WordCodeType(), CodeTypes.WordCodeType(), CodeTypes.ByteCodeType()))
RevealArea = CodeCommandDefinition('reveal_area', 'TODO', 0x91, (CodeTypes.ByteCodeType(), AISECodeTypes.AreaCodeType(), CodeTypes.WordCodeType(), AISECodeTypes.RevealCodeType()))
TechAvailability = CodeCommandDefinition('tech_avail', 'TODO', 0x92, (CodeTypes.ByteCodeType(), AISECodeTypes.CompareTrigCodeType(), CodeTypes.TechnologyCodeType(), CodeTypes.ByteCodeType(), AISECodeTypes.LongBlockCodeType()))
RemoveCreep = CodeCommandDefinition('remove_creep', 'TODO', 0x93, (AISECodeTypes.AreaCodeType(),))
SaveBank = CodeCommandDefinition('save_bank', 'TODO', 0x94, (CodeTypes.StringCodeType(),))
LoadBank = CodeCommandDefinition('load_bank', 'TODO', 0x95, (CodeTypes.StringCodeType(),))
BankDataOld = CodeCommandDefinition('bank_data_old', 'TODO', 0x96, (AISECodeTypes.CompareTrigCodeType(), CodeTypes.StringCodeType(), CodeTypes.StringCodeType(), CodeTypes.DWordCodeType(), AISECodeTypes.LongBlockCodeType()))
UnitName = CodeCommandDefinition('unit_name', 'TODO', 0x97, (CodeTypes.ByteCodeType(), CodeTypes.UnitCodeType(), AISECodeTypes.AreaCodeType(), CodeTypes.StringCodeType(), AISECodeTypes.LayoutActionCodeType()))
BankData = CodeCommandDefinition('bank_data', 'TODO', 0x98, (AISECodeTypes.CompareTrigCodeType(), CodeTypes.DWordCodeType(), CodeTypes.StringCodeType(), CodeTypes.StringCodeType(), AISECodeTypes.LongBlockCodeType()))
LiftLand = CodeCommandDefinition('lift_land', 'TODO', 0x99, (CodeTypes.UnitCodeType(), CodeTypes.ByteCodeType(), AISECodeTypes.AreaCodeType(), AISECodeTypes.AreaCodeType(), CodeTypes.ByteCodeType(), CodeTypes.ByteCodeType(), CodeTypes.ByteCodeType()))
Queue = CodeCommandDefinition('queue', 'TODO', 0x9A, (CodeTypes.ByteCodeType(), CodeTypes.UnitCodeType(), CodeTypes.UnitCodeType(), CodeTypes.ByteCodeType(), AISECodeTypes.QueueFlagCodeType(), AISECodeTypes.AreaCodeType(), CodeTypes.ByteCodeType()))
AISEDebug = CodeCommandDefinition('aise_debug', 'TODO', 0x9B, (CodeTypes.StringCodeType(),))
ReplaceUnit = CodeCommandDefinition('replace_unit', 'TODO', 0x9C, (CodeTypes.UnitCodeType(), CodeTypes.UnitCodeType()))
Defense = CodeCommandDefinition('defense', 'TODO', 0x9D, (CodeTypes.WordCodeType(), CodeTypes.UnitCodeType(), AISECodeTypes.DefenseTypeCodeType(), AISECodeTypes.DefenseDirectionCodeType(), AISECodeTypes.DefenseDirectionCodeType()))
# __9e: None
# __9f: None
BWKills = CodeCommandDefinition('bw_kills', 'TODO', 0xA0, (CodeTypes.ByteCodeType(), AISECodeTypes.CompareTrigCodeType(), CodeTypes.DWordCodeType(), AISECodeTypes.UnitGroupCodeType(), AISECodeTypes.LongBlockCodeType()))
BuildAt = CodeCommandDefinition('build_at', 'TODO', 0xA1, (AISECodeTypes.UnitGroupCodeType(), AISECodeTypes.BuildAtPointCodeType(), AISECodeTypes.BuildAtFlagsCodeType()))
DebugName = CodeCommandDefinition('debug_name', 'TODO', 0xA2, (CodeTypes.StringCodeType(),))

all_commands = [
	AttackTo,
	AttackTimeout,
	IssueOrder,
	Deaths,
	IdleOrders,
	IfAttacking,
	UnstartCampaign,
	MaxWorkers,
	UnderAttack,
	AIControl,
	BringJump,
	CreateScript,
	PlayerJump,
	AISEKills,
	WaitRand,
	UpgradeJump,
	TechJump,
	RandomCall,
	AttackRand,
	Supply,
	Time,
	Resources,
	SetID,
	RemoveBuild,
	Guard,
	BaseLayoutOld,
	Print,
	Attacking,
	BaseLayout,
	UnitAvailability,
	LoadBunkers,
	Ping,
	RevealArea,
	TechAvailability,
	SaveBank,
	LoadBank,
	BankDataOld,
	UnitName,
	BankData,
	LiftLand,
	Queue,
	AISEDebug,
	ReplaceUnit,
	Defense,
	BWKills,
	BuildAt,
	DebugName,
]
