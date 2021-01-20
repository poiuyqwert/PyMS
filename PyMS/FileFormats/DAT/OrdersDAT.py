
import AbstractDAT
import DATFormat

from collections import OrderedDict
import json

class Order(AbstractDAT.AbstractDATEntry):
	def __init__(self):
		self.label = 0
		self.use_weapon_targeting = 0
		self.unused_is_secondary = 0
		self.unused_allow_non_subunits = 0
		self.changes_subunit_order = 0
		self.unused_allow_subunits = 0
		self.interruptable = 0
		self.waypoint_step_slowdown = 0
		self.queueable = 0
		self.disabled_maintain_air_target = 0
		self.obstructable = 0
		self.flee_unreturnable_damage = 0
		self.unused_requires_movable_unit = 0
		self.weapon_targeting = 0
		self.technology_energy = 0
		self.iscript_animation = 0
		self.highlight_icon = 0
		self.unknown17 = 0
		self.obscured_order = 0

	def load_values(self, values):
		self.label,\
		self.use_weapon_targeting,\
		self.unused_is_secondary,\
		self.unused_allow_non_subunits,\
		self.changes_subunit_order,\
		self.unused_allow_subunits,\
		self.interruptable,\
		self.waypoint_step_slowdown,\
		self.queueable,\
		self.disabled_maintain_air_target,\
		self.obstructable,\
		self.flee_unreturnable_damage,\
		self.unused_requires_movable_unit,\
		self.weapon_targeting,\
		self.technology_energy,\
		self.iscript_animation,\
		self.highlight_icon,\
		self.unknown17,\
		self.obscured_order\
			= values

	def save_values(self):
		return (
			self.label,
			self.use_weapon_targeting,
			self.unused_is_secondary,
			self.unused_allow_non_subunits,
			self.changes_subunit_order,
			self.unused_allow_subunits,
			self.interruptable,
			self.waypoint_step_slowdown,
			self.queueable,
			self.disabled_maintain_air_target,
			self.obstructable,
			self.flee_unreturnable_damage,
			self.unused_requires_movable_unit,
			self.weapon_targeting,
			self.technology_energy,
			self.iscript_animation,
			self.highlight_icon,
			self.unknown17,
			self.obscured_order
		)

	def expand(self):
		self.label = self.label or 0
		self.use_weapon_targeting = self.use_weapon_targeting or 0
		self.unused_is_secondary = self.unused_is_secondary or 0
		self.unused_allow_non_subunits = self.unused_allow_non_subunits or 0
		self.changes_subunit_order = self.changes_subunit_order or 0
		self.unused_allow_subunits = self.unused_allow_subunits or 0
		self.interruptable = self.interruptable or 0
		self.waypoint_step_slowdown = self.waypoint_step_slowdown or 0
		self.queueable = self.queueable or 0
		self.disabled_maintain_air_target = self.disabled_maintain_air_target or 0
		self.obstructable = self.obstructable or 0
		self.flee_unreturnable_damage = self.flee_unreturnable_damage or 0
		self.unused_requires_movable_unit = self.unused_requires_movable_unit or 0
		self.weapon_targeting = self.weapon_targeting or 0
		self.technology_energy = self.technology_energy or 0
		self.iscript_animation = self.iscript_animation or 0
		self.highlight_icon = self.highlight_icon or 0
		self.unknown17 = self.unknown17 or 0
		self.obscured_order = self.obscured_order or 0

	def export_text(self, id):
		return """Order(%d):
	label %d
	use_weapon_targeting %d
	unused_is_secondary %d
	unused_allow_non_subunits %d
	changes_subunit_order %d
	unused_allow_subunits %d
	interruptable %d
	waypoint_step_slowdown %d
	queueable %d
	disabled_maintain_air_target %d
	obstructable %d
	flee_unreturnable_damage %d
	unused_requires_movable_unit %d
	weapon_targeting %d
	technology_energy %d
	iscript_animation %d
	highlight_icon %d
	unknown17 %d
	obscured_order %d""" % (
			id,
			self.label,
			self.use_weapon_targeting,
			self.unused_is_secondary,
			self.unused_allow_non_subunits,
			self.changes_subunit_order,
			self.unused_allow_subunits,
			self.interruptable,
			self.waypoint_step_slowdown,
			self.queueable,
			self.disabled_maintain_air_target,
			self.obstructable,
			self.flee_unreturnable_damage,
			self.unused_requires_movable_unit,
			self.weapon_targeting,
			self.technology_energy,
			self.iscript_animation,
			self.highlight_icon,
			self.unknown17,
			self.obscured_order
		)

	def export_json(self, id, dump=True, indent=4):
		data = OrderedDict()
		data["_type"] = "Order"
		data["_id"] = id
		data["label"] = self.label
		data["use_weapon_targeting"] = self.use_weapon_targeting
		data["unused_is_secondary"] = self.unused_is_secondary
		data["unused_allow_non_subunits"] = self.unused_allow_non_subunits
		data["changes_subunit_order"] = self.changes_subunit_order
		data["unused_allow_subunits"] = self.unused_allow_subunits
		data["interruptable"] = self.interruptable
		data["waypoint_step_slowdown"] = self.waypoint_step_slowdown
		data["queueable"] = self.queueable
		data["disabled_maintain_air_target"] = self.disabled_maintain_air_target
		data["obstructable"] = self.obstructable
		data["flee_unreturnable_damage"] = self.flee_unreturnable_damage
		data["unused_requires_movable_unit"] = self.unused_requires_movable_unit
		data["weapon_targeting"] = self.weapon_targeting
		data["technology_energy"] = self.technology_energy
		data["iscript_animation"] = self.iscript_animation
		data["highlight_icon"] = self.highlight_icon
		data["unknown17"] = self.unknown17
		data["obscured_order"] = self.obscured_order
		if not dump:
			return data
		return json.dumps(data, indent=indent)

# orders.dat file handler
class OrdersDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 189,
			"properties": [
				{
					"name": "label",
					"type": "short"
				},
				{
					"name": "use_weapon_targeting",
					"type": "byte"
				},
				{
					"name": "unused_is_secondary",
					"type": "byte"
				},
				{
					"name": "unused_allow_non_subunits",
					"type": "byte"
				},
				{
					"name": "changes_subunit_order",
					"type": "byte"
				},
				{
					"name": "unused_allow_subunits",
					"type": "byte"
				},
				{
					"name": "interruptable",
					"type": "byte"
				},
				{
					"name": "waypoint_step_slowdown",
					"type": "byte"
				},
				{
					"name": "queueable",
					"type": "byte"
				},
				{
					"name": "disabled_maintain_air_target",
					"type": "byte"
				},
				{
					"name": "obstructable",
					"type": "byte"
				},
				{
					"name": "flee_unreturnable_damage",
					"type": "byte"
				},
				{
					"name": "unused_requires_movable_unit",
					"type": "byte"
				},
				{
					"name": "targeting",
					"type": "byte"
				},
				{
					"name": "technology_energy",
					"type": "byte"
				},
				{
					"name": "iscript_animation",
					"type": "byte"
				},
				{
					"name": "highlight_icon",
					"type": "short"
				},
				{
					"name": "unknown17",
					"type": "short"
				},
				{
					"name": "obscured_order",
					"type": "byte"
				}
			]
		})
	ENTRY_STRUCT = Order
	FILE_NAME = "orders.dat"
