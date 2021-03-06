
import AbstractDAT
import DATFormat

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
		self.requirements = 0
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
	def _export(self, export_properties, export_type, data):
		self._export_property_value(export_properties, Upgrade.Property.mineral_cost_base, self.mineral_cost_base, export_type, data)
		self._export_property_value(export_properties, Upgrade.Property.mineral_cost_factor, self.mineral_cost_factor, export_type, data)
		self._export_property_value(export_properties, Upgrade.Property.vespene_cost_base, self.vespene_cost_base, export_type, data)
		self._export_property_value(export_properties, Upgrade.Property.vespene_cost_factor, self.vespene_cost_factor, export_type, data)
		self._export_property_value(export_properties, Upgrade.Property.research_time_base, self.research_time_base, export_type, data)
		self._export_property_value(export_properties, Upgrade.Property.research_time_factor, self.research_time_factor, export_type, data)
		self._export_property_value(export_properties, Upgrade.Property.requirements, self.requirements, export_type, data)
		self._export_property_value(export_properties, Upgrade.Property.icon, self.icon, export_type, data)
		self._export_property_value(export_properties, Upgrade.Property.label, self.label, export_type, data)
		self._export_property_value(export_properties, Upgrade.Property.staredit_race, self.staredit_race, export_type, data)
		self._export_property_value(export_properties, Upgrade.Property.max_repeats, self.max_repeats, export_type, data)
		self._export_property_value(export_properties, Upgrade.Property.broodwar_only, self.broodwar_only, export_type, data)

# upgrades.dat file handler
class UpgradesDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 61,
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
					"name": "icon",
					"type": "short"
				},
				{
					"name": "label",
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
