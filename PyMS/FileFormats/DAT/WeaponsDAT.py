
from . import AbstractDAT
from . import DATFormat
from . import DATCoders

from typing import cast

class DATWeapon(AbstractDAT.AbstractDATEntry):
	class Property:
		label = 'label'
		graphics = 'graphics'
		unused_technology = 'unused_technology'
		target_flags = 'target_flags'
		minimum_range = 'minimum_range'
		maximum_range = 'maximum_range'
		damage_upgrade = 'damage_upgrade'
		weapon_type = 'weapon_type'
		weapon_behavior = 'weapon_behavior'
		remove_after = 'remove_after'
		explosion_type = 'explosion_type'
		inner_splash_range = 'inner_splash_range'
		medium_splash_range = 'medium_splash_range'
		outer_splash_range = 'outer_splash_range'
		damage_amount = 'damage_amount'
		damage_bonus = 'damage_bonus'
		weapon_cooldown = 'weapon_cooldown'
		damage_factor = 'damage_factor'
		attack_angle = 'attack_angle'
		launch_spin = 'launch_spin'
		forward_offset = 'forward_offset'
		upward_offset = 'upward_offset'
		target_error_message = 'target_error_message'
		icon = 'icon'

	class TargetFlag:
		air                   = 1 << 0
		ground                = 1 << 1
		mechanical            = 1 << 2
		organic               = 1 << 3
		non_building          = 1 << 4
		non_robotic           = 1 << 5
		terrain               = 1 << 6
		organic_or_mechanical = 1 << 7
		own                   = 1 << 8
		ALL_FLAGS             = (air | ground | mechanical | organic | non_building | non_robotic | terrain | organic_or_mechanical | own)

	def __init__(self):
		self.label = 0
		self.graphics = 0
		self.unused_technology = 0
		self.target_flags = 0
		self.minimum_range = 0
		self.maximum_range = 0
		self.damage_upgrade = 0
		self.weapon_type = 0
		self.weapon_behavior = 0
		self.remove_after = 0
		self.explosion_type = 0
		self.inner_splash_range = 0
		self.medium_splash_range = 0
		self.outer_splash_range = 0
		self.damage_amount = 0
		self.damage_bonus = 0
		self.weapon_cooldown = 0
		self.damage_factor = 0
		self.attack_angle = 0
		self.launch_spin = 0
		self.forward_offset = 0
		self.upward_offset = 0
		self.target_error_message = 0
		self.icon = 0

	def load_values(self, values):
		self.label,\
		self.graphics,\
		self.unused_technology,\
		self.target_flags,\
		self.minimum_range,\
		self.maximum_range,\
		self.damage_upgrade,\
		self.weapon_type,\
		self.weapon_behavior,\
		self.remove_after,\
		self.explosion_type,\
		self.inner_splash_range,\
		self.medium_splash_range,\
		self.outer_splash_range,\
		self.damage_amount,\
		self.damage_bonus,\
		self.weapon_cooldown,\
		self.damage_factor,\
		self.attack_angle,\
		self.launch_spin,\
		self.forward_offset,\
		self.upward_offset,\
		self.target_error_message,\
		self.icon\
			= values

	def save_values(self):
		return (
			self.label,
			self.graphics,
			self.unused_technology,
			self.target_flags,
			self.minimum_range,
			self.maximum_range,
			self.damage_upgrade,
			self.weapon_type,
			self.weapon_behavior,
			self.remove_after,
			self.explosion_type,
			self.inner_splash_range,
			self.medium_splash_range,
			self.outer_splash_range,
			self.damage_amount,
			self.damage_bonus,
			self.weapon_cooldown,
			self.damage_factor,
			self.attack_angle,
			self.launch_spin,
			self.forward_offset,
			self.upward_offset,
			self.target_error_message,
			self.icon
		)

	EXPORT_NAME = 'Weapon'
	def _export_data(self, export_properties, data):
		self._export_property_value(export_properties, DATWeapon.Property.label, self.label, data)
		self._export_property_value(export_properties, DATWeapon.Property.graphics, self.graphics, data)
		self._export_property_value(export_properties, DATWeapon.Property.unused_technology, self.unused_technology, data)
		self._export_property_value(export_properties, DATWeapon.Property.target_flags, self.target_flags, data, _WeaponPropertyCoder.target_flags)
		self._export_property_value(export_properties, DATWeapon.Property.minimum_range, self.minimum_range, data)
		self._export_property_value(export_properties, DATWeapon.Property.maximum_range, self.maximum_range, data)
		self._export_property_value(export_properties, DATWeapon.Property.damage_upgrade, self.damage_upgrade, data)
		self._export_property_value(export_properties, DATWeapon.Property.weapon_type, self.weapon_type, data)
		self._export_property_value(export_properties, DATWeapon.Property.weapon_behavior, self.weapon_behavior, data)
		self._export_property_value(export_properties, DATWeapon.Property.remove_after, self.remove_after, data)
		self._export_property_value(export_properties, DATWeapon.Property.explosion_type, self.explosion_type, data)
		self._export_property_value(export_properties, DATWeapon.Property.inner_splash_range, self.inner_splash_range, data)
		self._export_property_value(export_properties, DATWeapon.Property.medium_splash_range, self.medium_splash_range, data)
		self._export_property_value(export_properties, DATWeapon.Property.outer_splash_range, self.outer_splash_range, data)
		self._export_property_value(export_properties, DATWeapon.Property.damage_amount, self.damage_amount, data)
		self._export_property_value(export_properties, DATWeapon.Property.damage_bonus, self.damage_bonus, data)
		self._export_property_value(export_properties, DATWeapon.Property.weapon_cooldown, self.weapon_cooldown, data)
		self._export_property_value(export_properties, DATWeapon.Property.damage_factor, self.damage_factor, data)
		self._export_property_value(export_properties, DATWeapon.Property.attack_angle, self.attack_angle, data)
		self._export_property_value(export_properties, DATWeapon.Property.launch_spin, self.launch_spin, data)
		self._export_property_value(export_properties, DATWeapon.Property.forward_offset, self.forward_offset, data)
		self._export_property_value(export_properties, DATWeapon.Property.upward_offset, self.upward_offset, data)
		self._export_property_value(export_properties, DATWeapon.Property.target_error_message, self.target_error_message, data)
		self._export_property_value(export_properties, DATWeapon.Property.icon, self.icon, data)

	def _import_data(self, data):
		label = self._import_property_value(data, DATWeapon.Property.label)
		graphics = self._import_property_value(data, DATWeapon.Property.graphics)
		unused_technology = self._import_property_value(data, DATWeapon.Property.unused_technology)
		target_flags = self._import_property_value(data, DATWeapon.Property.target_flags, _WeaponPropertyCoder.target_flags)
		minimum_range = self._import_property_value(data, DATWeapon.Property.minimum_range)
		maximum_range = self._import_property_value(data, DATWeapon.Property.maximum_range)
		damage_upgrade = self._import_property_value(data, DATWeapon.Property.damage_upgrade)
		weapon_type = self._import_property_value(data, DATWeapon.Property.weapon_type)
		weapon_behavior = self._import_property_value(data, DATWeapon.Property.weapon_behavior)
		remove_after = self._import_property_value(data, DATWeapon.Property.remove_after)
		explosion_type = self._import_property_value(data, DATWeapon.Property.explosion_type)
		inner_splash_range = self._import_property_value(data, DATWeapon.Property.inner_splash_range)
		medium_splash_range = self._import_property_value(data, DATWeapon.Property.medium_splash_range)
		outer_splash_range = self._import_property_value(data, DATWeapon.Property.outer_splash_range)
		damage_amount = self._import_property_value(data, DATWeapon.Property.damage_amount)
		damage_bonus = self._import_property_value(data, DATWeapon.Property.damage_bonus)
		weapon_cooldown = self._import_property_value(data, DATWeapon.Property.weapon_cooldown)
		damage_factor = self._import_property_value(data, DATWeapon.Property.damage_factor)
		attack_angle = self._import_property_value(data, DATWeapon.Property.attack_angle)
		launch_spin = self._import_property_value(data, DATWeapon.Property.launch_spin)
		forward_offset = self._import_property_value(data, DATWeapon.Property.forward_offset)
		upward_offset = self._import_property_value(data, DATWeapon.Property.upward_offset)
		target_error_message = self._import_property_value(data, DATWeapon.Property.target_error_message)
		icon = self._import_property_value(data, DATWeapon.Property.icon)

		if label is not None:
			self.label = label
		if graphics is not None:
			self.graphics = graphics
		if unused_technology is not None:
			self.unused_technology = unused_technology
		if target_flags is not None:
			self.target_flags = target_flags
		if minimum_range is not None:
			self.minimum_range = minimum_range
		if maximum_range is not None:
			self.maximum_range = maximum_range
		if damage_upgrade is not None:
			self.damage_upgrade = damage_upgrade
		if weapon_type is not None:
			self.weapon_type = weapon_type
		if weapon_behavior is not None:
			self.weapon_behavior = weapon_behavior
		if remove_after is not None:
			self.remove_after = remove_after
		if explosion_type is not None:
			self.explosion_type = explosion_type
		if inner_splash_range is not None:
			self.inner_splash_range = inner_splash_range
		if medium_splash_range is not None:
			self.medium_splash_range = medium_splash_range
		if outer_splash_range is not None:
			self.outer_splash_range = outer_splash_range
		if damage_amount is not None:
			self.damage_amount = damage_amount
		if damage_bonus is not None:
			self.damage_bonus = damage_bonus
		if weapon_cooldown is not None:
			self.weapon_cooldown = weapon_cooldown
		if damage_factor is not None:
			self.damage_factor = damage_factor
		if attack_angle is not None:
			self.attack_angle = attack_angle
		if launch_spin is not None:
			self.launch_spin = launch_spin
		if forward_offset is not None:
			self.forward_offset = forward_offset
		if upward_offset is not None:
			self.upward_offset = upward_offset
		if target_error_message is not None:
			self.target_error_message = target_error_message
		if icon is not None:
			self.icon = icon

