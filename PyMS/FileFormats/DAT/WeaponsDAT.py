
import AbstractDAT
import DATFormat

from collections import OrderedDict
import json

class Weapon(AbstractDAT.AbstractDATEntry):
	def __init__(self):
		self.label = 0
		self.graphics = 0
		self.unused = 0
		self.target_flags = 0
		self.minimum_range = 0
		self.maximum_range = 0
		self.damage_upgrade = 0
		self.weapon_type = 0
		self.weapon_behavior = 0
		self.remove_after = 0
		self.explosion_type = 0
		self.inner_splash_range = 0
		self.medium_spash_range = 0
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
		self.unused,\
		self.target_flags,\
		self.minimum_range,\
		self.maximum_range,\
		self.damage_upgrade,\
		self.weapon_type,\
		self.weapon_behavior,\
		self.remove_after,\
		self.explosion_type,\
		self.inner_splash_range,\
		self.medium_spash_range,\
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
			self.unused,
			self.target_flags,
			self.minimum_range,
			self.maximum_range,
			self.damage_upgrade,
			self.weapon_type,
			self.weapon_behavior,
			self.remove_after,
			self.explosion_type,
			self.inner_splash_range,
			self.medium_spash_range,
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

	def expand(self):
		self.label = self.label or 0
		self.graphics = self.graphics or 0
		self.unused = self.unused or 0
		self.target_flags = self.target_flags or 0
		self.minimum_range = self.minimum_range or 0
		self.maximum_range = self.maximum_range or 0
		self.damage_upgrade = self.damage_upgrade or 0
		self.weapon_type = self.weapon_type or 0
		self.weapon_behavior = self.weapon_behavior or 0
		self.remove_after = self.remove_after or 0
		self.explosion_type = self.explosion_type or 0
		self.inner_splash_range = self.inner_splash_range or 0
		self.medium_spash_range = self.medium_spash_range or 0
		self.outer_splash_range = self.outer_splash_range or 0
		self.damage_amount = self.damage_amount or 0
		self.damage_bonus = self.damage_bonus or 0
		self.weapon_cooldown = self.weapon_cooldown or 0
		self.damage_factor = self.damage_factor or 0
		self.attack_angle = self.attack_angle or 0
		self.launch_spin = self.launch_spin or 0
		self.forward_offset = self.forward_offset or 0
		self.upward_offset = self.upward_offset or 0
		self.target_error_message = self.target_error_message or 0
		self.icon = self.icon or 0

	def export_text(self, id):
		return """Weapon(%d):
	label %d
	graphics %d
	unused %d
	target_flags %d
	minimum_range %d
	maximum_range %d
	damage_upgrade %d
	weapon_type %d
	weapon_behavior %d
	remove_after %d
	explosion_type %d
	inner_splash_range %d
	medium_spash_range %d
	outer_splash_range %d
	damage_amount %d
	damage_bonus %d
	weapon_cooldown %d
	damage_factor %d
	attack_angle %d
	launch_spin %d
	forward_offset %d
	upward_offset %d
	target_error_message %d
	icon %d""" % (
			id,
			self.label,
			self.graphics,
			self.unused,
			self.target_flags,
			self.minimum_range,
			self.maximum_range,
			self.damage_upgrade,
			self.weapon_type,
			self.weapon_behavior,
			self.remove_after,
			self.explosion_type,
			self.inner_splash_range,
			self.medium_spash_range,
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

	def export_json(self, id, dump=True, indent=4):
		data = OrderedDict()
		data["_type"] = "Weapon"
		data["_id"] = id
		data["label"] = self.label
		data["graphics"] = self.graphics
		data["unused"] = self.unused
		data["target_flags"] = self.target_flags
		data["minimum_range"] = self.minimum_range
		data["maximum_range"] = self.maximum_range
		data["damage_upgrade"] = self.damage_upgrade
		data["weapon_type"] = self.weapon_type
		data["weapon_behavior"] = self.weapon_behavior
		data["remove_after"] = self.remove_after
		data["explosion_type"] = self.explosion_type
		data["inner_splash_range"] = self.inner_splash_range
		data["medium_spash_range"] = self.medium_spash_range
		data["outer_splash_range"] = self.outer_splash_range
		data["damage_amount"] = self.damage_amount
		data["damage_bonus"] = self.damage_bonus
		data["weapon_cooldown"] = self.weapon_cooldown
		data["damage_factor"] = self.damage_factor
		data["attack_angle"] = self.attack_angle
		data["launch_spin"] = self.launch_spin
		data["forward_offset"] = self.forward_offset
		data["upward_offset"] = self.upward_offset
		data["target_error_message"] = self.target_error_message
		data["icon"] = self.icon
		if not dump:
			return data
		return json.dumps(data, indent=indent)

# weapons.dat file handler
class WeaponsDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 130,
			"properties": [
				{
					"name": "label",
					"type": "short"
				},
				{
					"name": "graphics",
					"type": "long"
				},
				{
					"name": "unused",
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
					"name": "damage_upgrade",
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
					"name": "medium_spash_range",
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
					"name": "target_error_message",
					"type": "short"
				},
				{
					"name": "icon",
					"type": "short"
				}
			]
		})
	ENTRY_STRUCT = Weapon
	FILE_NAME = "weapons.dat"
