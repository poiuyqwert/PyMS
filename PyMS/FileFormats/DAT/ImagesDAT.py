
import AbstractDAT
import DATFormat

from collections import OrderedDict
import json

class Image(AbstractDAT.AbstractDATEntry):
	def __init__(self):
		self.grp_file = 0
		self.gfx_turns = 0
		self.clickable = 0
		self.use_full_iscript = 0
		self.draw_if_cloaked = 0
		self.draw_function = 0
		self.remapping = 0
		self.iscript_id = 0
		self.shield_overlay = 0
		self.attack_overlay = 0
		self.damage_overlay = 0
		self.special_overlay = 0
		self.landing_dust_overlay = 0
		self.lift_off_dust_overlay = 0

	def load_values(self, values):
		self.grp_file,\
		self.gfx_turns,\
		self.clickable,\
		self.use_full_iscript,\
		self.draw_if_cloaked,\
		self.draw_function,\
		self.remapping,\
		self.iscript_id,\
		self.shield_overlay,\
		self.attack_overlay,\
		self.damage_overlay,\
		self.special_overlay,\
		self.landing_dust_overlay,\
		self.lift_off_dust_overlay\
			= values

	def save_values(self):
		return (
			self.grp_file,
			self.gfx_turns,
			self.clickable,
			self.use_full_iscript,
			self.draw_if_cloaked,
			self.draw_function,
			self.remapping,
			self.iscript_id,
			self.shield_overlay,
			self.attack_overlay,
			self.damage_overlay,
			self.special_overlay,
			self.landing_dust_overlay,
			self.lift_off_dust_overlay
		)

	def expand(self):
		self.grp_file = self.grp_file or 0
		self.gfx_turns = self.gfx_turns or 0
		self.clickable = self.clickable or 0
		self.use_full_iscript = self.use_full_iscript or 0
		self.draw_if_cloaked = self.draw_if_cloaked or 0
		self.draw_function = self.draw_function or 0
		self.remapping = self.remapping or 0
		self.iscript_id = self.iscript_id or 0
		self.shield_overlay = self.shield_overlay or 0
		self.attack_overlay = self.attack_overlay or 0
		self.damage_overlay = self.damage_overlay or 0
		self.special_overlay = self.special_overlay or 0
		self.landing_dust_overlay = self.landing_dust_overlay or 0
		self.lift_off_dust_overlay = self.lift_off_dust_overlay or 0

	def export_text(self, id):
		return """Image(%d):
	grp_file %d
	gfx_turns %d
	clickable %d
	use_full_iscript %d
	draw_if_cloaked %d
	draw_function %d
	remapping %d
	iscript_id %d
	shield_overlay %d
	attack_overlay %d
	damage_overlay %d
	special_overlay %d
	landing_dust_overlay %d
	lift_off_dust_overlay %d""" % (
			id,
			self.grp_file,
			self.gfx_turns,
			self.clickable,
			self.use_full_iscript,
			self.draw_if_cloaked,
			self.draw_function,
			self.remapping,
			self.iscript_id,
			self.shield_overlay,
			self.attack_overlay,
			self.damage_overlay,
			self.special_overlay,
			self.landing_dust_overlay,
			self.lift_off_dust_overlay
		)

	def export_json(self, id, dump=True, indent=4):
		data = OrderedDict()
		data["_type"] = "Image"
		data["_id"] = id
		data["grp_file"] = self.grp_file
		data["gfx_turns"] = self.gfx_turns
		data["clickable"] = self.clickable
		data["use_full_iscript"] = self.use_full_iscript
		data["draw_if_cloaked"] = self.draw_if_cloaked
		data["draw_function"] = self.draw_function
		data["remapping"] = self.remapping
		data["iscript_id"] = self.iscript_id
		data["shield_overlay"] = self.shield_overlay
		data["attack_overlay"] = self.attack_overlay
		data["damage_overlay"] = self.damage_overlay
		data["special_overlay"] = self.special_overlay
		data["landing_dust_overlay"] = self.landing_dust_overlay
		data["lift_off_dust_overlay"] = self.lift_off_dust_overlay
		if not dump:
			return data
		return json.dumps(data, indent=indent)

# images.dat file handler
class ImagesDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 999,
			"properties": [
				{
					"name": "grp_file",
					"type": "long"
				},
				{
					"name": "gfx_turns",
					"type": "byte"
				},
				{
					"name": "clickable",
					"type": "byte"
				},
				{
					"name": "use_full_iscript",
					"type": "byte"
				},
				{
					"name": "draw_if_cloaked",
					"type": "byte"
				},
				{
					"name": "draw_function",
					"type": "byte"
				},
				{
					"name": "remapping",
					"type": "byte"
				},
				{
					"name": "iscript_id",
					"type": "long"
				},
				{
					"name": "shield_overlay",
					"type": "long"
				},
				{
					"name": "attack_overlay",
					"type": "long"
				},
				{
					"name": "damage_overlay",
					"type": "long"
				},
				{
					"name": "special_overlay",
					"type": "long"
				},
				{
					"name": "landing_dust_overlay",
					"type": "long"
				},
				{
					"name": "lift_off_dust_overlay",
					"type": "long"
				}
			]
		})
	ENTRY_STRUCT = Image
	FILE_NAME = "images.dat"
