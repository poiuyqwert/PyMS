
import AbstractDAT
import DATFormat

from collections import OrderedDict
import json

class Unit(AbstractDAT.AbstractDATEntry):
	class SpecialAbilityFlag:
		building             = 1 << 0
		addon                = 1 << 1
		flyer                = 1 << 2
		resource_miner       = 1 << 3
		subunit              = 1 << 4
		flying_building      = 1 << 5
		hero                 = 1 << 6
		regenerate           = 1 << 7
		animated_idle        = 1 << 8
		cloakable            = 1 << 9
		two_units_in_one_egg = 1 << 10
		single_entity        = 1 << 11
		resource_depot       = 1 << 12
		resource_container   = 1 << 13
		robotic              = 1 << 14
		detector             = 1 << 15
		organic              = 1 << 16
		requires_creep       = 1 << 17
		unused               = 1 << 18
		requires_psi         = 1 << 19
		burrowable           = 1 << 20
		spellcaster          = 1 << 21
		permanent_cloak      = 1 << 22
		pickup_item          = 1 << 23
		ignores_supply_check = 1 << 24
		use_medium_overlays  = 1 << 25
		use_large_overlays   = 1 << 26
		battle_reactions     = 1 << 27
		full_auto_attack     = 1 << 28
		invincible           = 1 << 29
		mechanical           = 1 << 30
		produces_units       = 1 << 31

	class UnknownFlags:
		unknown0x01 = 1 << 0
		unknown0x02 = 1 << 1
		unknown0x04 = 1 << 2
		unknown0x08 = 1 << 3
		unknown0x10 = 1 << 4
		unknown0x20 = 1 << 5
		unknown0x40 = 1 << 6
		unknown0x80 = 1 << 7

	class StarEditGroupFlag:
		zerg        = 1 << 0
		terran      = 1 << 1
		protoss     = 1 << 2
		men         = 1 << 3
		building    = 1 << 4
		factory     = 1 << 5
		independent = 1 << 6
		neutral     = 1 << 7
		RACE_FLAGS  = (zerg | terran | protoss)
		GROUP_FLAGS = (men | building | factory | independent | neutral)
	
	class StarEditAvailabilityFlag:
		non_neutral           = 1 << 0
		unit_listing          = 1 << 1
		mission_briefing      = 1 << 2
		player_settings       = 1 << 3
		all_races             = 1 << 4
		set_doodad_state      = 1 << 5
		non_location_triggers = 1 << 6
		unit_hero_settings    = 1 << 7
		location_triggers     = 1 << 8
		broodwar_only         = 1 << 9
		ALL_FLAGS             = (non_neutral | unit_listing | mission_briefing | player_settings | all_races | set_doodad_state | non_location_triggers | unit_hero_settings | location_triggers | broodwar_only)

	class AIInternalFlag:
		no_suicide = 1 << 0
		no_guard   = 1 << 1
		ALL_FLAGS  = (no_suicide | no_guard)

	def __init__(self):
		self.graphics = 0
		self.subunit1 = 0
		self.subunit2 = 0
		self.infestation = 0
		self.construction_animation = 0
		self.unit_direction = 0
		self.shield_enabled = 0
		self.shield_amount = 0
		self.hit_points = DATFormat.DATTypeHitPoints()
		self.elevation_level = 0
		# TODO: Get more info
		self.unknown_flags = 0
		self.sublabel = 0
		self.comp_ai_idle = 0
		self.human_ai_idle = 0
		self.return_to_idle = 0
		self.attack_unit = 0
		self.attack_move = 0
		self.ground_weapon = 0
		self.max_ground_hits = 0
		self.air_weapon = 0
		self.max_air_hits = 0
		self.ai_internal = 0
		self.special_ability_flags = 0
		self.target_acquisition_range = 0
		self.sight_range = 0
		self.armor_upgrade = 0
		self.unit_size = 0
		self.armor = 0
		self.right_click_action = 0
		self.ready_sound = 0
		self.what_sound_start = 0
		self.what_sound_end = 0
		self.pissed_sound_start = 0
		self.pissed_sound_end = 0
		self.yes_sound_start = 0
		self.yes_sound_end = 0
		self.staredit_placement_size = DATFormat.DATTypeSize()
		self.addon_position = DATFormat.DATTypePosition()
		self.unit_extents = DATFormat.DATTypeExtents()
		self.portrait = 0
		self.mineral_cost = 0
		self.vespene_cost = 0
		self.build_time = 0
		self.requirements = 0
		self.staredit_group_flags = 0
		self.supply_provided = 0
		self.supply_required = 0
		self.space_required = 0
		self.space_provided = 0
		self.build_score = 0
		self.destroy_score = 0
		self.unit_map_string = 0
		self.broodwar_unit_flag = 0
		self.staredit_availability_flags = 0

	def load_values(self, values):
		self.graphics,\
		self.subunit1,\
		self.subunit2,\
		self.infestation,\
		self.construction_animation,\
		self.unit_direction,\
		self.shield_enabled,\
		self.shield_amount,\
		self.hit_points,\
		self.elevation_level,\
		self.unknown_flags,\
		self.sublabel,\
		self.comp_ai_idle,\
		self.human_ai_idle,\
		self.return_to_idle,\
		self.attack_unit,\
		self.attack_move,\
		self.ground_weapon,\
		self.max_ground_hits,\
		self.air_weapon,\
		self.max_air_hits,\
		self.ai_internal,\
		self.special_ability_flags,\
		self.target_acquisition_range,\
		self.sight_range,\
		self.armor_upgrade,\
		self.unit_size,\
		self.armor,\
		self.right_click_action,\
		self.ready_sound,\
		self.what_sound_start,\
		self.what_sound_end,\
		self.pissed_sound_start,\
		self.pissed_sound_end,\
		self.yes_sound_start,\
		self.yes_sound_end,\
		self.staredit_placement_size,\
		self.addon_position,\
		self.unit_extents,\
		self.portrait,\
		self.mineral_cost,\
		self.vespene_cost,\
		self.build_time,\
		self.requirements,\
		self.staredit_group_flags,\
		self.supply_provided,\
		self.supply_required,\
		self.space_required,\
		self.space_provided,\
		self.build_score,\
		self.destroy_score,\
		self.unit_map_string,\
		self.broodwar_unit_flag,\
		self.staredit_availability_flags\
			= values

	def save_values(self):
		return (
			self.graphics,
			self.subunit1,
			self.subunit2,
			self.infestation,
			self.construction_animation,
			self.unit_direction,
			self.shield_enabled,
			self.shield_amount,
			self.hit_points,
			self.elevation_level,
			self.unknown_flags,
			self.sublabel,
			self.comp_ai_idle,
			self.human_ai_idle,
			self.return_to_idle,
			self.attack_unit,
			self.attack_move,
			self.ground_weapon,
			self.max_ground_hits,
			self.air_weapon,
			self.max_air_hits,
			self.ai_internal,
			self.special_ability_flags,
			self.target_acquisition_range,
			self.sight_range,
			self.armor_upgrade,
			self.unit_size,
			self.armor,
			self.right_click_action,
			self.ready_sound,
			self.what_sound_start,
			self.what_sound_end,
			self.pissed_sound_start,
			self.pissed_sound_end,
			self.yes_sound_start,
			self.yes_sound_end,
			self.staredit_placement_size,
			self.addon_position,
			self.unit_extents,
			self.portrait,
			self.mineral_cost,
			self.vespene_cost,
			self.build_time,
			self.requirements,
			self.staredit_group_flags,
			self.supply_provided,
			self.supply_required,
			self.space_required,
			self.space_provided,
			self.build_score,
			self.destroy_score,
			self.unit_map_string,
			self.broodwar_unit_flag,
			self.staredit_availability_flags
		)

	def expand(self):
		self.graphics = self.graphics or 0
		self.subunit1 = self.subunit1 or 0
		self.subunit2 = self.subunit2 or 0
		self.infestation = self.infestation or 0
		self.construction_animation = self.construction_animation or 0
		self.unit_direction = self.unit_direction or 0
		self.shield_enabled = self.shield_enabled or 0
		self.shield_amount = self.shield_amount or 0
		self.hit_points = self.hit_points or DATFormat.DATTypeHitPoints()
		self.elevation_level = self.elevation_level or 0
		self.unknown_flags = self.unknown_flags or 0
		self.sublabel = self.sublabel or 0
		self.comp_ai_idle = self.comp_ai_idle or 0
		self.human_ai_idle = self.human_ai_idle or 0
		self.return_to_idle = self.return_to_idle or 0
		self.attack_unit = self.attack_unit or 0
		self.attack_move = self.attack_move or 0
		self.ground_weapon = self.ground_weapon or 0
		self.max_ground_hits = self.max_ground_hits or 0
		self.air_weapon = self.air_weapon or 0
		self.max_air_hits = self.max_air_hits or 0
		self.ai_internal = self.ai_internal or 0
		self.special_ability_flags = self.special_ability_flags or 0
		self.target_acquisition_range = self.target_acquisition_range or 0
		self.sight_range = self.sight_range or 0
		self.armor_upgrade = self.armor_upgrade or 0
		self.unit_size = self.unit_size or 0
		self.armor = self.armor or 0
		self.right_click_action = self.right_click_action or 0
		self.ready_sound = self.ready_sound or 0
		self.what_sound_start = self.what_sound_start or 0
		self.what_sound_end = self.what_sound_end or 0
		self.pissed_sound_start = self.pissed_sound_start or 0
		self.pissed_sound_end = self.pissed_sound_end or 0
		self.yes_sound_start = self.yes_sound_start or 0
		self.yes_sound_end = self.yes_sound_end or 0
		self.staredit_placement_size = self.staredit_placement_size or DATFormat.DATTypeSize()
		self.addon_position = self.addon_position or DATFormat.DATTypePosition()
		self.unit_extents = self.unit_extents or DATFormat.DATTypeExtents()
		self.portrait = self.portrait or 0
		self.mineral_cost = self.mineral_cost or 0
		self.vespene_cost = self.vespene_cost or 0
		self.build_time = self.build_time or 0
		self.requirements = self.requirements or 0
		self.staredit_group_flags = self.staredit_group_flags or 0
		self.supply_provided = self.supply_provided or 0
		self.supply_required = self.supply_required or 0
		self.space_required = self.space_required or 0
		self.space_provided = self.space_provided or 0
		self.build_score = self.build_score or 0
		self.destroy_score = self.destroy_score or 0
		self.unit_map_string = self.unit_map_string or 0
		self.broodwar_unit_flag = self.broodwar_unit_flag or 0
		self.staredit_availability_flags = self.staredit_availability_flags or 0

	def export_text(self, id):
		return """Unit(%d):
	graphics %d
	subunit1 %d
	subunit2 %d
	infestation %d
	construction_animation %d
	unit_direction %d
	shield_enabled %d
	shield_amount %d
	hit_points.whole %d
	hot_points.fraction %d
	elevation_level %d
	unknown_flags %d
	sublabel %d
	comp_ai_idle %d
	human_ai_idle %d
	return_to_idle %d
	attack_unit %d
	attack_move %d
	ground_weapon %d
	max_ground_hits %d
	air_weapon %d
	max_air_hits %d
	ai_internal %d
	special_ability_flags %d
	target_acquisition_range %d
	sight_range %d
	armor_upgrade %d
	unit_size %d
	armor %d
	right_click_action %d
	ready_sound %d
	what_sound_start %d
	what_sound_end %d
	pissed_sound_start %d
	pissed_sound_end %d
	yes_sound_start %d
	yes_sound_end %d
	staredit_placement_size.width %d
	staredit_placement_size.height %d
	addon_position.x %d
	addon_position_y %d
	unit_extents.left %d
	unit_extents.up %d
	unit_extents.right %d
	unit_extents.down %d
	portrait %d
	mineral_cost %d
	vespene_cost %d
	build_time %d
	requirements %d
	staredit_group_flags %d
	supply_provided %d
	supply_required %d
	space_required %d
	space_provided %d
	build_score %d
	destroy_score %d
	unit_map_string %d
	broodwar_unit_flag %d
	staredit_availability_flags %d""" % (
			id,
			self.graphics,
			self.subunit1,
			self.subunit2,
			self.infestation,
			self.construction_animation,
			self.unit_direction,
			self.shield_enabled,
			self.shield_amount,
			self.hit_points.whole,
			self.hit_points.fraction,
			self.elevation_level,
			self.unknown_flags,
			self.sublabel,
			self.comp_ai_idle,
			self.human_ai_idle,
			self.return_to_idle,
			self.attack_unit,
			self.attack_move,
			self.ground_weapon,
			self.max_ground_hits,
			self.air_weapon,
			self.max_air_hits,
			self.ai_internal,
			self.special_ability_flags,
			self.target_acquisition_range,
			self.sight_range,
			self.armor_upgrade,
			self.unit_size,
			self.armor,
			self.right_click_action,
			self.ready_sound,
			self.what_sound_start,
			self.what_sound_end,
			self.pissed_sound_start,
			self.pissed_sound_end,
			self.yes_sound_start,
			self.yes_sound_end,
			self.staredit_placement_size.width,
			self.staredit_placement_size.height,
			self.addon_position.x,
			self.addon_position.y,
			self.unit_extents.left,
			self.unit_extents.up,
			self.unit_extents.right,
			self.unit_extents.down,
			self.portrait,
			self.mineral_cost,
			self.vespene_cost,
			self.build_time,
			self.requirements,
			self.staredit_group_flags,
			self.supply_provided,
			self.supply_required,
			self.space_required,
			self.space_provided,
			self.build_score,
			self.destroy_score,
			self.unit_map_string,
			self.broodwar_unit_flag,
			self.staredit_availability_flags
		)

	def export_json(self, id, dump=True, indent=4):
		data = OrderedDict()
		data["_type"] = "Unit"
		data["_id"] = id
		data["graphics"] = self.graphics
		data["subunit1"] = self.subunit1
		data["subunit2"] = self.subunit2
		data["infestation"] = self.infestation
		data["construction_animation"] = self.construction_animation
		data["unit_direction"] = self.unit_direction
		data["shield_enabled"] = self.shield_enabled
		data["shield_amount"] = self.shield_amount
		hit_points = OrderedDict()
		hit_points["whole"] = self.hit_points.whole
		hit_points["fraction"] = self.hit_points.fraction
		data["hit_points"] = hit_points
		data["elevation_level"] = self.elevation_level
		data["unknown_flags"] = self.unknown_flags
		data["sublabel"] = self.sublabel
		data["comp_ai_idle"] = self.comp_ai_idle
		data["human_ai_idle"] = self.human_ai_idle
		data["return_to_idle"] = self.return_to_idle
		data["attack_unit"] = self.attack_unit
		data["attack_move"] = self.attack_move
		data["ground_weapon"] = self.ground_weapon
		data["max_ground_hits"] = self.max_ground_hits
		data["air_weapon"] = self.air_weapon
		data["max_air_hits"] = self.max_air_hits
		data["ai_internal"] = self.ai_internal
		data["special_ability_flags"] = self.special_ability_flags
		data["target_acquisition_range"] = self.target_acquisition_range
		data["sight_range"] = self.sight_range
		data["armor_upgrade"] = self.armor_upgrade
		data["unit_size"] = self.unit_size
		data["armor"] = self.armor
		data["right_click_action"] = self.right_click_action
		data["ready_sound"] = self.ready_sound
		data["what_sound_start"] = self.what_sound_start
		data["what_sound_end"] = self.what_sound_end
		data["pissed_sound_start"] = self.pissed_sound_start
		data["pissed_sound_end"] = self.pissed_sound_end
		data["yes_sound_start"] = self.yes_sound_start
		data["yes_sound_end"] = self.yes_sound_end
		staredit_placement_size = OrderedDict()
		staredit_placement_size["width"] = self.staredit_placement_size.width
		staredit_placement_size["height"] = self.staredit_placement_size.height
		data["staredit_placement_size"] = staredit_placement_size
		addon_position = OrderedDict()
		addon_position["x"] = self.addon_position.x
		addon_position["y"] = self.addon_position.y
		data["addon_position"] = addon_position
		unit_extents = OrderedDict()
		unit_extents["left"] = self.unit_extents.left
		unit_extents["up"] = self.unit_extents.up
		unit_extents["right"] = self.unit_extents.right
		unit_extents["down"] = self.unit_extents.down
		data["unit_extents"] = unit_extents
		data["portrait"] = self.portrait
		data["mineral_cost"] = self.mineral_cost
		data["vespene_cost"] = self.vespene_cost
		data["build_time"] = self.build_time
		data["requirements"] = self.requirements
		data["staredit_group_flags"] = self.staredit_group_flags
		data["supply_provided"] = self.supply_provided
		data["supply_required"] = self.supply_required
		data["space_required"] = self.space_required
		data["space_provided"] = self.space_provided
		data["build_score"] = self.build_score
		data["destroy_score"] = self.destroy_score
		data["unit_map_string"] = self.unit_map_string
		data["broodwar_unit_flag"] = self.broodwar_unit_flag
		data["staredit_availability_flags"] = self.staredit_availability_flags
		if not dump:
			return data
		return json.dumps(data, indent=indent)


