
import AbstractDAT
import DATFormat

class Technology(AbstractDAT.AbstractDATEntry):
	class Property:
		mineral_cost = 'mineral_cost'
		vespene_cost = 'vespene_cost'
		research_time = 'research_time'
		energy_required = 'energy_required'
		research_requirements = 'research_requirements'
		use_requirements = 'use_requirements'
		icon = 'icon'
		label = 'label'
		staredit_race = 'staredit_race'
		researched = 'researched'
		broodwar_only = 'broodwar_only'

	def __init__(self):
		self.mineral_cost = 0
		self.vespene_cost = 0
		self.research_time = 0
		self.energy_required = 0
		self.research_requirements = 0
		self.use_requirements = 0
		self.icon = 0
		self.label = 0
		self.staredit_race = 0
		self.researched = 0
		self.broodwar_only = 0

	def load_values(self, values):
		self.mineral_cost,\
		self.vespene_cost,\
		self.research_time,\
		self.energy_required,\
		self.research_requirements,\
		self.use_requirements,\
		self.icon,\
		self.label,\
		self.staredit_race,\
		self.researched,\
		self.broodwar_only\
			= values

	def save_values(self):
		return (
			self.mineral_cost,
			self.vespene_cost,
			self.research_time,
			self.energy_required,
			self.research_requirements,
			self.use_requirements,
			self.icon,
			self.label,
			self.staredit_race,
			self.researched,
			self.broodwar_only
		)

	EXPORT_NAME = 'Technology'
	def _export(self, export_properties, export_type, data):
		self._export_property_value(export_properties, Technology.Property.mineral_cost, self.mineral_cost, export_type, data)
		self._export_property_value(export_properties, Technology.Property.vespene_cost, self.vespene_cost, export_type, data)
		self._export_property_value(export_properties, Technology.Property.research_time, self.research_time, export_type, data)
		self._export_property_value(export_properties, Technology.Property.energy_required, self.energy_required, export_type, data)
		self._export_property_value(export_properties, Technology.Property.research_requirements, self.research_requirements, export_type, data)
		self._export_property_value(export_properties, Technology.Property.use_requirements, self.use_requirements, export_type, data)
		self._export_property_value(export_properties, Technology.Property.icon, self.icon, export_type, data)
		self._export_property_value(export_properties, Technology.Property.label, self.label, export_type, data)
		self._export_property_value(export_properties, Technology.Property.staredit_race, self.staredit_race, export_type, data)
		self._export_property_value(export_properties, Technology.Property.researched, self.researched, export_type, data)
		self._export_property_value(export_properties, Technology.Property.broodwar_only, self.broodwar_only, export_type, data)

# techdata.dat file handler
class TechDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 44,
			"expanded_max_entries": 255,
			"properties": [
				{
					"name": "mineral_cost",
					"type": "short"
				},
				{
					"name": "vespene_cost",
					"type": "short"
				},
				{
					"name": "research_time",
					"type": "short"
				},
				{
					"name": "energy_required",
					"type": "short"
				},
				{
					"name": "research_requirements",
					"type": "short"
				},
				{
					"name": "use_requirements",
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
					"name": "researched",
					"type": "byte"
				},
				{
					"name": "broodwar_only",
					"type": "byte"
				}
			]
		})
	ENTRY_STRUCT = Technology
	FILE_NAME = "techdata.dat"
