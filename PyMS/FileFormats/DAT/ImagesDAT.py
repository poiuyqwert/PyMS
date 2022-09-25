
from . import AbstractDAT
from . import DATFormat
from . import DATCoders

class Image(AbstractDAT.AbstractDATEntry):
	class Property:
		grp_file = 'grp_file'
		gfx_turns = 'gfx_turns'
		clickable = 'clickable'
		use_full_iscript = 'use_full_iscript'
		draw_if_cloaked = 'draw_if_cloaked'
		draw_function = 'draw_function'
		remapping = 'remapping'
		iscript_id = 'iscript_id'
		shield_overlay = 'shield_overlay'
		attack_overlay = 'attack_overlay'
		damage_overlay = 'damage_overlay'
		special_overlay = 'special_overlay'
		landing_dust_overlay = 'landing_dust_overlay'
		lift_off_dust_overlay = 'lift_off_dust_overlay'

	class DrawFunction:
		normal                  = 0
		normal_no_hallucination = 1
		non_vision_cloaking     = 2
		non_vision_cloaked      = 3
		non_vision_decloaking   = 4
		vision_cloaking         = 5
		vision_cloaked          = 6
		vision_decloaking       = 7 # Crashes?
		emp_shockwave           = 8
		use_remapping           = 9
		shadow                  = 10
		hp_bar                  = 11
		warp_flash              = 12 # crashes staredit
		selection_circle        = 13
		player_color_override   = 14 # Flag
		hide_gfx_show_size_rect = 15
		hallucination           = 16
		warp_flash              = 17

	class Remapping:
		none     = 0
		ofire    = 1 # Orange
		gfire    = 2 # Green
		bfire    = 3 # Blue
		bexpl    = 4 # Blue2
		special  = 5 # Own cloak
		_crash   = 6
		_crash2  = 7
		unknown8 = 8
		uknonwn9 = 9

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

	EXPORT_NAME = 'Image'
	def _export_data(self, export_properties, data):
		self._export_property_value(export_properties, Image.Property.grp_file, self.grp_file, data)
		self._export_property_value(export_properties, Image.Property.gfx_turns, self.gfx_turns, data, _ImagePropertyCoder.gfx_turns)
		self._export_property_value(export_properties, Image.Property.clickable, self.clickable, data, _ImagePropertyCoder.clickable)
		self._export_property_value(export_properties, Image.Property.use_full_iscript, self.use_full_iscript, data, _ImagePropertyCoder.use_full_iscript)
		self._export_property_value(export_properties, Image.Property.draw_if_cloaked, self.draw_if_cloaked, data, _ImagePropertyCoder.draw_if_cloaked)
		self._export_property_value(export_properties, Image.Property.draw_function, self.draw_function, data)
		self._export_property_value(export_properties, Image.Property.remapping, self.remapping, data)
		self._export_property_value(export_properties, Image.Property.iscript_id, self.iscript_id, data)
		self._export_property_value(export_properties, Image.Property.shield_overlay, self.shield_overlay, data)
		self._export_property_value(export_properties, Image.Property.attack_overlay, self.attack_overlay, data)
		self._export_property_value(export_properties, Image.Property.damage_overlay, self.damage_overlay, data)
		self._export_property_value(export_properties, Image.Property.special_overlay, self.special_overlay, data)
		self._export_property_value(export_properties, Image.Property.landing_dust_overlay, self.landing_dust_overlay, data)
		self._export_property_value(export_properties, Image.Property.lift_off_dust_overlay, self.lift_off_dust_overlay, data)

	def _import_data(self, data):
		grp_file = self._import_property_value(data, Image.Property.grp_file)
		gfx_turns = self._import_property_value(data, Image.Property.gfx_turns, _ImagePropertyCoder.gfx_turns)
		clickable = self._import_property_value(data, Image.Property.clickable, _ImagePropertyCoder.clickable)
		use_full_iscript = self._import_property_value(data, Image.Property.use_full_iscript, _ImagePropertyCoder.use_full_iscript)
		draw_if_cloaked = self._import_property_value(data, Image.Property.draw_if_cloaked, _ImagePropertyCoder.draw_if_cloaked)
		draw_function = self._import_property_value(data, Image.Property.draw_function)
		remapping = self._import_property_value(data, Image.Property.remapping)
		iscript_id = self._import_property_value(data, Image.Property.iscript_id)
		shield_overlay = self._import_property_value(data, Image.Property.shield_overlay)
		attack_overlay = self._import_property_value(data, Image.Property.attack_overlay)
		damage_overlay = self._import_property_value(data, Image.Property.damage_overlay)
		special_overlay = self._import_property_value(data, Image.Property.special_overlay)
		landing_dust_overlay = self._import_property_value(data, Image.Property.landing_dust_overlay)
		lift_off_dust_overlay = self._import_property_value(data, Image.Property.lift_off_dust_overlay)

		if grp_file != None:
			self.grp_file = grp_file
		if gfx_turns != None:
			self.gfx_turns = gfx_turns
		if clickable != None:
			self.clickable = clickable
		if use_full_iscript != None:
			self.use_full_iscript = use_full_iscript
		if draw_if_cloaked != None:
			self.draw_if_cloaked = draw_if_cloaked
		if draw_function != None:
			self.draw_function = draw_function
		if remapping != None:
			self.remapping = remapping
		if iscript_id != None:
			self.iscript_id = iscript_id
		if shield_overlay != None:
			self.shield_overlay = shield_overlay
		if attack_overlay != None:
			self.attack_overlay = attack_overlay
		if damage_overlay != None:
			self.damage_overlay = damage_overlay
		if special_overlay != None:
			self.special_overlay = special_overlay
		if landing_dust_overlay != None:
			self.landing_dust_overlay = landing_dust_overlay
		if lift_off_dust_overlay != None:
			self.lift_off_dust_overlay = lift_off_dust_overlay

class _ImagePropertyCoder:
	gfx_turns = DATCoders.DATBoolCoder()
	clickable = DATCoders.DATBoolCoder()
	use_full_iscript = DATCoders.DATBoolCoder()
	draw_if_cloaked = DATCoders.DATBoolCoder()

# images.dat file handler
class ImagesDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 999,
			"expanded_max_entries": 65536,
			"properties": [
				{
					"name": "grp_file", # Pointer to images.tbl
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
					"name": "iscript_id", # Pointer to iscript.bin
					"type": "long"
				},
				{
					"name": "shield_overlay", # Pointer to images.tbl
					"type": "long"
				},
				{
					"name": "attack_overlay", # Pointer to images.tbl
					"type": "long"
				},
				{
					"name": "damage_overlay", # Pointer to images.tbl
					"type": "long"
				},
				{
					"name": "special_overlay", # Pointer to images.tbl
					"type": "long"
				},
				{
					"name": "landing_dust_overlay", # Pointer to images.tbl
					"type": "long"
				},
				{
					"name": "lift_off_dust_overlay", # Pointer to images.tbl
					"type": "long"
				}
			]
		})
	ENTRY_STRUCT = Image
	FILE_NAME = "images.dat"

	def get_entry(self, index): # type: (int) -> Image
		return super(ImagesDAT, self).get_entry(index)