class _WeaponPropertyCoder:
	target_flags = DATCoders.DATFlagsCoder(9, {
		DATWeapon.TargetFlag.air: 'air',
		DATWeapon.TargetFlag.ground: 'ground',
		DATWeapon.TargetFlag.mechanical: 'mechanical',
		DATWeapon.TargetFlag.organic: 'organic',
		DATWeapon.TargetFlag.non_building: 'non_building',
		DATWeapon.TargetFlag.non_robotic: 'non_robotic',
		DATWeapon.TargetFlag.terrain: 'terrain',
		DATWeapon.TargetFlag.organic_or_mechanical: 'organic_or_mechanical',
		DATWeapon.TargetFlag.own: 'own',
	})

# weapons.dat file handler
class WeaponsDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 130,
			"expanded_max_entries": 255,
			"properties": [
				{
					"name": "label", # Pointer to stat_txt.tbl
					"type": "short"
				},
				{
					"name": "graphics", # Pointer to flingy.dat
					"type": "long"
				},
				{
					"name": "unused_technology", # Pointer to techdata.dat
					"type": "byte"
				},
				{
					"name": "target_flags",
					"type": "short"
				},
				{
					"name": "minimum_range",
					"type": "long"
				},
				{
					"name": "maximum_range",
					"type": "long"
				},
				{
					"name": "damage_upgrade", # Pointer to upgrades.dat
					"type": "byte"
				},
				{
					"name": "weapon_type",
					"type": "byte"
				},
				{
					"name": "weapon_behavior",
					"type": "byte"
				},
				{
					"name": "remove_after",
					"type": "byte"
				},
				{
					"name": "explosion_type",
					"type": "byte"
				},
				{
					"name": "inner_splash_range",
					"type": "short"
				},
				{
					"name": "medium_splash_range",
					"type": "short"
				},
				{
					"name": "outer_splash_range",
					"type": "short"
				},
				{
					"name": "damage_amount",
					"type": "short"
				},
				{
					"name": "damage_bonus",
					"type": "short"
				},
				{
					"name": "weapon_cooldown",
					"type": "byte"
				},
				{
					"name": "damage_factor",
					"type": "byte"
				},
				{
					"name": "attack_angle",
					"type": "byte"
				},
				{
					"name": "launch_spin",
					"type": "byte"
				},
				{
					"name": "forward_offset",
					"type": "byte"
				},
				{
					"name": "upward_offset",
					"type": "byte"
				},
				{
					"name": "target_error_message", # Pointer to stat_txt.tbl
					"type": "short"
				},
				{
					"name": "icon", # Pointer to cmdicon.grp
					"type": "short"
				}
			]
		})
	ENTRY_STRUCT = DATWeapon
	FILE_NAME = "weapons.dat"

	def get_entry(self, index): # type: (int) -> DATWeapon
		return cast(DATWeapon, super(WeaponsDAT, self).get_entry(index))
