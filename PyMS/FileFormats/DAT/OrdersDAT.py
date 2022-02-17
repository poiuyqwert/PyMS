
import AbstractDAT
import DATFormat

class Order(AbstractDAT.AbstractDATEntry):
	class Property:
		label = 'label'
		use_weapon_targeting = 'use_weapon_targeting'
		unused_is_secondary = 'unused_is_secondary'
		unused_allow_non_subunits = 'unused_allow_non_subunits'
		changes_subunit_order = 'changes_subunit_order'
		unused_allow_subunits = 'unused_allow_subunits'
		interruptable = 'interruptable'
		waypoints_slowdown = 'waypoints_slowdown'
		queueable = 'queueable'
		disabled_maintain_unit_target = 'disabled_maintain_unit_target'
		obstructable = 'obstructable'
		flee_unreturnable_damage = 'flee_unreturnable_damage'
		unused_requires_movable_unit = 'unused_requires_movable_unit'
		weapon_targeting = 'weapon_targeting'
		technology_energy = 'technology_energy'
		iscript_animation = 'iscript_animation'
		highlight_icon = 'highlight_icon'
		requirements = 'requirements'
		obscured_order = 'obscured_order'

	def __init__(self):
		self.label = 0
		self.use_weapon_targeting = 0
		self.unused_is_secondary = 0
		self.unused_allow_non_subunits = 0
		self.changes_subunit_order = 0
		self.unused_allow_subunits = 0
		self.interruptable = 0
		self.waypoints_slowdown = 0
		self.queueable = 0
		self.disabled_maintain_unit_target = 0
		self.obstructable = 0
		self.flee_unreturnable_damage = 0
		self.unused_requires_movable_unit = 0
		self.weapon_targeting = 0
		self.technology_energy = 0
		self.iscript_animation = 0
		self.highlight_icon = 0
		self.requirements = 65535
		self.obscured_order = 0

	def load_values(self, values):
		self.label,\
		self.use_weapon_targeting,\
		self.unused_is_secondary,\
		self.unused_allow_non_subunits,\
		self.changes_subunit_order,\
		self.unused_allow_subunits,\
		self.interruptable,\
		self.waypoints_slowdown,\
		self.queueable,\
		self.disabled_maintain_unit_target,\
		self.obstructable,\
		self.flee_unreturnable_damage,\
		self.unused_requires_movable_unit,\
		self.weapon_targeting,\
		self.technology_energy,\
		self.iscript_animation,\
		self.highlight_icon,\
		self.requirements,\
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
			self.waypoints_slowdown,
			self.queueable,
			self.disabled_maintain_unit_target,
			self.obstructable,
			self.flee_unreturnable_damage,
			self.unused_requires_movable_unit,
			self.weapon_targeting,
			self.technology_energy,
			self.iscript_animation,
			self.highlight_icon,
			self.requirements,
			self.obscured_order
		)

	EXPORT_NAME = 'Order'
	def _export(self, export_properties, export_type, data):
		self._export_property_value(export_properties, Order.Property.label, self.label, export_type, data)
		self._export_property_value(export_properties, Order.Property.use_weapon_targeting, self.use_weapon_targeting, export_type, data)
		self._export_property_value(export_properties, Order.Property.unused_is_secondary, self.unused_is_secondary, export_type, data)
		self._export_property_value(export_properties, Order.Property.unused_allow_non_subunits, self.unused_allow_non_subunits, export_type, data)
		self._export_property_value(export_properties, Order.Property.changes_subunit_order, self.changes_subunit_order, export_type, data)
		self._export_property_value(export_properties, Order.Property.unused_allow_subunits, self.unused_allow_subunits, export_type, data)
		self._export_property_value(export_properties, Order.Property.interruptable, self.interruptable, export_type, data)
		self._export_property_value(export_properties, Order.Property.waypoints_slowdown, self.waypoints_slowdown, export_type, data)
		self._export_property_value(export_properties, Order.Property.queueable, self.queueable, export_type, data)
		self._export_property_value(export_properties, Order.Property.disabled_maintain_unit_target, self.disabled_maintain_unit_target, export_type, data)
		self._export_property_value(export_properties, Order.Property.obstructable, self.obstructable, export_type, data)
		self._export_property_value(export_properties, Order.Property.flee_unreturnable_damage, self.flee_unreturnable_damage, export_type, data)
		self._export_property_value(export_properties, Order.Property.unused_requires_movable_unit, self.unused_requires_movable_unit, export_type, data)
		self._export_property_value(export_properties, Order.Property.weapon_targeting, self.weapon_targeting, export_type, data)
		self._export_property_value(export_properties, Order.Property.technology_energy, self.technology_energy, export_type, data)
		self._export_property_value(export_properties, Order.Property.iscript_animation, self.iscript_animation, export_type, data)
		self._export_property_value(export_properties, Order.Property.highlight_icon, self.highlight_icon, export_type, data)
		self._export_property_value(export_properties, Order.Property.requirements, self.requirements, export_type, data)
		self._export_property_value(export_properties, Order.Property.obscured_order, self.obscured_order, export_type, data)

# orders.dat file handler
class OrdersDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 189,
			"expanded_max_entries": 255,
			"properties": [
				{
					"name": "label", # Pointer to stat_txt.tbl
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
					"name": "waypoints_slowdown",
					"type": "byte"
				},
				{
					"name": "queueable",
					"type": "byte"
				},
				{
					"name": "disabled_maintain_unit_target",
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
					"name": "targeting", # Pointer to weapons.dat
					"type": "byte"
				},
				{
					"name": "technology_energy", # Pointer to techdata.dat
					"type": "byte"
				},
				{
					"name": "iscript_animation",
					"type": "byte"
				},
				{
					"name": "highlight_icon", # Pointer to cmdicon.grp
					"type": "short"
				},
				{
					"name": "requirements",
					"type": "short"
				},
				{
					"name": "obscured_order", # Pointer to orders.dat
					"type": "byte"
				}
			]
		})
	ENTRY_STRUCT = Order
	FILE_NAME = "orders.dat"

	def get_entry(self, index): # type: (int) -> Order
		return super(OrdersDAT, self).get_entry(index)
