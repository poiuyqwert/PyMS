
from . import CodeTypes
from . import AISECodeTypes

from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition

AttackTo = CodeCommandDefinition('attack_to', 'Prepare attack at region of {1} and attack to region of {2}', 0x71, (AISECodeTypes.PointCodeType(), AISECodeTypes.PointCodeType()))
AttackTimeout = CodeCommandDefinition('attack_timeout', 'TODO', 0x72, (CodeTypes.DWordCodeType(),))
IssueOrder = CodeCommandDefinition('ai_order', 'Issue order {1} for at most {2} units owned by current player matching type {3} at area {4}, targeting area {5} with target unit type {6} and flags {7}.', 0x73, (AISECodeTypes.OrderCodeType(), CodeTypes.WordCodeType(), AISECodeTypes.UnitGroupCodeType(), AISECodeTypes.AreaCodeType(), AISECodeTypes.AreaCodeType(), AISECodeTypes.UnitGroupCodeType(), AISECodeTypes.IssueOrderFlagsCodeType()))
Deaths = CodeCommandDefinition('deaths', 'Either jump to {5} based on comparing {2} deaths suffered by Player {1} of {4} to {3}, or modify the said deaths', 0x74, (CodeTypes.ByteCodeType(), AISECodeTypes.CompareTrigCodeType(), CodeTypes.DWordCodeType(), AISECodeTypes.UnitGroupCodeType(), AISECodeTypes.LongBlockCodeType()))
# IdleOrders = CodeCommandDefinition('idle_orders', 'Set idle order {1} for the AI controlled unit {4} targeting {6}, executed every {2} frames with maximum of {3} units targeting a single unit and maximum distance of {5}. {6} sets the priority relative to other {1}.', 0x75, (AISECodeTypes.IdleOrderCodeType(), CodeTypes.WordCodeType(), CodeTypes.WordCodeType(), AISECodeTypes.UnitGroupCodeType(), CodeTypes.WordCodeType(), AISECodeTypes.UnitGroupCodeType(), CodeTypes.ByteCodeType(), AISECodeTypes.IdleOrderFlagsCodeType()))
# idle_orders: ['ai_idle_order', 'ai_word', 'ai_word', 'ai_unit_or_group', 'ai_word', 'ai_unit_or_group', 'ai_byte', 'ai_idle_order_flags']
# if_attacking: ['ai_address']
# unstart_campaign: None
MaxWorkers = CodeCommandDefinition('max_workers', 'Sets maximum workers for the current town. 255 to restore default logic', 0x78, (CodeTypes.ByteCodeType(),))
# under_attack: ['ai_byte']
# aicontrol: ['ai_control_type']
# bring_jump: ['ai_byte', 'ai_compare_trig', 'ai_dword', 'ai_unit_or_group', 'ai_area', 'ai_address']
# create_script: ['ai_address', 'ai_byte', 'ai_area', 'ai_byte', 'ai_byte']
# player_jump: ['ai_string', 'ai_address']
# aise_kills: ['ai_byte', 'ai_byte', 'ai_compare_trig', 'ai_dword', 'ai_unit_or_group', 'ai_address']
# wait_rand: ['ai_dword', 'ai_dword']
# upgrade_jump: ['ai_byte', 'ai_compare_trig', 'ai_upgrade', 'ai_byte', 'ai_address']
# tech_jump: ['ai_byte', 'ai_compare_trig', 'ai_technology', 'ai_byte', 'ai_address']
# random_call: ['ai_byte', 'ai_address']
# attack_rand: ['ai_byte', 'ai_byte', 'ai_military']
# supply: ['ai_byte', 'ai_compare_trig', 'ai_word', 'ai_supply', 'ai_unit_or_group', 'ai_race', 'ai_address']
# time: ['ai_compare_trig', 'ai_dword', 'ai_time_type', 'ai_address']
# resources: ['ai_byte', 'ai_compare_trig', 'ai_resource_type', 'ai_dword', 'ai_address']
# set_id: ['ai_byte']
# remove_build: ['ai_byte', 'ai_unit_or_group', 'ai_byte']
# guard: ['ai_unit', 'ai_point', 'ai_byte', 'ai_byte', 'ai_byte']
# base_layout_old: ['ai_unit', 'ai_layout_action', 'ai_area', 'ai_byte', 'ai_byte']
# print: ['ai_string']
# attacking: ['ai_bool_compare', 'ai_address']
# base_layout: ['ai_unit', 'ai_layout_action', 'ai_area', 'ai_byte', 'ai_byte', 'ai_byte']
# unit_avail: ['ai_byte', 'ai_compare_trig', 'ai_avail', 'ai_unit', 'ai_address']
# load_bunkers: ['ai_area', 'ai_unit', 'ai_byte', 'ai_unit', 'ai_byte', 'ai_byte']
# ping: ['ai_word', 'ai_word', 'ai_byte']
# reveal_area: ['ai_byte', 'ai_area', 'ai_word', 'ai_reveal_type']
# tech_avail: ['ai_byte', 'ai_compare_trig', 'ai_technology', 'ai_byte', 'ai_address']
# remove_creep: ['ai_area']
# save_bank: ['ai_string']
# load_bank: ['ai_string']
# bank_data_old: ['ai_compare_trig', 'ai_string', 'ai_string', 'ai_dword', 'ai_address']
# unit_name: ['ai_byte', 'ai_unit', 'ai_area', 'ai_string', 'ai_layout_action']
# bank_data: ['ai_compare_trig', 'ai_dword', 'ai_string', 'ai_string', 'ai_address']
# lift_land: ['ai_unit', 'ai_byte', 'ai_area', 'ai_area', 'ai_byte', 'ai_byte', 'ai_byte']
# queue: ['ai_byte', 'ai_unit', 'ai_unit', 'ai_byte', 'ai_queue_flag', 'ai_area', 'ai_byte']
# aise_debug: ['ai_string']
# replace_unit: ['ai_unit', 'ai_unit']
# defense: ['ai_word', 'ai_unit', 'ai_defense_type', 'ai_defense_direction', 'ai_defense_direction']
# __9e: None
# __9f: None
# bw_kills: ['ai_byte', 'ai_compare_trig', 'ai_dword', 'ai_unit_or_group', 'ai_address']
# build_at: ['ai_unit_or_group', 'ai_build_at_point', 'ai_build_at_flags']
# debug_name: ['ai_string']

all_commands = [
	AttackTo,
	AttackTimeout,
	IssueOrder,
	Deaths,
	MaxWorkers,
]