# units.dat file handler
class UnitsDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 228,
			"expanded_entries_multiple": 12,
			"expanded_min_entries": 250,
			"expanded_max_entries": 912,
			"expanded_entries_reserved": [
				228,
				229,
				230,
				231,
				232,
				233,
				234,
				235,
				236,
				237,
				238,
				239,
				240,
				241,
				242,
				243,
				244,
				245,
				246,
				247,
				248,
				249,
				250
			],
			"properties": [
				{
					"name": "graphics",
					"type": "byte",
					"expanded_type": "short"
				},
				{
					"name": "subunit1",
					"type": "short"
				},
				{
					"name": "subunit2",
					"type": "short"
				},
				{
					"name": "infestation",
					"type": "short",
					"entry_offset": 106,
					"entry_count": 96
				},
				{
					"name": "construction_animation",
					"type": "long"
				},
				{
					"name": "unit_direction",
					"type": "byte"
				},
				{
					"name": "shield_enabled",
					"type": "byte"
				},
				{
					"name": "shield_amount",
					"type": "short"
				},
				{
					"name": "hit_points",
					"type": "hit_points"
				},
				{
					"name": "elevation_level",
					"type": "byte"
				},
				{
					"name": "unknown_flags",
					"type": "byte"
				},
				{
					"name": "sublabel",
					"type": "byte"
				},
				{
					"name": "comp_ai_idle",
					"type": "byte"
				},
				{
					"name": "human_ai_idle",
					"type": "byte"
				},
				{
					"name": "return_to_idle",
					"type": "byte"
				},
				{
					"name": "attack_unit",
					"type": "byte"
				},
				{
					"name": "attack_move",
					"type": "byte"
				},
				{
					"name": "ground_weapon",
					"type": "byte"
				},
				{
					"name": "max_ground_hits",
					"type": "byte"
				},
				{
					"name": "air_weapon",
					"type": "byte"
				},
				{
					"name": "max_air_hits",
					"type": "byte"
				},
				{
					"name": "ai_internal",
					"type": "byte"
				},
				{
					"name": "special_ability_flags",
					"type": "long"
				},
				{
					"name": "target_acquisition_range",
					"type": "byte"
				},
				{
					"name": "sight_range",
					"type": "byte"
				},
				{
					"name": "armor_upgrade",
					"type": "byte"
				},
				{
					"name": "unit_size",
					"type": "byte"
				},
				{
					"name": "armor",
					"type": "byte"
				},
				{
					"name": "right_click_action",
					"type": "byte"
				},
				{
					"name": "ready_sound",
					"type": "short",
					"entry_offset": 0,
					"entry_count": 106
				},
				{
					"name": "what_sound_start",
					"type": "short"
				},
				{
					"name": "what_sound_end",
					"type": "short"
				},
				{
					"name": "pissed_sound_start",
					"type": "short",
					"entry_offset": 0,
					"entry_count": 106
				},
				{
					"name": "pissed_sound_end",
					"type": "short",
					"entry_offset": 0,
					"entry_count": 106
				},
				{
					"name": "yes_sound_start",
					"type": "short",
					"entry_offset": 0,
					"entry_count": 106
				},
				{
					"name": "yes_sound_end",
					"type": "short",
					"entry_offset": 0,
					"entry_count": 106
				},
				{
					"name": "staredit_placement_size",
					"type": "size"
				},
				{
					"name": "addon_position",
					"type": "position",
					"entry_offset": 106,
					"entry_count": 96
				},
				{
					"name": "unit_extents",
					"type": "extents"
				},
				{
					"name": "portrait",
					"type": "short"
				},
				{
					"name": "mineral_cost",
					"type": "short"
				},
				{
					"name": "vespene_cost",
					"type": "short"
				},
				{
					"name": "build_time",
					"type": "short"
				},
				{
					"name": "requirements",
					"type": "short"
				},
				{
					"name": "staredit_group_flags",
					"type": "byte"
				},
				{
					"name": "supply_provided",
					"type": "byte"
				},
				{
					"name": "supply_required",
					"type": "byte"
				},
				{
					"name": "space_required",
					"type": "byte"
				},
				{
					"name": "space_provided",
					"type": "byte"
				},
				{
					"name": "build_score",
					"type": "short"
				},
				{
					"name": "destroy_score",
					"type": "short"
				},
				{
					"name": "unit_map_string",
					"type": "short"
				},
				{
					"name": "broodwar_unit_flag",
					"type": "byte"
				},
				{
					"name": "staredit_availability_flags",
					"type": "short"
				}
			]
		})
	ENTRY_STRUCT = Unit
	FILE_NAME = "units.dat"
