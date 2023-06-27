
class ConditionType:
	no_condition = 0
	countdown_timer = 1
	command = 2
	bring = 3
	accumulate = 4
	kill = 5
	commands_the_most = 6
	commands_the_most_at = 7
	most_kills = 8
	highest_score = 9
	most_resources = 10
	switch = 11
	elapsed_time = 12
	is_mission_briefing = 13
	opponents = 14
	deaths = 15
	commands_the_least = 16
	commands_the_least_at = 17
	least_kills = 18
	lowest_score = 19
	least_resources = 20
	score = 21
	always = 22
	never = 23

class ActionType:
	no_action = 0
	victory = 1
	defeat = 2
	preserve_trigger = 3
	wait = 4
	pause_game = 5
	unpause_game = 6
	transmission = 7
	play_wav = 8
	display_message = 9
	center_view = 10
	create_unit_properties = 11
	set_mission_objectives = 12
	set_switch = 13
	set_countdown_timer = 14
	run_aiscript = 15
	run_aiscript_at_location = 16
	leaderboard_control = 17
	leaderboard_control_at_location = 18
	leaderboard_resources = 19
	leaderboard_kills = 20
	leaderboard_points = 21
	kill_unit = 22
	kill_unit_at_location = 23
	remove_unit = 24
	remove_unit_at_location = 25
	set_resources = 26
	set_score = 27
	minimap_ping = 28
	talking_portrait = 29
	mute_unit_speech = 30
	unmute_unit_speech = 31
	leaderboard_computer_players = 32
	leaderboard_goal_control = 33
	leaderboard_goal_control_at_location = 34
	leaderboard_goal_resources = 35
	leaderboard_goal_kills = 36
	leaderboard_goal_points = 37
	move_location = 38
	move_unit = 39
	leaderboard_greed = 40
	set_next_scenario = 41
	set_doodad_state = 42
	set_invincibility = 43
	create_unit = 44
	set_deaths = 45
	order = 46
	comment = 47
	give_units = 48
	modify_unit_hit_points = 49
	modify_unit_energy = 50
	modify_unit_shield_points = 51
	modify_unit_resources = 52
	modify_unit_hanger_count = 53
	pause_timer = 54
	unpause_timer = 55
	draw = 56
	set_alliance_status = 57
	disable_debug_mode = 58
	enable_debug_mode = 59


class Comparison:
	at_least = 0
	at_most = 1
	exactly = 10

class SwitchState:
	set = 2
	cleared = 3

class ConditionFlag:
	disabled = (1 << 1)
	unit_type_used = (1 << 4)

class PlayerGroup:
	p1 = 0
	p2 = 1
	p3 = 2
	p4 = 3
	p5 = 4
	p6 = 5
	p7 = 6
	p8 = 7
	p9 = 8
	p10 = 9
	p11 = 10
	p12 = 11
	none = 12
	current_player = 13
	foes = 14
	allies = 15
	neutral_players = 16
	all_players = 17
	force_1 = 18
	force_2 = 19
	force_3 = 20
	force_4 = 21
	unused_1 = 22
	unused_2 = 23
	unused_3 = 24
	unused_4 = 25
	non_allied_victory_players = 26

class UnitType:
	none = 228
	any = 229
	men = 230
	buildings = 231
	factories = 232

class ResourceType:
	ore = 0
	gas = 1
	ore_and_gas = 2

class ScoreType:
	total = 0
	units = 1
	buildings = 2
	units_and_buildings = 3
	kills = 4
	razings = 5
	kills_and_razings = 6
	custom = 7

class AllianceStatus:
	enemy = 0
	ally = 1
	allied_victory = 2

class BriefingActionType:
	no_action = 0
	wait = 1
	play_wav = 2
	text_message = 3
	mission_objective = 4
	show_portrait = 5
	hide_portrait = 6
	display_speaking_portrait = 7
	transmission = 8
	skip_tutorial_enabled = 9

class SwitchAction:
	set = 4
	clear = 5
	toggle = 6
	randomize = 11

class StateAction:
	set = 4
	clear = 5
	toggle = 6

class Order:
	move = 0
	patrol = 1
	attack = 2

class NumberModifier:
	set = 7
	add = 8
	subtract = 9

class ActionFlag:
	ignore_wait_once = (1 << 0)
	disabled = (1 << 1)
	always_display = (1 << 2)
	unit_property_used = (1 << 3)
	unit_type_used = (1 << 4)

Masked = 0x4353




class Matches:
	no = 0
	low = 100
	medium = 200
	high = 300
