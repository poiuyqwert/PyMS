
from . import AbstractDAT
from . import DATFormat
from . import DATCoders

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
	def _export_data(self, export_properties, data):
		self._export_property_value(export_properties, Order.Property.label, self.label, data)
		self._export_property_value(export_properties, Order.Property.use_weapon_targeting, self.use_weapon_targeting, data, _OrderPropertyCoder.use_weapon_targeting)
		self._export_property_value(export_properties, Order.Property.unused_is_secondary, self.unused_is_secondary, data, _OrderPropertyCoder.unused_is_secondary)
		self._export_property_value(export_properties, Order.Property.unused_allow_non_subunits, self.unused_allow_non_subunits, data, _OrderPropertyCoder.unused_allow_non_subunits)
		self._export_property_value(export_properties, Order.Property.changes_subunit_order, self.changes_subunit_order, data, _OrderPropertyCoder.changes_subunit_order)
		self._export_property_value(export_properties, Order.Property.unused_allow_subunits, self.unused_allow_subunits, data, _OrderPropertyCoder.unused_allow_subunits)
		self._export_property_value(export_properties, Order.Property.interruptable, self.interruptable, data, _OrderPropertyCoder.interruptable)
		self._export_property_value(export_properties, Order.Property.waypoints_slowdown, self.waypoints_slowdown, data, _OrderPropertyCoder.waypoints_slowdown)
		self._export_property_value(export_properties, Order.Property.queueable, self.queueable, data, _OrderPropertyCoder.queueable)
		self._export_property_value(export_properties, Order.Property.disabled_maintain_unit_target, self.disabled_maintain_unit_target, data, _OrderPropertyCoder.disabled_maintain_unit_target)
		self._export_property_value(export_properties, Order.Property.obstructable, self.obstructable, data, _OrderPropertyCoder.obstructable)
		self._export_property_value(export_properties, Order.Property.flee_unreturnable_damage, self.flee_unreturnable_damage, data, _OrderPropertyCoder.flee_unreturnable_damage)
		self._export_property_value(export_properties, Order.Property.unused_requires_movable_unit, self.unused_requires_movable_unit, data, _OrderPropertyCoder.unused_requires_movable_unit)
		self._export_property_value(export_properties, Order.Property.weapon_targeting, self.weapon_targeting, data)
		self._export_property_value(export_properties, Order.Property.technology_energy, self.technology_energy, data)
		self._export_property_value(export_properties, Order.Property.iscript_animation, self.iscript_animation, data)
		self._export_property_value(export_properties, Order.Property.highlight_icon, self.highlight_icon, data)
		self._export_property_value(export_properties, Order.Property.requirements, self.requirements, data)
		self._export_property_value(export_properties, Order.Property.obscured_order, self.obscured_order, data)

	def _import_data(self, data):
		label = self._import_property_value(data, Order.Property.label)
		use_weapon_targeting = self._import_property_value(data, Order.Property.use_weapon_targeting, _OrderPropertyCoder.use_weapon_targeting)
		unused_is_secondary = self._import_property_value(data, Order.Property.unused_is_secondary, _OrderPropertyCoder.unused_is_secondary)
		unused_allow_non_subunits = self._import_property_value(data, Order.Property.unused_allow_non_subunits, _OrderPropertyCoder.unused_allow_non_subunits)
		changes_subunit_order = self._import_property_value(data, Order.Property.changes_subunit_order, _OrderPropertyCoder.changes_subunit_order)
		unused_allow_subunits = self._import_property_value(data, Order.Property.unused_allow_subunits, _OrderPropertyCoder.unused_allow_subunits)
		interruptable = self._import_property_value(data, Order.Property.interruptable, _OrderPropertyCoder.interruptable)
		waypoints_slowdown = self._import_property_value(data, Order.Property.waypoints_slowdown, _OrderPropertyCoder.waypoints_slowdown)
		queueable = self._import_property_value(data, Order.Property.queueable, _OrderPropertyCoder.queueable)
		disabled_maintain_unit_target = self._import_property_value(data, Order.Property.disabled_maintain_unit_target, _OrderPropertyCoder.disabled_maintain_unit_target)
		obstructable = self._import_property_value(data, Order.Property.obstructable, _OrderPropertyCoder.obstructable)
		flee_unreturnable_damage = self._import_property_value(data, Order.Property.flee_unreturnable_damage, _OrderPropertyCoder.flee_unreturnable_damage)
		unused_requires_movable_unit = self._import_property_value(data, Order.Property.unused_requires_movable_unit, _OrderPropertyCoder.unused_requires_movable_unit)
		weapon_targeting = self._import_property_value(data, Order.Property.weapon_targeting)
		technology_energy = self._import_property_value(data, Order.Property.technology_energy)
		iscript_animation = self._import_property_value(data, Order.Property.iscript_animation)
		highlight_icon = self._import_property_value(data, Order.Property.highlight_icon)
		requirements = self._import_property_value(data, Order.Property.requirements)
		obscured_order = self._import_property_value(data, Order.Property.obscured_order)

		if label != None:
			self.label = label
		if use_weapon_targeting != None:
			self.use_weapon_targeting = use_weapon_targeting
		if unused_is_secondary != None:
			self.unused_is_secondary = unused_is_secondary
		if unused_allow_non_subunits != None:
			self.unused_allow_non_subunits = unused_allow_non_subunits
		if changes_subunit_order != None:
			self.changes_subunit_order = changes_subunit_order
		if unused_allow_subunits != None:
			self.unused_allow_subunits = unused_allow_subunits
		if interruptable != None:
			self.interruptable = interruptable
		if waypoints_slowdown != None:
			self.waypoints_slowdown = waypoints_slowdown
		if queueable != None:
			self.queueable = queueable
		if disabled_maintain_unit_target != None:
			self.disabled_maintain_unit_target = disabled_maintain_unit_target
		if obstructable != None:
			self.obstructable = obstructable
		if flee_unreturnable_damage != None:
			self.flee_unreturnable_damage = flee_unreturnable_damage
		if unused_requires_movable_unit != None:
			self.unused_requires_movable_unit = unused_requires_movable_unit
		if weapon_targeting != None:
			self.weapon_targeting = weapon_targeting
		if technology_energy != None:
			self.technology_energy = technology_energy
		if iscript_animation != None:
			self.iscript_animation = iscript_animation
		if highlight_icon != None:
			self.highlight_icon = highlight_icon
		if requirements != None:
			self.requirements = requirements
		if obscured_order != None:
			self.obscured_order = obscured_order

class _OrderPropertyCoder:
	use_weapon_targeting = DATCoders.DATBoolCoder()
	unused_is_secondary = DATCoders.DATBoolCoder()
	unused_allow_non_subunits = DATCoders.DATBoolCoder()
	changes_subunit_order = DATCoders.DATBoolCoder()
	unused_allow_subunits = DATCoders.DATBoolCoder()
	interruptable = DATCoders.DATBoolCoder()
	waypoints_slowdown = DATCoders.DATBoolCoder()
	queueable = DATCoders.DATBoolCoder()
	disabled_maintain_unit_target = DATCoders.DATBoolCoder()
	obstructable = DATCoders.DATBoolCoder()
	flee_unreturnable_damage = DATCoders.DATBoolCoder()
	unused_requires_movable_unit = DATCoders.DATBoolCoder()

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
