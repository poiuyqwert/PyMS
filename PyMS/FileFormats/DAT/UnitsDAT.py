
from . import AbstractDAT
from . import DATFormat
from . import DATCoders

class Unit(AbstractDAT.AbstractDATEntry):
	class Property:
		graphics = 'graphics'
		subunit1 = 'subunit1'
		subunit2 = 'subunit2'
		infestation = 'infestation'
		construction_animation = 'construction_animation'
		unit_direction = 'unit_direction'
		shield_enabled = 'shield_enabled'
		shield_amount = 'shield_amount'
		hit_points = 'hit_points'
		elevation_level = 'elevation_level'
		unknown_flags = 'unknown_flags'
		sublabel = 'sublabel'
		comp_ai_idle = 'comp_ai_idle'
		human_ai_idle = 'human_ai_idle'
		return_to_idle = 'return_to_idle'
		attack_unit = 'attack_unit'
		attack_move = 'attack_move'
		ground_weapon = 'ground_weapon'
		max_ground_hits = 'max_ground_hits'
		air_weapon = 'air_weapon'
		max_air_hits = 'max_air_hits'
		ai_internal = 'ai_internal'
		special_ability_flags = 'special_ability_flags'
		target_acquisition_range = 'target_acquisition_range'
		sight_range = 'sight_range'
		armor_upgrade = 'armor_upgrade'
		unit_size = 'unit_size'
		armor = 'armor'
		right_click_action = 'right_click_action'
		ready_sound = 'ready_sound'
		what_sound_start = 'what_sound_start'
		what_sound_end = 'what_sound_end'
		pissed_sound_start = 'pissed_sound_start'
		pissed_sound_end = 'pissed_sound_end'
		yes_sound_start = 'yes_sound_start'
		yes_sound_end = 'yes_sound_end'
		staredit_placement_size = 'staredit_placement_size'
		addon_position = 'addon_position'
		unit_extents = 'unit_extents'
		portrait = 'portrait'
		mineral_cost = 'mineral_cost'
		vespene_cost = 'vespene_cost'
		build_time = 'build_time'
		requirements = 'requirements'
		staredit_group_flags = 'staredit_group_flags'
		supply_provided = 'supply_provided'
		supply_required = 'supply_required'
		space_required = 'space_required'
		space_provided = 'space_provided'
		build_score = 'build_score'
		destroy_score = 'destroy_score'
		unit_map_string = 'unit_map_string'
		broodwar_unit_flag = 'broodwar_unit_flag'
		staredit_availability_flags = 'staredit_availability_flags'

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
		self.requirements = 65535
		self.staredit_group_flags = 0
		self.supply_provided = DATFormat.DATTypeSupply()
		self.supply_required = DATFormat.DATTypeSupply()
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

	def limit(self, id):
		self.infestation = None
		self.ready_sound = None
		self.pissed_sound_start = None
		self.pissed_sound_end = None
		self.yes_sound_start = None
		self.yes_sound_end = None
		self.addon_position = None

	def expand(self):
		self.infestation = self.infestation or 0
		self.ready_sound = self.ready_sound or 0
		self.pissed_sound_start = self.pissed_sound_start or 0
		self.pissed_sound_end = self.pissed_sound_end or 0
		self.yes_sound_start = self.yes_sound_start or 0
		self.yes_sound_end = self.yes_sound_end or 0
		self.addon_position = self.addon_position or DATFormat.DATTypePosition()

	EXPORT_NAME = 'Unit'
	def _export_data(self, export_properties, data):
		self._export_property_value(export_properties, Unit.Property.graphics, self.graphics, data)
		self._export_property_value(export_properties, Unit.Property.subunit1, self.subunit1, data)
		self._export_property_value(export_properties, Unit.Property.subunit2, self.subunit2, data)
		self._export_property_value(export_properties, Unit.Property.infestation, self.infestation, data)
		self._export_property_value(export_properties, Unit.Property.construction_animation, self.construction_animation, data)
		self._export_property_value(export_properties, Unit.Property.unit_direction, self.unit_direction, data)
		self._export_property_value(export_properties, Unit.Property.shield_enabled, self.shield_enabled, data)
		self._export_property_value(export_properties, Unit.Property.shield_amount, self.shield_amount, data)
		self._export_property_value(export_properties, Unit.Property.hit_points, self.hit_points, data, _UnitPropertyCoder.hit_points)
		self._export_property_value(export_properties, Unit.Property.elevation_level, self.elevation_level, data)
		self._export_property_value(export_properties, Unit.Property.unknown_flags, self.unknown_flags, data, _UnitPropertyCoder.unknown_flags)
		self._export_property_value(export_properties, Unit.Property.sublabel, self.sublabel, data)
		self._export_property_value(export_properties, Unit.Property.comp_ai_idle, self.comp_ai_idle, data)
		self._export_property_value(export_properties, Unit.Property.human_ai_idle, self.human_ai_idle, data)
		self._export_property_value(export_properties, Unit.Property.return_to_idle, self.return_to_idle, data)
		self._export_property_value(export_properties, Unit.Property.attack_unit, self.attack_unit, data)
		self._export_property_value(export_properties, Unit.Property.attack_move, self.attack_move, data)
		self._export_property_value(export_properties, Unit.Property.ground_weapon, self.ground_weapon, data)
		self._export_property_value(export_properties, Unit.Property.max_ground_hits, self.max_ground_hits, data)
		self._export_property_value(export_properties, Unit.Property.air_weapon, self.air_weapon, data)
		self._export_property_value(export_properties, Unit.Property.max_air_hits, self.max_air_hits, data)
		self._export_property_value(export_properties, Unit.Property.ai_internal, self.ai_internal, data)
		self._export_property_value(export_properties, Unit.Property.special_ability_flags, self.special_ability_flags, data, _UnitPropertyCoder.special_ability_flags)
		self._export_property_value(export_properties, Unit.Property.target_acquisition_range, self.target_acquisition_range, data)
		self._export_property_value(export_properties, Unit.Property.sight_range, self.sight_range, data)
		self._export_property_value(export_properties, Unit.Property.armor_upgrade, self.armor_upgrade, data)
		self._export_property_value(export_properties, Unit.Property.unit_size, self.unit_size, data)
		self._export_property_value(export_properties, Unit.Property.armor, self.armor, data)
		self._export_property_value(export_properties, Unit.Property.right_click_action, self.right_click_action, data)
		self._export_property_value(export_properties, Unit.Property.ready_sound, self.ready_sound, data)
		self._export_property_value(export_properties, Unit.Property.what_sound_start, self.what_sound_start, data)
		self._export_property_value(export_properties, Unit.Property.what_sound_end, self.what_sound_end, data)
		self._export_property_value(export_properties, Unit.Property.pissed_sound_start, self.pissed_sound_start, data)
		self._export_property_value(export_properties, Unit.Property.pissed_sound_end, self.pissed_sound_end, data)
		self._export_property_value(export_properties, Unit.Property.yes_sound_start, self.yes_sound_start, data)
		self._export_property_value(export_properties, Unit.Property.yes_sound_end, self.yes_sound_end, data)
		self._export_property_value(export_properties, Unit.Property.staredit_placement_size, self.staredit_placement_size, data, _UnitPropertyCoder.staredit_placement_size)
		self._export_property_value(export_properties, Unit.Property.addon_position, self.addon_position, data, _UnitPropertyCoder.addon_position)
		self._export_property_value(export_properties, Unit.Property.unit_extents, self.unit_extents, data, _UnitPropertyCoder.unit_extents)
		self._export_property_value(export_properties, Unit.Property.portrait, self.portrait, data)
		self._export_property_value(export_properties, Unit.Property.mineral_cost, self.mineral_cost, data)
		self._export_property_value(export_properties, Unit.Property.vespene_cost, self.vespene_cost, data)
		self._export_property_value(export_properties, Unit.Property.build_time, self.build_time, data)
		self._export_property_value(export_properties, Unit.Property.requirements, self.requirements, data)
		self._export_property_value(export_properties, Unit.Property.staredit_group_flags, self.staredit_group_flags, data, _UnitPropertyCoder.staredit_group_flags)
		self._export_property_value(export_properties, Unit.Property.supply_provided, self.supply_provided, data, _UnitPropertyCoder.supply_provided)
		self._export_property_value(export_properties, Unit.Property.supply_required, self.supply_required, data, _UnitPropertyCoder.supply_required)
		self._export_property_value(export_properties, Unit.Property.space_required, self.space_required, data)
		self._export_property_value(export_properties, Unit.Property.space_provided, self.space_provided, data)
		self._export_property_value(export_properties, Unit.Property.build_score, self.build_score, data)
		self._export_property_value(export_properties, Unit.Property.destroy_score, self.destroy_score, data)
		self._export_property_value(export_properties, Unit.Property.unit_map_string, self.unit_map_string, data)
		self._export_property_value(export_properties, Unit.Property.broodwar_unit_flag, self.broodwar_unit_flag, data)
		self._export_property_value(export_properties, Unit.Property.staredit_availability_flags, self.staredit_availability_flags, data, _UnitPropertyCoder.staredit_availability_flags)

	def _import_data(self, data):
		graphics = self._import_property_value(data, Unit.Property.graphics)
		subunit1 = self._import_property_value(data, Unit.Property.subunit1)
		subunit2 = self._import_property_value(data, Unit.Property.subunit2)
		infestation = self._import_property_value(data, Unit.Property.infestation, allowed=(self.infestation != None))
		construction_animation = self._import_property_value(data, Unit.Property.construction_animation)
		unit_direction = self._import_property_value(data, Unit.Property.unit_direction)
		shield_enabled = self._import_property_value(data, Unit.Property.shield_enabled)
		shield_amount = self._import_property_value(data, Unit.Property.shield_amount)
		hit_points = self._import_property_value(data, Unit.Property.hit_points, _UnitPropertyCoder.hit_points)
		elevation_level = self._import_property_value(data, Unit.Property.elevation_level)
		unknown_flags = self._import_property_value(data, Unit.Property.unknown_flags, _UnitPropertyCoder.unknown_flags)
		sublabel = self._import_property_value(data, Unit.Property.sublabel)
		comp_ai_idle = self._import_property_value(data, Unit.Property.comp_ai_idle)
		human_ai_idle = self._import_property_value(data, Unit.Property.human_ai_idle)
		return_to_idle = self._import_property_value(data, Unit.Property.return_to_idle)
		attack_unit = self._import_property_value(data, Unit.Property.attack_unit)
		attack_move = self._import_property_value(data, Unit.Property.attack_move)
		ground_weapon = self._import_property_value(data, Unit.Property.ground_weapon)
		max_ground_hits = self._import_property_value(data, Unit.Property.max_ground_hits)
		air_weapon = self._import_property_value(data, Unit.Property.air_weapon)
		max_air_hits = self._import_property_value(data, Unit.Property.max_air_hits)
		ai_internal = self._import_property_value(data, Unit.Property.ai_internal)
		special_ability_flags = self._import_property_value(data, Unit.Property.special_ability_flags, _UnitPropertyCoder.special_ability_flags)
		target_acquisition_range = self._import_property_value(data, Unit.Property.target_acquisition_range)
		sight_range = self._import_property_value(data, Unit.Property.sight_range)
		armor_upgrade = self._import_property_value(data, Unit.Property.armor_upgrade)
		unit_size = self._import_property_value(data, Unit.Property.unit_size)
		armor = self._import_property_value(data, Unit.Property.armor)
		right_click_action = self._import_property_value(data, Unit.Property.right_click_action)
		ready_sound = self._import_property_value(data, Unit.Property.ready_sound, allowed=(self.ready_sound != None))
		what_sound_start = self._import_property_value(data, Unit.Property.what_sound_start)
		what_sound_end = self._import_property_value(data, Unit.Property.what_sound_end)
		pissed_sound_start = self._import_property_value(data, Unit.Property.pissed_sound_start, allowed=(self.pissed_sound_start != None))
		pissed_sound_end = self._import_property_value(data, Unit.Property.pissed_sound_end, allowed=(self.pissed_sound_end != None))
		yes_sound_start = self._import_property_value(data, Unit.Property.yes_sound_start, allowed=(self.yes_sound_start != None))
		yes_sound_end = self._import_property_value(data, Unit.Property.yes_sound_end, allowed=(self.yes_sound_end != None))
		staredit_placement_size = self._import_property_value(data, Unit.Property.staredit_placement_size, _UnitPropertyCoder.staredit_placement_size)
		addon_position = self._import_property_value(data, Unit.Property.addon_position, _UnitPropertyCoder.addon_position, allowed=(self.addon_position != None))
		unit_extents = self._import_property_value(data, Unit.Property.unit_extents, _UnitPropertyCoder.unit_extents)
		portrait = self._import_property_value(data, Unit.Property.portrait)
		mineral_cost = self._import_property_value(data, Unit.Property.mineral_cost)
		vespene_cost = self._import_property_value(data, Unit.Property.vespene_cost)
		build_time = self._import_property_value(data, Unit.Property.build_time)
		requirements = self._import_property_value(data, Unit.Property.requirements)
		staredit_group_flags = self._import_property_value(data, Unit.Property.staredit_group_flags, _UnitPropertyCoder.staredit_group_flags)
		supply_provided = self._import_property_value(data, Unit.Property.supply_provided, _UnitPropertyCoder.supply_provided)
		supply_required = self._import_property_value(data, Unit.Property.supply_required, _UnitPropertyCoder.supply_required)
		space_required = self._import_property_value(data, Unit.Property.space_required)
		space_provided = self._import_property_value(data, Unit.Property.space_provided)
		build_score = self._import_property_value(data, Unit.Property.build_score)
		destroy_score = self._import_property_value(data, Unit.Property.destroy_score)
		unit_map_string = self._import_property_value(data, Unit.Property.unit_map_string)
		broodwar_unit_flag = self._import_property_value(data, Unit.Property.broodwar_unit_flag)
		staredit_availability_flags = self._import_property_value(data, Unit.Property.staredit_availability_flags, _UnitPropertyCoder.staredit_availability_flags)

		if graphics != None:
			self.graphics = graphics
		if subunit1 != None:
			self.subunit1 = subunit1
		if subunit2 != None:
			self.subunit2 = subunit2
		if infestation != None:
			self.infestation = infestation
		if construction_animation != None:
			self.construction_animation = construction_animation
		if unit_direction != None:
			self.unit_direction = unit_direction
		if shield_enabled != None:
			self.shield_enabled = shield_enabled
		if shield_amount != None:
			self.shield_amount = shield_amount
		if hit_points != None:
			self.hit_points = hit_points
		if elevation_level != None:
			self.elevation_level = elevation_level
		if unknown_flags != None:
			self.unknown_flags = unknown_flags
		if sublabel != None:
			self.sublabel = sublabel
		if comp_ai_idle != None:
			self.comp_ai_idle = comp_ai_idle
		if human_ai_idle != None:
			self.human_ai_idle = human_ai_idle
		if return_to_idle != None:
			self.return_to_idle = return_to_idle
		if attack_unit != None:
			self.attack_unit = attack_unit
		if attack_move != None:
			self.attack_move = attack_move
		if ground_weapon != None:
			self.ground_weapon = ground_weapon
		if max_ground_hits != None:
			self.max_ground_hits = max_ground_hits
		if air_weapon != None:
			self.air_weapon = air_weapon
		if max_air_hits != None:
			self.max_air_hits = max_air_hits
		if ai_internal != None:
			self.ai_internal = ai_internal
		if special_ability_flags != None:
			self.special_ability_flags = special_ability_flags
		if target_acquisition_range != None:
			self.target_acquisition_range = target_acquisition_range
		if sight_range != None:
			self.sight_range = sight_range
		if armor_upgrade != None:
			self.armor_upgrade = armor_upgrade
		if unit_size != None:
			self.unit_size = unit_size
		if armor != None:
			self.armor = armor
		if right_click_action != None:
			self.right_click_action = right_click_action
		if ready_sound != None:
			self.ready_sound = ready_sound
		if what_sound_start != None:
			self.what_sound_start = what_sound_start
		if what_sound_end != None:
			self.what_sound_end = what_sound_end
		if pissed_sound_start != None:
			self.pissed_sound_start = pissed_sound_start
		if pissed_sound_end != None:
			self.pissed_sound_end = pissed_sound_end
		if yes_sound_start != None:
			self.yes_sound_start = yes_sound_start
		if yes_sound_end != None:
			self.yes_sound_end = yes_sound_end
		if staredit_placement_size != None:
			self.staredit_placement_size = staredit_placement_size
		if addon_position != None:
			self.addon_position = addon_position
		if unit_extents != None:
			self.unit_extents = unit_extents
		if portrait != None:
			self.portrait = portrait
		if mineral_cost != None:
			self.mineral_cost = mineral_cost
		if vespene_cost != None:
			self.vespene_cost = vespene_cost
		if build_time != None:
			self.build_time = build_time
		if requirements != None:
			self.requirements = requirements
		if staredit_group_flags != None:
			self.staredit_group_flags = staredit_group_flags
		if supply_provided != None:
			self.supply_provided = supply_provided
		if supply_required != None:
			self.supply_required = supply_required
		if space_required != None:
			self.space_required = space_required
		if space_provided != None:
			self.space_provided = space_provided
		if build_score != None:
			self.build_score = build_score
		if destroy_score != None:
			self.destroy_score = destroy_score
		if unit_map_string != None:
			self.unit_map_string = unit_map_string
		if broodwar_unit_flag != None:
			self.broodwar_unit_flag = broodwar_unit_flag
		if staredit_availability_flags != None:
			self.staredit_availability_flags = staredit_availability_flags


