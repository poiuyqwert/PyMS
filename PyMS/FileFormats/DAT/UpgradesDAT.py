
from . import AbstractDAT
from . import DATFormat
from . import DATCoders

class Upgrade(AbstractDAT.AbstractDATEntry):
	class Property:
		mineral_cost_base = 'mineral_cost_base'
		mineral_cost_factor = 'mineral_cost_factor'
		vespene_cost_base = 'vespene_cost_base'
		vespene_cost_factor = 'vespene_cost_factor'
		research_time_base = 'research_time_base'
		research_time_factor = 'research_time_factor'
		requirements = 'requirements'
		icon = 'icon'
		label = 'label'
		staredit_race = 'staredit_race'
		max_repeats = 'max_repeats'
		broodwar_only = 'broodwar_only'

	def __init__(self):
		self.mineral_cost_base = 0
		self.mineral_cost_factor = 0
		self.vespene_cost_base = 0
		self.vespene_cost_factor = 0
		self.research_time_base = 0
		self.research_time_factor = 0
		self.requirements = 65535
		self.icon = 0
		self.label = 0
		self.staredit_race = 0
		self.max_repeats = 0
		self.broodwar_only = 0

	def load_values(self, values):
		self.mineral_cost_base,\
		self.mineral_cost_factor,\
		self.vespene_cost_base,\
		self.vespene_cost_factor,\
		self.research_time_base,\
		self.research_time_factor,\
		self.requirements,\
		self.icon,\
		self.label,\
		self.staredit_race,\
		self.max_repeats,\
		self.broodwar_only\
			= values

	def save_values(self):
		return (
			self.mineral_cost_base,
			self.mineral_cost_factor,
			self.vespene_cost_base,
			self.vespene_cost_factor,
			self.research_time_base,
			self.research_time_factor,
			self.requirements,
			self.icon,
			self.label,
			self.staredit_race,
			self.max_repeats,
			self.broodwar_only
		)

	EXPORT_NAME = 'Upgrade'
	def _export_data(self, export_properties, data):
		self._export_property_value(export_properties, Upgrade.Property.mineral_cost_base, self.mineral_cost_base, data)
		self._export_property_value(export_properties, Upgrade.Property.mineral_cost_factor, self.mineral_cost_factor, data)
		self._export_property_value(export_properties, Upgrade.Property.vespene_cost_base, self.vespene_cost_base, data)
		self._export_property_value(export_properties, Upgrade.Property.vespene_cost_factor, self.vespene_cost_factor, data)
		self._export_property_value(export_properties, Upgrade.Property.research_time_base, self.research_time_base, data)
		self._export_property_value(export_properties, Upgrade.Property.research_time_factor, self.research_time_factor, data)
		self._export_property_value(export_properties, Upgrade.Property.requirements, self.requirements, data)
		self._export_property_value(export_properties, Upgrade.Property.icon, self.icon, data)
		self._export_property_value(export_properties, Upgrade.Property.label, self.label, data)
		self._export_property_value(export_properties, Upgrade.Property.staredit_race, self.staredit_race, data)
		self._export_property_value(export_properties, Upgrade.Property.max_repeats, self.max_repeats, data)
		self._export_property_value(export_properties, Upgrade.Property.broodwar_only, self.broodwar_only, data, _UpgradePropertyCoder.broodwar_only)

	def _import_data(self, data):
		mineral_cost_base = self._import_property_value(data, Upgrade.Property.mineral_cost_base)
		mineral_cost_factor = self._import_property_value(data, Upgrade.Property.mineral_cost_factor)
		vespene_cost_base = self._import_property_value(data, Upgrade.Property.vespene_cost_base)
		vespene_cost_factor = self._import_property_value(data, Upgrade.Property.vespene_cost_factor)
		research_time_base = self._import_property_value(data, Upgrade.Property.research_time_base)
		research_time_factor = self._import_property_value(data, Upgrade.Property.research_time_factor)
		requirements = self._import_property_value(data, Upgrade.Property.requirements)
		icon = self._import_property_value(data, Upgrade.Property.icon)
		label = self._import_property_value(data, Upgrade.Property.label)
		staredit_race = self._import_property_value(data, Upgrade.Property.staredit_race)
		max_repeats = self._import_property_value(data, Upgrade.Property.max_repeats)
		broodwar_only = self._import_property_value(data, Upgrade.Property.broodwar_only, _UpgradePropertyCoder.broodwar_only)

		if mineral_cost_base != None:
			self.mineral_cost_base = mineral_cost_base
		if mineral_cost_factor != None:
			self.mineral_cost_factor = mineral_cost_factor
		if vespene_cost_base != None:
			self.vespene_cost_base = vespene_cost_base
		if vespene_cost_factor != None:
			self.vespene_cost_factor = vespene_cost_factor
		if research_time_base != None:
			self.research_time_base = research_time_base
		if research_time_factor != None:
			self.research_time_factor = research_time_factor
		if requirements != None:
			self.requirements = requirements
		if icon != None:
			self.icon = icon
		if label != None:
			self.label = label
		if staredit_race != None:
			self.staredit_race = staredit_race
		if max_repeats != None:
			self.max_repeats = max_repeats
		if broodwar_only != None:
			self.broodwar_only = broodwar_only

class _UpgradePropertyCoder:
	broodwar_only = DATCoders.DATBoolCoder()

# upgrades.dat file handler
class UpgradesDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 61,
			"expanded_max_entries": 256,
			"properties": [
				{
					"name": "mineral_cost_base",
					"type": "short"
				},
				{
					"name": "mineral_cost_factor",
					"type": "short"
				},
				{
					"name": "vespene_cost_base",
					"type": "short"
				},
				{
					"name": "vespene_cost_factor",
					"type": "short"
				},
				{
					"name": "research_time_base",
					"type": "short"
				},
				{
					"name": "research_time_factor",
					"type": "short"
				},
				{
					"name": "requirements",
					"type": "short"
				},
				{
					"name": "icon", # Pointer to cmdicon.grp
					"type": "short"
				},
				{
					"name": "label", # Pointer to stat_txt.tbl
					"type": "short"
				},
				{
					"name": "staredit_race",
					"type": "byte"
				},
				{
					"name": "max_repeats",
					"type": "byte"
				},
				{
					"name": "broodwar_only",
					"type": "byte"
				}
			]
		})
	ENTRY_STRUCT = Upgrade
	FILE_NAME = "upgrades.dat"

	def get_entry(self, index): # type: (int) -> Upgrade
		return super(UpgradesDAT, self).get_entry(index)
