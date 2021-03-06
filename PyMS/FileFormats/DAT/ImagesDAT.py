
import AbstractDAT
import DATFormat

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
		overlay_on_target       = 1
		enemy_unit_cloak        = 2 # + spell
		own_unit_cloak          = 3 # + spell
		ally_unit_cloak         = 4
		own_unit_cloak2         = 5 # + spell
		own_unit_cloak3         = 6 # draw only
		_crash                  = 7
		emp_shockwave           = 8
		use_remapping           = 9
		rle_shadow              = 10
		rle_hpfloatdraw         = 11
		warp_flash              = 12 # crashes staredit
		rle_outline             = 13
		rle_player_side         = 14 # Flag
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
	def _export(self, export_properties, export_type, data):
		self._export_property_value(export_properties, Image.Property.grp_file, self.grp_file, export_type, data)
		self._export_property_value(export_properties, Image.Property.gfx_turns, self.gfx_turns, export_type, data)
		self._export_property_value(export_properties, Image.Property.clickable, self.clickable, export_type, data)
		self._export_property_value(export_properties, Image.Property.use_full_iscript, self.use_full_iscript, export_type, data)
		self._export_property_value(export_properties, Image.Property.draw_if_cloaked, self.draw_if_cloaked, export_type, data)
		self._export_property_value(export_properties, Image.Property.draw_function, self.draw_function, export_type, data)
		self._export_property_value(export_properties, Image.Property.remapping, self.remapping, export_type, data)
		self._export_property_value(export_properties, Image.Property.iscript_id, self.iscript_id, export_type, data)
		self._export_property_value(export_properties, Image.Property.shield_overlay, self.shield_overlay, export_type, data)
		self._export_property_value(export_properties, Image.Property.attack_overlay, self.attack_overlay, export_type, data)
		self._export_property_value(export_properties, Image.Property.damage_overlay, self.damage_overlay, export_type, data)
		self._export_property_value(export_properties, Image.Property.special_overlay, self.special_overlay, export_type, data)
		self._export_property_value(export_properties, Image.Property.landing_dust_overlay, self.landing_dust_overlay, export_type, data)
		self._export_property_value(export_properties, Image.Property.lift_off_dust_overlay, self.lift_off_dust_overlay, export_type, data)

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
