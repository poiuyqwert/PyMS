
from .TilePaletteView import TilePaletteView
from .MegaEditorView import MegaEditorView
from .TilePalette import TilePalette
from .Placeability import Placeability
from .Delegates import TilePaletteDelegate, TilePaletteViewDelegate, MegaEditorViewDelegate, PlaceabilityDelegate

from ..FileFormats.Tileset.Tileset import Tileset, TileType, megatile_to_photo, minitile_to_photo
from ..FileFormats.Tileset.CV5 import CV5Group, CV5Flag, CV5DoodadFlag
from ..FileFormats.Tileset.VF4 import VF4Flag
from ..FileFormats.Tileset.VX4 import VX4Minitile
from ..FileFormats.Tileset.Serialize import TileGroupField, DoodadGroupField, MegatileField
from ..FileFormats import TBL

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.Settings import Settings
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.SettingsDialog import SettingsDialog
from ..Utilities import Serialize

import sys, io
from enum import Enum

from typing import Self, cast, Callable, TextIO

LONG_VERSION = 'v%s' % Assets.version('PyTILE')

class CheckSaved(Enum):
	cancelled = 0
	saved = 1 # Also covers not open, not edited, and chose to ignore changes

class EditorGroup:
	class EditorWidget:
		def __init__(self, group: 'EditorGroup', widget: Widget):
			self.group = group
			self.widget = widget

		def add(self, sticky: str = W, span: int = 1, weight: int | None = None, new_row: bool = True) -> 'EditorGroup':
			self.widget.grid(row=self.group.row, column=self.group.column, sticky=sticky, columnspan=span)
			if weight is not None:
				self.group.container.grid_columnconfigure(self.group.column, weight=weight)
			if new_row:
				self.group.row += 1
				self.group.column = 0
			else:
				self.group.column += span
			return self.group

	def __init__(self, parent: Misc, name: str, tooltip: str | None = None, weight: int = 0):
		self.container = LabelFrame(parent, text=name)
		self.content = Frame(self.container)
		self.content.pack(padx=2, pady=2)
		self.tooltip = tooltip
		self.weight = weight
		self.row = 0
		self.column = 0
		self.editors = [] # type: list[Widget]

	def _tip(self, widget: Widget, tooltip: str) -> None:
		if self.tooltip:
			tooltip += '\n' + self.tooltip
		Tooltip(widget, tooltip)

	def skip(self, columns=1) -> Self:
		self.column += columns
		return self

	def label(self, text: str, add_colon: bool = True) -> EditorWidget:
		if add_colon:
			text += ':'
		widget = Label(self.content, text=text)
		return EditorGroup.EditorWidget(self, widget)

	def check(self, name: str, tooltip: str, variable: BooleanVar) -> EditorWidget:
		widget = Checkbutton(self.content, text=name, variable=variable, state=DISABLED)
		self._tip(widget, tooltip)
		self.editors.append(widget)
		return EditorGroup.EditorWidget(self, widget)

	def check_flag(self, name: str, tooltip: str, variable: IntegerVar, value: int, editable: bool = True) -> EditorWidget:
		widget = MaskedCheckbutton(self.content, text=name, variable=variable, value=value, state=DISABLED)
		self._tip(widget, tooltip)
		if editable:
			self.editors.append(widget)
		return EditorGroup.EditorWidget(self, widget)

	def radio_flag(self, name: str, tooltip: str, variable: IntegerVar, value: int, mask: int | None = None, editable: bool = True) -> EditorWidget:
		widget = MaskedRadiobutton(self.content, text=name, variable=variable, value=value, mask=mask if mask else variable.range[1], state=DISABLED)
		self._tip(widget, tooltip)
		if editable:
			self.editors.append(widget)
		return EditorGroup.EditorWidget(self, widget)

	def entry(self, tooltip: str, variable: IntegerVar) -> EditorWidget:
		widget = Entry(self.content, textvariable=variable, font=Font.fixed(), width=len(str(variable.range[1])), state=DISABLED)
		self._tip(widget, tooltip)
		self.editors.append(widget)
		return EditorGroup.EditorWidget(self, widget)

	def dropdown(self, tooltip: str, options: list[str], variable: IntegerVar) -> EditorWidget:
		widget = DropDown(self.content, IntVar(), options, variable, width=20)
		self._tip(widget, tooltip)
		self.editors.append(widget)
		return EditorGroup.EditorWidget(self, widget)

	def button(self, name: str, tooltip: str, callback: Callable[[], None]) -> EditorWidget:
		widget = Button(self.content, text=name, command=callback, state=DISABLED)
		self._tip(widget, tooltip)
		self.editors.append(widget)
		return EditorGroup.EditorWidget(self, widget)

	def widget(self, widget: Widget, editors: list[Widget]) -> EditorWidget:
		self.editors.extend(editors)
		return EditorGroup.EditorWidget(self, widget)

	def enabled(self, enabled: bool) -> None:
		for editor in self.editors:
			editor['state'] = NORMAL if enabled else DISABLED

class CopyOptions:
	def __init__(self, group: str, settings: Settings, callback: Callable[[], None], reset_key: str | None = None):
		self.group = group
		self.settings = settings
		self.callback = callback
		self.options: list[tuple[str, BooleanVar]] = []
		if reset_key and reset_key in self.settings['copy'][group]:
			del self.settings['copy'][group]
			
	def option(self, name: str) -> BooleanVar:
		variable = BooleanVar()
		self.options.append((name, variable))
		variable.set(self.settings['copy'][self.group].get(name, True))
		variable.trace('w', self.callback)
		return variable

	def any_enabled(self) -> bool:
		return any(var.get() for _,var in self.options)

	def save(self) -> None:
		for name,var in self.options:
			self.settings['copy'][self.group][name] = var.get()

