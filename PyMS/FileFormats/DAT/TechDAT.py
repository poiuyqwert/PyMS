
import AbstractDAT
import DATFormat

from collections import OrderedDict
import json

class Technology(AbstractDAT.AbstractDATEntry):
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

	def expand(self):
		self.mineral_cost = self.mineral_cost or 0
		self.vespene_cost = self.vespene_cost or 0
		self.research_time = self.research_time or 0
		self.energy_required = self.energy_required or 0
		self.research_requirements = self.research_requirements or 0
		self.use_requirements = self.use_requirements or 0
		self.icon = self.icon or 0
		self.label = self.label or 0
		self.staredit_race = self.staredit_race or 0
		self.researched = self.researched or 0
		self.broodwar_only = self.broodwar_only or 0

	def export_text(self, id):
		return """Technology(%d):
	mineral_cost %d
	vespene_cost %d
	research_time %d
	energy_required %d
	research_requirements %d
	use_requirements %d
	icon %d
	label %d
	staredit_race %d
	researched %d
	broodwar_only %d""" % (
			id,
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

	def export_json(self, id, dump=True, indent=4):
		data = OrderedDict()
		data["_type"] = "Technology"
		data["_id"] = id
		data["mineral_cost"] = self.mineral_cost
		data["vespene_cost"] = self.vespene_cost
		data["research_time"] = self.research_time
		data["energy_required"] = self.energy_required
		data["research_requirements"] = self.research_requirements
		data["use_requirements"] = self.use_requirements
		data["icon"] = self.icon
		data["label"] = self.label
		data["staredit_race"] = self.staredit_race
		data["researched"] = self.researched
		data["broodwar_only"] = self.broodwar_only
		if not dump:
			return data
		return json.dumps(data, indent=indent)

# techdata.dat file handler
class TechDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 44,
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
