
from . import AbstractDAT
from . import DATFormat
from . import DATCoders

class Weapon(AbstractDAT.AbstractDATEntry):
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
		self._export_property_value(export_properties, Weapon.Property.label, self.label, data)
		self._export_property_value(export_properties, Weapon.Property.graphics, self.graphics, data)
		self._export_property_value(export_properties, Weapon.Property.unused_technology, self.unused_technology, data)
		self._export_property_value(export_properties, Weapon.Property.target_flags, self.target_flags, data, _WeaponPropertyCoder.target_flags)
		self._export_property_value(export_properties, Weapon.Property.minimum_range, self.minimum_range, data)
		self._export_property_value(export_properties, Weapon.Property.maximum_range, self.maximum_range, data)
		self._export_property_value(export_properties, Weapon.Property.damage_upgrade, self.damage_upgrade, data)
		self._export_property_value(export_properties, Weapon.Property.weapon_type, self.weapon_type, data)
		self._export_property_value(export_properties, Weapon.Property.weapon_behavior, self.weapon_behavior, data)
		self._export_property_value(export_properties, Weapon.Property.remove_after, self.remove_after, data)
		self._export_property_value(export_properties, Weapon.Property.explosion_type, self.explosion_type, data)
		self._export_property_value(export_properties, Weapon.Property.inner_splash_range, self.inner_splash_range, data)
		self._export_property_value(export_properties, Weapon.Property.medium_splash_range, self.medium_splash_range, data)
		self._export_property_value(export_properties, Weapon.Property.outer_splash_range, self.outer_splash_range, data)
		self._export_property_value(export_properties, Weapon.Property.damage_amount, self.damage_amount, data)
		self._export_property_value(export_properties, Weapon.Property.damage_bonus, self.damage_bonus, data)
		self._export_property_value(export_properties, Weapon.Property.weapon_cooldown, self.weapon_cooldown, data)
		self._export_property_value(export_properties, Weapon.Property.damage_factor, self.damage_factor, data)
		self._export_property_value(export_properties, Weapon.Property.attack_angle, self.attack_angle, data)
		self._export_property_value(export_properties, Weapon.Property.launch_spin, self.launch_spin, data)
		self._export_property_value(export_properties, Weapon.Property.forward_offset, self.forward_offset, data)
		self._export_property_value(export_properties, Weapon.Property.upward_offset, self.upward_offset, data)
		self._export_property_value(export_properties, Weapon.Property.target_error_message, self.target_error_message, data)
		self._export_property_value(export_properties, Weapon.Property.icon, self.icon, data)

	def _import_data(self, data):
		label = self._import_property_value(data, Weapon.Property.label)
		graphics = self._import_property_value(data, Weapon.Property.graphics)
		unused_technology = self._import_property_value(data, Weapon.Property.unused_technology)
		target_flags = self._import_property_value(data, Weapon.Property.target_flags, _WeaponPropertyCoder.target_flags)
		minimum_range = self._import_property_value(data, Weapon.Property.minimum_range)
		maximum_range = self._import_property_value(data, Weapon.Property.maximum_range)
		damage_upgrade = self._import_property_value(data, Weapon.Property.damage_upgrade)
		weapon_type = self._import_property_value(data, Weapon.Property.weapon_type)
		weapon_behavior = self._import_property_value(data, Weapon.Property.weapon_behavior)
		remove_after = self._import_property_value(data, Weapon.Property.remove_after)
		explosion_type = self._import_property_value(data, Weapon.Property.explosion_type)
		inner_splash_range = self._import_property_value(data, Weapon.Property.inner_splash_range)
		medium_splash_range = self._import_property_value(data, Weapon.Property.medium_splash_range)
		outer_splash_range = self._import_property_value(data, Weapon.Property.outer_splash_range)
		damage_amount = self._import_property_value(data, Weapon.Property.damage_amount)
		damage_bonus = self._import_property_value(data, Weapon.Property.damage_bonus)
		weapon_cooldown = self._import_property_value(data, Weapon.Property.weapon_cooldown)
		damage_factor = self._import_property_value(data, Weapon.Property.damage_factor)
		attack_angle = self._import_property_value(data, Weapon.Property.attack_angle)
		launch_spin = self._import_property_value(data, Weapon.Property.launch_spin)
		forward_offset = self._import_property_value(data, Weapon.Property.forward_offset)
		upward_offset = self._import_property_value(data, Weapon.Property.upward_offset)
		target_error_message = self._import_property_value(data, Weapon.Property.target_error_message)
		icon = self._import_property_value(data, Weapon.Property.icon)

		if label != None:
			self.label = label
		if graphics != None:
			self.graphics = graphics
		if unused_technology != None:
			self.unused_technology = unused_technology
		if target_flags != None:
			self.target_flags = target_flags
		if minimum_range != None:
			self.minimum_range = minimum_range
		if maximum_range != None:
			self.maximum_range = maximum_range
		if damage_upgrade != None:
			self.damage_upgrade = damage_upgrade
		if weapon_type != None:
			self.weapon_type = weapon_type
		if weapon_behavior != None:
			self.weapon_behavior = weapon_behavior
		if remove_after != None:
			self.remove_after = remove_after
		if explosion_type != None:
			self.explosion_type = explosion_type
		if inner_splash_range != None:
			self.inner_splash_range = inner_splash_range
		if medium_splash_range != None:
			self.medium_splash_range = medium_splash_range
		if outer_splash_range != None:
			self.outer_splash_range = outer_splash_range
		if damage_amount != None:
			self.damage_amount = damage_amount
		if damage_bonus != None:
			self.damage_bonus = damage_bonus
		if weapon_cooldown != None:
			self.weapon_cooldown = weapon_cooldown
		if damage_factor != None:
			self.damage_factor = damage_factor
		if attack_angle != None:
			self.attack_angle = attack_angle
		if launch_spin != None:
			self.launch_spin = launch_spin
		if forward_offset != None:
			self.forward_offset = forward_offset
		if upward_offset != None:
			self.upward_offset = upward_offset
		if target_error_message != None:
			self.target_error_message = target_error_message
		if icon != None:
			self.icon = icon

class _WeaponPropertyCoder:
	target_flags = DATCoders.DATFlagsCoder(9, {
		Weapon.TargetFlag.air: 'air',
		Weapon.TargetFlag.ground: 'ground',
		Weapon.TargetFlag.mechanical: 'mechanical',
		Weapon.TargetFlag.organic: 'organic',
		Weapon.TargetFlag.non_building: 'non_building',
		Weapon.TargetFlag.non_robotic: 'non_robotic',
		Weapon.TargetFlag.terrain: 'terrain',
		Weapon.TargetFlag.organic_or_mechanical: 'organic_or_mechanical',
		Weapon.TargetFlag.own: 'own',
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
	ENTRY_STRUCT = Weapon
	FILE_NAME = "weapons.dat"

	def get_entry(self, index): # type: (int) -> Weapon
		return super(WeaponsDAT, self).get_entry(index)