class _UnitPropertyCoder:
	hit_points = DATCoders.DATHitPointsCoder()
	unknown_flags = DATCoders.DATFlagsCoder(8, {})
	special_ability_flags = DATCoders.DATFlagsCoder(32, {
		Unit.SpecialAbilityFlag.building: 'building',
		Unit.SpecialAbilityFlag.addon: 'addon',
		Unit.SpecialAbilityFlag.flyer: 'flyer',
		Unit.SpecialAbilityFlag.resource_miner: 'resource_miner',
		Unit.SpecialAbilityFlag.subunit: 'subunit',
		Unit.SpecialAbilityFlag.flying_building: 'flying_building',
		Unit.SpecialAbilityFlag.hero: 'hero',
		Unit.SpecialAbilityFlag.regenerate: 'regenerate',
		Unit.SpecialAbilityFlag.animated_idle: 'animated_idle',
		Unit.SpecialAbilityFlag.cloakable: 'cloakable',
		Unit.SpecialAbilityFlag.two_units_in_one_egg: 'two_units_in_one_egg',
		Unit.SpecialAbilityFlag.single_entity: 'single_entity',
		Unit.SpecialAbilityFlag.resource_depot: 'resource_depot',
		Unit.SpecialAbilityFlag.resource_container: 'resource_container',
		Unit.SpecialAbilityFlag.robotic: 'robotic',
		Unit.SpecialAbilityFlag.detector: 'detector',
		Unit.SpecialAbilityFlag.organic: 'organic',
		Unit.SpecialAbilityFlag.requires_creep: 'requires_creep',
		Unit.SpecialAbilityFlag.unused: 'unused',
		Unit.SpecialAbilityFlag.requires_psi: 'requires_psi',
		Unit.SpecialAbilityFlag.burrowable: 'burrowable',
		Unit.SpecialAbilityFlag.spellcaster: 'spellcaster',
		Unit.SpecialAbilityFlag.permanent_cloak: 'permanent_cloak',
		Unit.SpecialAbilityFlag.pickup_item: 'pickup_item',
		Unit.SpecialAbilityFlag.ignores_supply_check: 'ignores_supply_check',
		Unit.SpecialAbilityFlag.use_medium_overlays: 'use_medium_overlays',
		Unit.SpecialAbilityFlag.use_large_overlays: 'use_large_overlays',
		Unit.SpecialAbilityFlag.battle_reactions: 'battle_reactions',
		Unit.SpecialAbilityFlag.full_auto_attack: 'full_auto_attack',
		Unit.SpecialAbilityFlag.invincible: 'invincible',
		Unit.SpecialAbilityFlag.mechanical: 'mechanical',
		Unit.SpecialAbilityFlag.produces_units: 'produces_units',
	})
	staredit_placement_size = DATCoders.DATSizeCoder()
	addon_position = DATCoders.DATPositionCoder()
	unit_extents = DATCoders.DATExtentsCoder()
	staredit_group_flags = DATCoders.DATFlagsCoder(8, {
		Unit.StarEditGroupFlag.zerg: 'zerg',
		Unit.StarEditGroupFlag.terran: 'terran',
		Unit.StarEditGroupFlag.protoss: 'protoss',
		Unit.StarEditGroupFlag.men: 'men',
		Unit.StarEditGroupFlag.building: 'building',
		Unit.StarEditGroupFlag.factory: 'factory',
		Unit.StarEditGroupFlag.independent: 'independent',
		Unit.StarEditGroupFlag.neutral: 'neutral',
	})
	supply_provided = DATCoders.DATSupplyCoder()
	supply_required = DATCoders.DATSupplyCoder()
	staredit_availability_flags = DATCoders.DATFlagsCoder(10, {
		Unit.StarEditAvailabilityFlag.non_neutral: 'non_neutral',
		Unit.StarEditAvailabilityFlag.unit_listing: 'unit_listing',
		Unit.StarEditAvailabilityFlag.mission_briefing: 'mission_briefing',
		Unit.StarEditAvailabilityFlag.player_settings: 'player_settings',
		Unit.StarEditAvailabilityFlag.all_races: 'all_races',
		Unit.StarEditAvailabilityFlag.set_doodad_state: 'set_doodad_state',
		Unit.StarEditAvailabilityFlag.non_location_triggers: 'non_location_triggers',
		Unit.StarEditAvailabilityFlag.unit_hero_settings: 'unit_hero_settings',
		Unit.StarEditAvailabilityFlag.location_triggers: 'location_triggers',
		Unit.StarEditAvailabilityFlag.broodwar_only: 'broodwar_only',
	})

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
					"name": "graphics", # Pointer to flingy.dat
					"type": "byte",
					"expanded_type": "short"
				},
				{
					"name": "subunit1", # Pointer to units.dat
					"type": "short"
				},
				{
					"name": "subunit2", # Pointer to units.dat
					"type": "short"
				},
				{
					"name": "infestation", # Pointer to units.dat
					"type": "short",
					"entry_offset": 106,
					"entry_count": 96
				},
				{
					"name": "construction_animation", # Pointer to images.dat
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
					"name": "sublabel", # Pointer to stat_txt.tbl
					"type": "byte"
				},
				{
					"name": "comp_ai_idle", # Pointer to orders.dat
					"type": "byte"
				},
				{
					"name": "human_ai_idle", # Pointer to orders.dat
					"type": "byte"
				},
				{
					"name": "return_to_idle", # Pointer to orders.dat
					"type": "byte"
				},
				{
					"name": "attack_unit", # Pointer to orders.dat
					"type": "byte"
				},
				{
					"name": "attack_move", # Pointer to orders.dat
					"type": "byte"
				},
				{
					"name": "ground_weapon", # Pointer to weapons.dat
					"type": "byte"
				},
				{
					"name": "max_ground_hits",
					"type": "byte"
				},
				{
					"name": "air_weapon", # Pointer to weapons.dat
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
					"name": "armor_upgrade", # Pointer to upgrades.dat
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
					"name": "ready_sound", # Pointer to sfxdata.dat
					"type": "short",
					"entry_offset": 0,
					"entry_count": 106
				},
				{
					"name": "what_sound_start", # Pointer to sfxdata.dat
					"type": "short"
				},
				{
					"name": "what_sound_end", # Pointer to sfxdata.dat
					"type": "short"
				},
				{
					"name": "pissed_sound_start", # Pointer to sfxdata.dat
					"type": "short",
					"entry_offset": 0,
					"entry_count": 106
				},
				{
					"name": "pissed_sound_end", # Pointer to sfxdata.dat
					"type": "short",
					"entry_offset": 0,
					"entry_count": 106
				},
				{
					"name": "yes_sound_start", # Pointer to sfxdata.dat
					"type": "short",
					"entry_offset": 0,
					"entry_count": 106
				},
				{
					"name": "yes_sound_end", # Pointer to sfxdata.dat
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
					"name": "portrait", # Pointer to portdata.dat
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
					"type": "supply"
				},
				{
					"name": "supply_required",
					"type": "supply"
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

	def get_entry(self, index): # type: (int) -> Unit
		return super(UnitsDAT, self).get_entry(index)
