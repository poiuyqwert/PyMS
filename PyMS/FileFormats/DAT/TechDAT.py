
from . import AbstractDAT
from . import DATFormat
from . import DATCoders

from typing import cast

class DATTechnology(AbstractDAT.AbstractDATEntry):
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
		self.research_requirements = 65535
		self.use_requirements = 65535
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
	def _export_data(self, export_properties, data):
		self._export_property_value(export_properties, DATTechnology.Property.mineral_cost, self.mineral_cost, data)
		self._export_property_value(export_properties, DATTechnology.Property.vespene_cost, self.vespene_cost, data)
		self._export_property_value(export_properties, DATTechnology.Property.research_time, self.research_time, data)
		self._export_property_value(export_properties, DATTechnology.Property.energy_required, self.energy_required, data)
		self._export_property_value(export_properties, DATTechnology.Property.research_requirements, self.research_requirements, data)
		self._export_property_value(export_properties, DATTechnology.Property.use_requirements, self.use_requirements, data)
		self._export_property_value(export_properties, DATTechnology.Property.icon, self.icon, data)
		self._export_property_value(export_properties, DATTechnology.Property.label, self.label, data)
		self._export_property_value(export_properties, DATTechnology.Property.staredit_race, self.staredit_race, data)
		self._export_property_value(export_properties, DATTechnology.Property.researched, self.researched, data, _TechnologyPropertyCoder.researched)
		self._export_property_value(export_properties, DATTechnology.Property.broodwar_only, self.broodwar_only, data, _TechnologyPropertyCoder.broodwar_only)

	def _import_data(self, data):
		mineral_cost = self._import_property_value(data, DATTechnology.Property.mineral_cost)
		vespene_cost = self._import_property_value(data, DATTechnology.Property.vespene_cost)
		research_time = self._import_property_value(data, DATTechnology.Property.research_time)
		energy_required = self._import_property_value(data, DATTechnology.Property.energy_required)
		research_requirements = self._import_property_value(data, DATTechnology.Property.research_requirements)
		use_requirements = self._import_property_value(data, DATTechnology.Property.use_requirements)
		icon = self._import_property_value(data, DATTechnology.Property.icon)
		label = self._import_property_value(data, DATTechnology.Property.label)
		staredit_race = self._import_property_value(data, DATTechnology.Property.staredit_race)
		researched = self._import_property_value(data, DATTechnology.Property.researched, _TechnologyPropertyCoder.researched)
		broodwar_only = self._import_property_value(data, DATTechnology.Property.broodwar_only, _TechnologyPropertyCoder.broodwar_only)

		if mineral_cost is not None:
			self.mineral_cost = mineral_cost
		if vespene_cost is not None:
			self.vespene_cost = vespene_cost
		if research_time is not None:
			self.research_time = research_time
		if energy_required is not None:
			self.energy_required = energy_required
		if research_requirements is not None:
			self.research_requirements = research_requirements
		if use_requirements is not None:
			self.use_requirements = use_requirements
		if icon is not None:
			self.icon = icon
		if label is not None:
			self.label = label
		if staredit_race is not None:
			self.staredit_race = staredit_race
		if researched is not None:
			self.researched = researched
		if broodwar_only is not None:
			self.broodwar_only = broodwar_only

class _TechnologyPropertyCoder:
	researched = DATCoders.DATBoolCoder()
	broodwar_only = DATCoders.DATBoolCoder()

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
	ENTRY_STRUCT = DATTechnology
	FILE_NAME = "techdata.dat"

	def get_entry(self, index: int) -> DATTechnology:
		return cast(DATTechnology, super(TechDAT, self).get_entry(index))