class PyTILE(MainWindow, TilePaletteDelegate, TilePaletteViewDelegate, MegaEditorViewDelegate, PlaceabilityDelegate):
	def __init__(self, guifile=None): # type: (str | None) -> None
		MainWindow.__init__(self)

		self.settings = Settings('PyTILE', '1')
		self.title('PyTILE %s' % LONG_VERSION)
		self.set_icon('PyTILE')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyTILE', Assets.version('PyTILE'))
		ga.track(GAScreen('PyTILE'))
		setup_trace('PyTILE', self)
		Theme.load_theme(self.settings.get('theme'), self)

		self.stat_txt = TBL.TBL()
		self.stat_txt_file = ''
		filen = str(self.settings.files.get('stat_txt', Assets.mpq_file_path('rez', 'stat_txt.tbl')))
		while True:
			try:
				self.stat_txt.load_file(filen)
				break
			except:
				filen = self.settings.lastpath.tbl.select_open_file(self, title='Open stat_txt.tbl', filetypes=[FileType.tbl()])
				if not filen:
					sys.exit()

		self.loading_megas = False
		self.loading_minis = False
		self.tileset = None # type: Tileset | None
		self.file = None # type: str | None
		self.edited = False
		self.megatile = None

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		def save_as(): # type: () -> None
			self.saveas()
		self.toolbar.add_button(Assets.get_image('saveas'), save_as, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('find'), lambda *_: self.choose(TileType.group), 'MegaTile Group Palette', Ctrl.p, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.sets, "Manage Settings", Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.cv5 editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyTILE')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		# self.disable = [] # type: list[Widget]

		self.megatilee = IntegerVar(0,[0,4095],callback=lambda id: self.change(TileType.mega, int(id)))

		self.group_type = IntegerVar(0,[0,65535],callback=self.group_type_changed)
		self.group_flags = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.group_edge_left_or_overlay_id = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.group_edge_up_or_scr = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.group_edge_right_or_string_id = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.group_edge_down_or_unknown4 = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.group_piece_left_or_dddata_id = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.group_piece_up_or_width = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.group_piece_right_or_height = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.group_piece_down_or_unknown8 = IntegerVar(0,[0,65535],callback=self.group_values_changed)

		self.doodad = BooleanVar()
		self.doodad.set(False)
		self.doodad.trace('w', self.group_doodad_changed)

		self.apply_all_exclude_nulls = IntVar()
		self.apply_all_exclude_nulls.set(self.settings.mega_edit.get('apply_all_exclude_nulls', True))

		self.options_copy_mega = CopyOptions('mega', self.settings, self.action_states)
		self.copy_mega_height = self.options_copy_mega.option('height')
		self.copy_mega_walkable = self.options_copy_mega.option('walkable')
		self.copy_mega_sight = self.options_copy_mega.option('sight')
		self.copy_mega_ramp = self.options_copy_mega.option('ramp')

		self.options_copy_tilegroup = CopyOptions('tilegroup', self.settings, self.action_states)
		self.copy_tilegroup_walkability = self.options_copy_tilegroup.option('walkability')
		self.copy_tilegroup_buildability = self.options_copy_tilegroup.option('buildability')
		self.copy_tilegroup_creep = self.options_copy_tilegroup.option('creep')
		self.copy_tilegroup_height = self.options_copy_tilegroup.option('height')
		self.copy_tilegroup_misc = self.options_copy_tilegroup.option('misc')
		self.copy_tilegroup_unknown = self.options_copy_tilegroup.option('unknown')
		self.copy_tilegroup_edge_types = self.options_copy_tilegroup.option('edge_types')
		self.copy_tilegroup_piece_types = self.options_copy_tilegroup.option('piece_types')
		self.copy_tilegroup_group_type = self.options_copy_tilegroup.option('group_type')

		self.options_copy_doodadgroup = CopyOptions('doodadgroup', self.settings, self.action_states)
		self.copy_doodadgroup_doodad = self.options_copy_doodadgroup.option('doodad')
		self.copy_doodadgroup_overlay = self.options_copy_doodadgroup.option('overlay')
		self.copy_doodadgroup_walkability = self.options_copy_doodadgroup.option('walkability')
		self.copy_doodadgroup_buildability = self.options_copy_doodadgroup.option('buildability')
		self.copy_doodadgroup_creep = self.options_copy_doodadgroup.option('creep')
		self.copy_doodadgroup_height = self.options_copy_doodadgroup.option('height')
		self.copy_doodadgroup_misc = self.options_copy_doodadgroup.option('misc')
		self.copy_doodadgroup_unknown = self.options_copy_doodadgroup.option('unknown')
		self.copy_doodadgroup_scr = self.options_copy_doodadgroup.option('scr')
		self.copy_doodadgroup_name = self.options_copy_doodadgroup.option('name')

		mid = Frame(self)
		self.palette = TilePaletteView(mid, self, TileType.group, multiselect=False, sub_select=True)
		self.palette.pack(side=LEFT, fill=Y)

		settings = Frame(mid)
		self.groupid = LabelFrame(settings, text='MegaTile Group')
		self.flow_view = FlowView(self.groupid, width=300)
		self.flow_view.pack(fill=BOTH, expand=1, padx=2)

		self.normal_editors = [] # type: list[EditorGroup]
		walkability_editor = EditorGroup(self.flow_view.content_view, 'Walkability')\
			.check_flag('Walkable*', '*Gets overwritten by SC based on minitile flags', self.group_flags, CV5Flag.walkable).add()\
			.check_flag('Unwalkable*', '*Gets overwritten by SC based on minitile flags', self.group_flags, CV5Flag.unwalkable).add()
		self.normal_editors.append(walkability_editor)
		buildability_editor = EditorGroup(self.flow_view.content_view, 'Buildability')\
			.check_flag('Unbuildable', 'No buildings buildable', self.group_flags, CV5Flag.unbuildable).add()\
			.check_flag('Occupied', 'Unbuildable until a building on this tile gets removed', self.group_flags, CV5Flag.occupied).add()\
			.check_flag('Special', 'Allow Beacons/Start Locations to be placeable', self.group_flags, CV5Flag.special_placeable).add()
		self.normal_editors.append(buildability_editor)
		self.normal_editors.append(
			EditorGroup(self.flow_view.content_view, 'Creep')
			.check_flag('Creep', 'Zerg can build here when this flag is combined with the Temporary creep flag', self.group_flags, CV5Flag.creep).add()
			.check_flag('Receding', 'Receding creep', self.group_flags, CV5Flag.creep_receding).add()
			.check_flag('Temporary', 'Zerg can build here when this flag is combined with the Creep flag', self.group_flags, CV5Flag.creep_temp).add()
		)
		height_editor = EditorGroup(self.flow_view.content_view, 'Height')\
			.check_flag('Mid Ground*', '*Gets overwritten by SC based on minitile flags', self.group_flags, CV5Flag.mid_ground).add()\
			.check_flag('High Ground*', '*Gets overwritten by SC based on minitile flags (priority over Mid Ground)', self.group_flags, CV5Flag.high_ground).add()
		self.normal_editors.append(height_editor)
		self.normal_editors.append(
			EditorGroup(self.flow_view.content_view, 'Misc.')
			.check_flag('Has Doodad Cover', 'Provides cover for hit calculations', self.group_flags, CV5Flag.has_doodad_cover).add()
			.check_flag('Blocks View*', '*Gets overwritten by SC based on minitile flags', self.group_flags, CV5Flag.blocks_view).add()
			.check_flag('Cliff Edge*', '*Gets overwritten by SC based on minitile flagsg', self.group_flags, CV5Flag.cliff_edge).add()
		)
		self.normal_editors.append(
			EditorGroup(self.flow_view.content_view, 'Unknown')
			.check_flag('0002', 'Unknown/unused flag 0x0002', self.group_flags, CV5Flag.unknown_0002).add()
			.check_flag('0008', 'Unknown/unused flag 0x0008', self.group_flags, CV5Flag.unknown_0008).add()
			.check_flag('0020', 'Unknown/unused flag 0x0020', self.group_flags, CV5Flag.unknown_0020).add()
		)
		self.normal_editors.append(
			EditorGroup(self.flow_view.content_view, 'Edge Types*', '*Unsure if StarEdit actually uses these, or if they are just reference/outdated values.')
			.label('Left').add(new_row=False).entry('What tile types can be to the left of tiles in this group.', self.group_edge_left_or_overlay_id).add(new_row=False)
			.label('Up').add(new_row=False).entry('What tile types can be above tiles in this group.', self.group_edge_up_or_scr).add()
			.label('Right').add(new_row=False).entry('What tile types can be to the left of tiles in this group.', self.group_edge_right_or_string_id).add(new_row=False)
			.label('Down').add(new_row=False).entry('What tile types can be below tiles in this group.', self.group_edge_down_or_unknown4).add()
		)
		self.normal_editors.append(
			EditorGroup(self.flow_view.content_view, 'Piece Types*', 'A value of 0 can match any appropriate tile, otherwise the edge only pairs with a matching Terrain Piece Type value and tile index.\n*Unsure if StarEdit actually uses these, or if they are just reference/outdated values.')
			.label('Left').add(new_row=False).entry('Edge only pairs with a matching Terrain Piece Type value and tile index on the left.', self.group_piece_left_or_dddata_id).add(new_row=False)
			.label('Up').add(new_row=False).entry('Edge only pairs with a matching Terrain Piece Type value and tile index above.', self.group_piece_up_or_width).add()
			.label('Right').add(new_row=False).entry('Edge only pairs with a matching Terrain Piece Type value and tile index on the right.', self.group_piece_right_or_height).add(new_row=False)
			.label('Down').add(new_row=False).entry('Edge only pairs with a matching Terrain Piece Type value and tile index below.', self.group_piece_down_or_unknown8).add()
		)
		group_type_editor = EditorGroup(self.flow_view.content_view, 'Group')\
			.label('Type').add(new_row=False).entry('0 for unused/unplaceable, 1 for doodads, 2+ for basic terrain and edges', self.group_type).add()\
			.check('Doodad', 'Whether this group is a doodad group or not.', self.doodad).add(span=2)
		self.normal_editors.append(group_type_editor)

		megatile_editor = EditorGroup(self.flow_view.content_view, 'MegaTile')
		megatile_group = Frame(megatile_editor.content)
		megatile_editors = [] # type: list[Widget]
		f = Frame(megatile_group)
		Label(f, text='ID:').pack(side=LEFT)
		megatile_editors.append(Entry(f, textvariable=self.megatilee, font=Font.fixed(), width=len(str(self.megatilee.range[1])), state=DISABLED))
		megatile_editors[-1].pack(side=LEFT, padx=2)
		Tooltip(megatile_editors[-1], 'MegaTile ID:\nID for the selected MegaTile in the current MegaTile Group')
		megatile_editors.append(Button(f, image=Assets.get_image('find'), width=20, height=20, command=lambda: self.choose(TileType.mega), state=DISABLED))
		megatile_editors[-1].pack(side=LEFT, padx=2)
		Tooltip(megatile_editors[-1], 'MegaTile Palette')
		f.pack(side=TOP, fill=X, padx=3)
		def megatile_apply_all_pressed():
			menu = Menu(self, tearoff=0)
			mode = self.mega_editor.get_edit_mode()
			name = [None,None,'Height','Walkability','Blocks View','Ramp(?)'][mode.value]
			menu.add_command(label="Apply %s flags to Megatiles in Group (Control+Shift+%s)" % (name, name[0]), command=lambda m=mode: self.megatile_apply_all(mode))
			menu.add_command(label="Apply all flags to Megatiles in Group (Control+Shift+A)", command=self.megatile_apply_all)
			menu.add_separator()
			menu.add_checkbutton(label="Exclude Null Tiles (Control+Shift+N)", variable=self.apply_all_exclude_nulls)
			menu.post(*self.winfo_pointerxy())
		self.apply_all_btn = Button(megatile_group, text='Apply to Megas', state=DISABLED, command=megatile_apply_all_pressed)
		megatile_editors.append(self.apply_all_btn)
		self.apply_all_btn.pack(side=BOTTOM, padx=3, pady=(0,3), fill=X)
		self.bind(Shift.Ctrl.h(), lambda *_: self.megatile_apply_all(MegaEditorView.Mode.height))
		self.bind(Shift.Ctrl.w(), lambda *_: self.megatile_apply_all(MegaEditorView.Mode.walkability))
		self.bind(Shift.Ctrl.b(), lambda *_: self.megatile_apply_all(MegaEditorView.Mode.view_blocking))
		self.bind(Shift.Ctrl.r(), lambda *_: self.megatile_apply_all(MegaEditorView.Mode.ramp))
		self.bind(Shift.Ctrl.a(), lambda *_: self.megatile_apply_all(None))
		self.bind(Shift.Ctrl.n(), lambda *_: self.apply_all_exclude_nulls.set(not self.apply_all_exclude_nulls.get()))
		self.mega_editor = MegaEditorView(megatile_group, self.settings, self, palette_editable=True)
		self.mega_editor.set_enabled(False)
		self.mega_editor.pack(side=TOP, padx=3, pady=(3,0))
		megatile_editor.widget(megatile_group, megatile_editors).add()
		self.normal_editors.append(megatile_editor)

		def copy_mega(*args):
			if not self.tileset:
				return
			options = {
				'megatiles_export_height': self.copy_mega_height.get(),
				'megatiles_export_walkability': self.copy_mega_walkable.get(),
				'megatiles_export_block_sight': self.copy_mega_sight.get(),
				'megatiles_export_ramp': self.copy_mega_ramp.get(),
			}
			if not max(options.values()):
				return
			group = self.tileset.cv5.groups[self.palette.selected[0]]
			mega = group[13][self.palette.sub_selection]
			f = io.StringIO()
			self.tileset.export_settings(TileType.mega, f, [mega], options)
			self.clipboard_clear()
			self.clipboard_append(f.getvalue())
		def paste_mega(*args):
			if not self.tileset:
				return
			group = self.tileset.cv5.groups[self.palette.selected[0]]
			mega = group[13][self.palette.sub_selection]
			settings = self.clipboard_get()
			try:
				self.tileset.import_settings(TileType.mega, settings, [mega])
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.mega_editor.draw()
			self.mark_edited()
		copy_mega_editor = EditorGroup(self.flow_view.content_view, 'Copy MegaTile Flags')\
			.check('Height', 'Copy Height settings for MegaTile', self.copy_mega_height).add()\
			.check('Walkable', 'Copy Walkable settings for MegaTile', self.copy_mega_walkable).add()\
			.check('Blocks Sight', 'Copy Blocks Sight settings for MegaTile', self.copy_mega_sight).add()\
			.check('Ramp', 'Copy Ramp settings for MegaTile', self.copy_mega_ramp).add()
		copy_mega_btn = copy_mega_editor.button('Copy (%s)' % Shift.Ctrl.c.description(), 'Copy chosen settings to clipboard', copy_mega)
		self.copy_mega_btn = copy_mega_btn.widget
		copy_mega_btn.add()
		copy_mega_editor.button('Paste (%s)' % Shift.Ctrl.v.description(), 'Paste settings from clipboard', paste_mega).add()
		self.normal_editors.append(copy_mega_editor)
		self.bind(Shift.Ctrl.c(), copy_mega)
		self.bind(Shift.Ctrl.v(), paste_mega)
	
		def copy_tilegroup(*args): # type: (Any) -> None
			if not self.tileset:
				return
			group = self.palette.selected[0]
			fields: Serialize.Fields
			if self.doodad.get():
				if not self.options_copy_doodadgroup.any_enabled():
					return
				fields = {
					DoodadGroupField.flags: {
						DoodadGroupField.Flag.walkable: self.copy_doodadgroup_walkability.get(),
						DoodadGroupField.Flag.unknown_0002: self.copy_doodadgroup_unknown.get(),
						DoodadGroupField.Flag.unwalkable: self.copy_doodadgroup_walkability.get(),
						DoodadGroupField.Flag.unknown_0008: self.copy_doodadgroup_unknown.get(),
						DoodadGroupField.Flag.has_doodad_cover: self.copy_doodadgroup_misc.get(),
						DoodadGroupField.Flag.unknown_0020: self.copy_doodadgroup_unknown.get(),
						DoodadGroupField.Flag.creep: self.copy_doodadgroup_creep.get(),
						DoodadGroupField.Flag.unbuildable: self.copy_doodadgroup_buildability.get(),
						DoodadGroupField.Flag.blocks_view: self.copy_doodadgroup_misc.get(),
						DoodadGroupField.Flag.mid_ground: self.copy_doodadgroup_height.get(),
						DoodadGroupField.Flag.high_ground: self.copy_doodadgroup_height.get(),
						DoodadGroupField.Flag.occupied: self.copy_doodadgroup_buildability.get(),
						DoodadGroupField.Flag.has_overlay_sprite: self.copy_doodadgroup_overlay.get(),
						DoodadGroupField.Flag.has_overlay_unit: self.copy_doodadgroup_overlay.get(),
						DoodadGroupField.Flag.overlay_flipped: self.copy_doodadgroup_overlay.get(),
						DoodadGroupField.Flag.special_placeable: self.copy_doodadgroup_buildability.get()
					},
					DoodadGroupField.overlay_id: self.copy_doodadgroup_overlay.get(),
					DoodadGroupField.scr: self.copy_doodadgroup_scr.get(),
					DoodadGroupField.string_id: self.copy_doodadgroup_name.get(),
					DoodadGroupField.unknown4: self.copy_doodadgroup_unknown.get(),
					DoodadGroupField.dddata_id: self.copy_doodadgroup_doodad.get(),
					DoodadGroupField.width: self.copy_doodadgroup_doodad.get(),
					DoodadGroupField.height: self.copy_doodadgroup_doodad.get(),
					DoodadGroupField.unknown8: self.copy_doodadgroup_unknown.get(),
				}
			else:
				if not self.options_copy_tilegroup.any_enabled():
					return
				fields = {
					TileGroupField.type: self.copy_tilegroup_group_type.get(),
					TileGroupField.flags: {
						TileGroupField.Flag.walkable: self.copy_tilegroup_walkability.get(),
						TileGroupField.Flag.unknown_0002: self.copy_tilegroup_unknown.get(),
						TileGroupField.Flag.unwalkable: self.copy_tilegroup_walkability.get(),
						TileGroupField.Flag.unknown_0008: self.copy_tilegroup_unknown.get(),
						TileGroupField.Flag.has_doodad_cover: self.copy_tilegroup_misc.get(),
						TileGroupField.Flag.unknown_0020: self.copy_tilegroup_unknown.get(),
						TileGroupField.Flag.creep: self.copy_tilegroup_creep.get(),
						TileGroupField.Flag.unbuildable: self.copy_tilegroup_buildability.get(),
						TileGroupField.Flag.blocks_view: self.copy_tilegroup_misc.get(),
						TileGroupField.Flag.mid_ground: self.copy_tilegroup_height.get(),
						TileGroupField.Flag.high_ground: self.copy_tilegroup_height.get(),
						TileGroupField.Flag.occupied: self.copy_tilegroup_buildability.get(),
						TileGroupField.Flag.creep_receding: self.copy_tilegroup_creep.get(),
						TileGroupField.Flag.cliff_edge: self.copy_tilegroup_misc.get(),
						TileGroupField.Flag.creep_temp: self.copy_tilegroup_creep.get(),
						TileGroupField.Flag.special_placeable: self.copy_tilegroup_buildability.get()
					},
					TileGroupField.edge: self.copy_tilegroup_edge_types.get(),
					TileGroupField.piece: self.copy_tilegroup_piece_types.get(),
				}
			f = io.StringIO()
			self.tileset.export_group_settings(f, [group], fields)
			self.clipboard_clear()
			self.clipboard_append(f.getvalue())
		def paste_tilegroup(*args): # type: (Any) -> None
			if not self.tileset:
				return
			group = self.palette.selected[0]
			settings = self.clipboard_get()
			try:
				self.tileset.import_group_settings(settings, [group])
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.megaload()
			self.mark_edited()
		copy_tilegroup_settings_editor = EditorGroup(self.flow_view.content_view, 'Copy Group Settings')\
			.check('Walkability', 'Copy settings from Walkability', self.copy_tilegroup_walkability).add(new_row=False)\
			.check('Buildability', 'Copy settings from Buildability', self.copy_tilegroup_buildability).add()\
			.check('Creep', 'Copy settings from Creep', self.copy_tilegroup_creep).add(new_row=False)\
			.check('Height', 'Copy settings from Height', self.copy_tilegroup_height).add()\
			.check('Misc.', 'Copy settings from Misc.', self.copy_tilegroup_misc).add(new_row=False)\
			.check('Unknown', 'Copy settings from Unknown', self.copy_tilegroup_unknown).add()\
			.check('Edge Types', 'Copy settings from Edge Types', self.copy_tilegroup_edge_types).add(new_row=False)\
			.check('Piece Types', 'Copy settings from Piece Types', self.copy_tilegroup_piece_types).add()\
			.check('Group Type', 'Copy Group Type setting', self.copy_tilegroup_group_type).add()
		copy_tilegroup_btn = copy_tilegroup_settings_editor.button('Copy (%s)' % Ctrl.Alt.c.description(), 'Copy chosen settings to clipboard', copy_tilegroup)
		self.copy_tilegroup_btn = copy_tilegroup_btn.widget
		copy_tilegroup_btn.add(new_row=False)
		copy_tilegroup_settings_editor.button('Paste (%s)' % Ctrl.Alt.v.description(), 'Paste settings from clipboard', paste_tilegroup).add()
		self.normal_editors.append(copy_tilegroup_settings_editor)
		self.bind(Ctrl.Alt.c(), copy_tilegroup)
		self.bind(Ctrl.Alt.v(), paste_tilegroup)

		self.doodad_editors = [] # type: list[EditorGroup]
		self.doodad_editors.append(
			EditorGroup(self.flow_view.content_view, 'Doodad')
			.label('ID').add(new_row=False).entry('Each doodad must have a unique Doodad ID.\nAll MegaTile Groups in the doodad must have the same ID.', self.group_piece_left_or_dddata_id).add()
			.label('Width').add(new_row=False).entry('Total width of the doodad in MegaTiles', self.group_piece_up_or_width).add()
			.label('Height').add(new_row=False).entry('Total height of the doodad in MegaTiles', self.group_piece_right_or_height).add()
		)
		self.doodad_editors.append(
			EditorGroup(self.flow_view.content_view, 'Overlay')
			.label('ID').add(new_row=False).entry('Sprite or Unit ID (depending on the following flags) for the overlay', self.group_edge_left_or_overlay_id).add(new_row=False)
			.radio_flag('None', 'No overlay', self.group_flags, 0, mask=CV5DoodadFlag.has_overlay_sprite | CV5DoodadFlag.has_overlay_unit).add(span=2)
			.check_flag('Flipped*', 'The overlay is flipped. (*Unused)\n*Not cleared SC, so this flag also counts as Temporary creep', self.group_flags, CV5DoodadFlag.overlay_flipped).add(span=2, new_row=False)
			.radio_flag('Sprites.dat*', 'The overlay ID is a Sprites.dat reference.\n*Not cleared by SC, so this flag also counts as Receding creep', self.group_flags, CV5DoodadFlag.has_overlay_sprite, mask=CV5DoodadFlag.has_overlay_sprite | CV5DoodadFlag.has_overlay_unit).add(span=2)
			.skip(2).radio_flag('Units.dat', 'The overlay ID is a Units.dat reference', self.group_flags, CV5DoodadFlag.has_overlay_unit, mask=CV5DoodadFlag.has_overlay_sprite | CV5DoodadFlag.has_overlay_unit).add()
		)
		self.doodad_editors.append(walkability_editor)
		self.doodad_editors.append(buildability_editor)
		self.doodad_editors.append(
			EditorGroup(self.flow_view.content_view, 'Creep')
			.check_flag('Creep', 'Zerg can build here when this flag is combined with the Temporary creep flag', self.group_flags, CV5Flag.creep).add()
			.check_flag('Receding*', 'Receding creep\n*Overlaps with Has Overlay Sprites.dat flag', self.group_flags, CV5Flag.creep_receding, editable=False).add()
			.check_flag('Temporary*', 'Zerg can build here when this flag is combined with the Creep flag\n*Overlaps with Has Overlay Flipped flag', self.group_flags, CV5Flag.creep_temp, editable=False).add()
		)
		self.doodad_editors.append(height_editor)
		self.doodad_editors.append(
			EditorGroup(self.flow_view.content_view, 'Misc.')
			.check_flag('Has Doodad Cover', 'Provides cover for hit calculations', self.group_flags, CV5Flag.has_doodad_cover).add()
			.check_flag('Blocks View*', '*Gets overwritten by SC based on minitile flags', self.group_flags, CV5Flag.blocks_view).add()
			.check_flag('Cliff Edge*', '*Overlaps with Has Overlay Units.dat flag', self.group_flags, CV5Flag.cliff_edge, editable=False).add()
		)
		self.doodad_editors.append(
			EditorGroup(self.flow_view.content_view, 'Unknown')
			.label('Unknown 4').add(new_row=False).entry('Unknown/unused', self.group_edge_down_or_unknown4).add(new_row=False)
			.check_flag('0002', 'Unknown/unused flag 0x0002', self.group_flags, CV5Flag.unknown_0002).add(span=2)
			.label('Unknown 8').add(new_row=False).entry('Unknown/unused', self.group_piece_down_or_unknown8).add(new_row=False)
			.check_flag('0008', 'Unknown/unused flag 0x0008', self.group_flags, CV5Flag.unknown_0008).add(span=2)
			.skip(2).check_flag('0020', 'Unknown/unused flag 0x0020', self.group_flags, CV5Flag.unknown_0020).add(span=2)
		)
		self.doodad_editors.append(group_type_editor)
		self.doodad_editors.append(
			EditorGroup(self.flow_view.content_view, 'SC:R')
			.check_flag('SC:R', 'Added in StarCraft: Remastered', self.group_edge_up_or_scr, CV5Group.SCR).add(span=2)
			.label('Raw').add(new_row=False).entry('Raw value of added in StarCraft: Remastered (1 = Added in SC:R)', self.group_edge_up_or_scr).add()
		)
		self.doodad_editors.append(
			EditorGroup(self.flow_view.content_view, 'Name')
			.label('String').add(new_row=False).dropdown('Doodad group string from stat_txt.tbl',['None'] + [TBL.decompile_string(s) for s in self.stat_txt.strings], self.group_edge_right_or_string_id).add(sticky=EW, weight=1)
			.label('Raw').add(new_row=False).entry('Doodad group string from stat_txt.tbl', self.group_edge_right_or_string_id).add()
		)
		self.doodad_editors.append(
			EditorGroup(self.flow_view.content_view, 'Other')
			.button('Placeability', 'Modify which megatile groups the doodad must be placed on.', self.placeability).add(sticky=EW)
			.button('Apply All', 'Apply these MegaTile Group settings to all the MegaTile Groups with the same Doodad ID', self.doodad_apply_all).add(sticky=EW)
		)
		self.doodad_editors.append(megatile_editor)
		self.doodad_editors.append(copy_mega_editor)

		copy_doodadgroup_editor = EditorGroup(self.flow_view.content_view, 'Copy Group Settings')\
			.check('Doodad', 'Copy settings from Doodad', self.copy_doodadgroup_doodad).add(new_row=False)\
			.check('Overlay', 'Copy settings from Overlay', self.copy_doodadgroup_overlay).add()\
			.check('Walkability', 'Copy settings from Walkability', self.copy_doodadgroup_walkability).add(new_row=False)\
			.check('Buildability', 'Copy settings from Buildability', self.copy_doodadgroup_buildability).add()\
			.check('Creep', 'Copy settings from Creep', self.copy_doodadgroup_creep).add(new_row=False)\
			.check('Height', 'Copy settings from Height', self.copy_doodadgroup_height).add()\
			.check('Misc.', 'Copy settings from Misc.', self.copy_doodadgroup_misc).add(new_row=False)\
			.check('Unknown', 'Copy settings from Unknown', self.copy_doodadgroup_unknown).add()\
			.check('SC:R', 'Copy settings from SC:R', self.copy_doodadgroup_scr).add()\
			.check('Name', 'Copy settings from Name', self.copy_doodadgroup_name).add()
		copy_doodadgroup_btn = copy_doodadgroup_editor.button('Copy (%s)' % Ctrl.Alt.c.description(), 'Copy chosen settings to clipboard', copy_tilegroup)
		self.copy_doodadgroup_btn = copy_doodadgroup_btn.widget
		copy_doodadgroup_btn.add(new_row=False)
		copy_doodadgroup_editor.button('Paste (%s)' % Ctrl.Alt.v.description(), 'Paste settings from clipboard', paste_tilegroup).add()
		self.doodad_editors.append(copy_doodadgroup_editor)

		self.update_editor(force=True)

		self.groupid.pack(fill=BOTH, expand=1, padx=5, pady=5)
		settings.pack(side=LEFT, fill=BOTH, expand=1)
		mid.pack(fill=BOTH, expand=1)

		#Statusbar
		self.status = StringVar()
		self.expanded = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, width=45, anchor=W).pack(side=LEFT, padx=1)
		self.editstatus = Label(statusbar, image=Assets.get_image('save'), bd=0, state=DISABLED)
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, textvariable=self.expanded, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load a Tileset.')
		statusbar.pack(side=BOTTOM, fill=X)

		self.settings.windows.load_window_size('main', self)

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyTILE')

	def get_tileset(self): # type: () -> (Tileset | None)
		return self.tileset

	def tile_palette_binding_widget(self): # type: () -> Self
		return self

	def tile_palette_bind_updown(self): # type: () -> bool
		return False

	def tile_palette_selection_changed(self): # type: () -> None
		self.megaload()

	def is_file_open(self): # type: () -> bool
		return not not self.tileset

	def check_saved(self): # type: () -> CheckSaved
		if not self.is_file_open() or not self.edited:
			return CheckSaved.saved
		file = self.file
		if not file:
			file = 'Unnamed.cv5'
		save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
		if save != MessageBox.NO:
			if save == MessageBox.CANCEL:
				return CheckSaved.cancelled
			if self.file:
				self.save()
			else:
				return self.saveas()
		return CheckSaved.saved

	def action_states(self, *args, **kwargs): # type: (Any, Any) -> None
		is_file_open = self.is_file_open()

		self.toolbar.tag_enabled('file_open', is_file_open)
		for editor in self.normal_editors + self.doodad_editors:
			editor.enabled(is_file_open)
		self.mega_editor.set_enabled(is_file_open)

		if is_file_open and cast(Tileset, self.tileset).vx4.is_expanded():
			self.expanded.set('VX4 Expanded')
		
		can_copy_mega = is_file_open and self.options_copy_mega.any_enabled()
		self.copy_mega_btn['state'] = NORMAL if can_copy_mega else DISABLED

		can_copy_group = is_file_open and self.options_copy_tilegroup.any_enabled()
		self.copy_tilegroup_btn['state'] = NORMAL if can_copy_group else DISABLED

		can_copy_doodadgroup = is_file_open and self.options_copy_doodadgroup.any_enabled()
		self.copy_doodadgroup_btn['state'] = NORMAL if can_copy_doodadgroup else DISABLED

	def mark_edited(self, edited=True): # type: (bool) -> None
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def get_tile(self, id_or_minitile): # type: (int | VX4Minitile) -> Image
		if id_or_minitile in TilePalette.TILE_CACHE:
			return TilePalette.TILE_CACHE[id_or_minitile]
		assert self.tileset is not None
		if isinstance(id_or_minitile, VX4Minitile):
			image = minitile_to_photo(self.tileset, id_or_minitile)
		else:
			image = megatile_to_photo(self.tileset, id_or_minitile)
		TilePalette.TILE_CACHE[id_or_minitile] = image
		return image

	def megatile_apply_all(self, mode=None): # type: (MegaEditorView.Mode | None) -> None
		if not self.tileset:
			return
		copy_mask = ~0
		if mode == MegaEditorView.Mode.height:
			copy_mask = VF4Flag.mid_ground | VF4Flag.high_ground
		elif mode == MegaEditorView.Mode.walkability:
			copy_mask = VF4Flag.walkable
		elif mode == MegaEditorView.Mode.view_blocking:
			copy_mask = VF4Flag.blocks_sight
		elif mode == MegaEditorView.Mode.ramp:
			copy_mask = VF4Flag.ramp
		copy_megatile_id = self.tileset.cv5.get_group(self.palette.selected[0]).megatile_ids[self.palette.sub_selection]
		edited = False
		copy_megatile = self.tileset.vf4.get_megatile(copy_megatile_id)
		for megatile_id in self.tileset.cv5.get_group(self.palette.selected[0]).megatile_ids:
			if megatile_id == copy_megatile_id or (megatile_id == 0 and self.apply_all_exclude_nulls.get()):
				continue
			megatile = self.tileset.vf4.get_megatile(megatile_id)
			for n in range(16):
				new_flags = (megatile.flags[n] & ~copy_mask) | (copy_megatile.flags[n] & copy_mask)
				if new_flags != megatile.flags[n]:
					megatile.flags[n] = new_flags
					edited = True
		if edited:
			self.mark_edited()

	def doodad_apply_all(self): # type: () -> None
		if not self.tileset:
			return
		doodad_id = self.group_piece_left_or_dddata_id.get()
		copy_group = self.tileset.cv5.get_group(self.palette.selected[0])
		for group_id in range(self.tileset.cv5.group_count()):
			group = self.tileset.cv5.get_group(group_id)
			if not group.type == CV5Group.TYPE_DOODAD:
				continue
			if group_id != self.palette.selected[0] and group.doodad_dddata_id == doodad_id:
				group.update_settings(copy_group)

	def mega_edit_mode_updated(self, mode): # type: (MegaEditorView.Mode) -> None
		if mode == MegaEditorView.Mode.mini or mode == MegaEditorView.Mode.flip:
			self.apply_all_btn.pack_forget()
		else:
			self.apply_all_btn.pack()

	def update_group_label(self): # type: () -> None
		if not self.tileset:
			return
		group = self.tileset.cv5.get_group(self.palette.selected[0])
		d = ['',' - Doodad'][group.type == CV5Group.TYPE_DOODAD]
		self.groupid['text'] = 'MegaTile Group [%s%s]' % (self.palette.selected[0], d)
 
	def update_editor(self, doodad=False, force=False): # type: (bool, bool) -> None
		if self.doodad.get() == doodad and not force:
			return
		if doodad:
			editors = self.doodad_editors
		else:
			editors = self.normal_editors
		self.flow_view.remove_all_subviews()
		for editor in editors:
			self.flow_view.add_subview(editor.container, padx=2, weight=editor.weight)
		self.doodad.set(doodad)

	def megaload(self): # type: () -> None
		if not self.tileset:
			return
		self.loading_megas = True
		group = self.tileset.cv5.get_group(self.palette.selected[0])
		mega = group.megatile_ids[self.palette.sub_selection]
		if self.megatilee.get() != mega:
			self.megatilee.set(mega)
		self.update_editor(group.type == CV5Group.TYPE_DOODAD)
		self.group_type.set(group.type)
		self.group_flags.set(group.flags)
		if group.type == CV5Group.TYPE_DOODAD:
			self.group_edge_left_or_overlay_id.set(group.doodad_overlay_id)
			self.group_edge_up_or_scr.set(group.doodad_scr)
			self.group_edge_right_or_string_id.set(group.doodad_string_id)
			self.group_edge_down_or_unknown4.set(group.doodad_unknown4)
			self.group_piece_left_or_dddata_id.set(group.doodad_dddata_id)
			self.group_piece_up_or_width.set(group.doodad_width)
			self.group_piece_right_or_height.set(group.doodad_height)
			self.group_piece_down_or_unknown8.set(group.doodad_unknown8)
		else:
			self.group_edge_left_or_overlay_id.set(group.basic_edge_left)
			self.group_edge_up_or_scr.set(group.basic_edge_up)
			self.group_edge_right_or_string_id.set(group.basic_edge_right)
			self.group_edge_down_or_unknown4.set(group.basic_edge_down)
			self.group_piece_left_or_dddata_id.set(group.basic_piece_left)
			self.group_piece_up_or_width.set(group.basic_piece_up)
			self.group_piece_right_or_height.set(group.basic_piece_right)
			self.group_piece_down_or_unknown8.set(group.basic_piece_down)
		self.miniload()
		self.update_group_label()
		self.loading_megas = False

	def miniload(self): # type: () -> None
		if not self.tileset:
			return
		self.mega_editor.set_megatile(self.tileset.cv5.get_group(self.palette.selected[0]).megatile_ids[self.palette.sub_selection])

	def group_type_changed(self, *_): # type: (Any) -> None
		pass

	def group_doodad_changed(self, *_): # type: (Any) -> None
		pass

	def group_values_changed(self, *_): # type: (Any) -> None
		if not self.tileset or self.loading_megas:
			return
		group = self.tileset.cv5.get_group(self.palette.selected[0])
		# TODO: Save settings
		# group[0] = self.index.get()
		# if self.palette.selected[0] >= 1024:
		# 	o = [self.buildable,self.flags,self.buildable2,self.groundheight,self.hasup,self.hasdown,self.edgeleft,self.unknown9,self.edgeright,self.edgeup,self.edgedown,self.unknown11]
		# else:
		# 	o = [self.buildable,self.flags,self.buildable2,self.groundheight,self.edgeleft,self.edgeup,self.edgeright,self.edgedown,self.unknown9,self.hasup,self.unknown11,self.hasdown]
		# for n,v in enumerate(o):
		# 	group[n+1] = v.get()
		self.mark_edited()

	def choose(self, tile_type): # type: (TileType) -> None
		if not self.tileset:
			return
		TilePalette(
			self,
			self.settings,
			self,
			tile_type,
			self.palette.selected[0] if tile_type == TileType.group else self.tileset.cv5.get_group(self.palette.selected[0]).megatile_ids[self.palette.sub_selection],
			editing=True
		)

	def change(self, tiletype, id): # type: (TileType, int) -> None
		if not self.tileset:
			return
		if tiletype == TileType.group:
			self.palette.select(id, sub_select=0, scroll_to=True)
		elif tiletype == TileType.mega and not self.loading_megas:
			self.tileset.cv5.get_group(self.palette.selected[0]).megatile_ids[self.palette.sub_selection] = id
			self.palette.draw_tiles(force=True)
			self.mega_editor.set_megatile(id)
			self.mark_edited()

	def placeability(self): # type: () -> None
		Placeability(self, self.settings, self, self.group_piece_left_or_dddata_id.get())

	def update_ranges(self): # type: () -> None
		if not self.tileset:
			return
		self.megatilee.setrange([0,self.tileset.vf4.megatile_count()-1])
		self.mega_editor.update_mini_range()
		self.palette.update_size()
		self.palette.draw_tiles(force=True)

	def open(self, key=None, file=None): # type: (Any, str | None) -> None
		if self.check_saved() == CheckSaved.cancelled:
			return
		if file is None:
			file = self.settings.lastpath.tileset.select_open_file(self, title='Open Complete Tileset', filetypes=[FileType.cv5()])
			if not file:
				return
		tileset = Tileset()
		try:
			tileset.load_file(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.tileset = tileset
		self.file = file
		self.status.set('Load successful!')
		self.mark_edited(False)
		self.action_states()
		self.update_ranges()
		self.palette.update_size()
		self.palette.select(0)
		if self.tileset.vx4.is_expanded():
			self.settings.dont_warn.warn('expanded_vx4', self, "This tileset is using an expanded vx4 file (vx4ex). This could be a Remastered tileset, and/or will require a 'VX4 Expander Plugin' for pre-Remastered.")

	def save(self, key=None): # type: (Any) -> None
		self.saveas(file_path=self.file)

	def saveas(self, key=None, file_path=None): # type: (Any, str | None) -> CheckSaved
		if not self.tileset:
			return CheckSaved.saved
		if not file_path:
			file_path = self.settings.lastpath.tileset.select_save_file(self, title='Save Tileset As', filetypes=[FileType.cv5()])
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		try:
			self.tileset.save_file(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
		self.file = file_path
		self.status.set('Save Successful!')
		self.mark_edited(False)
		return CheckSaved.saved

	def close(self, key=None): # type: (Any) -> None
		if not self.is_file_open():
			return
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.tileset = None
		self.file = None
		self.status.set('Load or create a Tileset.')
		self.mark_edited(False)
		self.groupid['text'] = 'MegaTile Group'
		self.update_editor()
		self.mega_editor.set_megatile(None)
		for v in [self.group_type,self.group_flags,self.group_edge_left_or_overlay_id,self.group_edge_up_or_scr,self.group_edge_right_or_string_id,self.group_edge_down_or_unknown4,self.group_piece_left_or_dddata_id,self.group_piece_up_or_width,self.group_piece_right_or_height,self.group_piece_down_or_unknown8]:
			v.set(0)
		self.palette.draw_tiles()
		self.action_states()

	def register_registry(self, e=None): # type: (Any) -> None
		try:
			register_registry('PyTILE', 'cv5', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def sets(self, key=None, err=None): # type: (Any, Exception | None) -> None
		SettingsDialog(self, [('Theme',)], (550,380), err, settings=self.settings)

	def help(self, e=None): # type: (Any) -> None
		HelpDialog(self, self.settings, 'Help/Programs/PyTILE.md')

	def about(self, key=None): # type: (Any) -> None
		AboutDialog(self, 'PyTILE', LONG_VERSION, [('FaRTy1billion','Tileset file specs and HawtTiles.')])

	def exit(self, e=None): # type: (Any) -> None
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.settings.windows.save_window_size('main', self)
		self.settings.mega_edit.apply_all_exclude_nulls = not not self.apply_all_exclude_nulls.get()
		self.options_copy_mega.save()
		self.options_copy_tilegroup.save()
		self.options_copy_doodadgroup.save()
		self.settings.save()
		self.destroy()
