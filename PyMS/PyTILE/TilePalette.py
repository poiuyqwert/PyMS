
from .Delegates import TilePaletteDelegate, TilePaletteViewDelegate, MegaEditorDelegate, MiniEditorDelegate, GraphicsImporterDelegate
from .TilePaletteView import TilePaletteView

from ..FileFormats.Tileset.Tileset import Tileset, TileType
from ..FileFormats.Tileset.CV5 import CV5Group
from ..FileFormats.Tileset.VX4 import VX4Megatile, VX4Minitile
from ..FileFormats.Tileset.VF4 import VF4Megatile

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Assets

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from ..Utilities.Settings import Settings

class TilePalette(PyMSDialog, TilePaletteViewDelegate, TilePaletteDelegate, MegaEditorDelegate, MiniEditorDelegate, GraphicsImporterDelegate):
	OPEN_PALETTE_COUNT = 0
	TILE_CACHE = {} # type: dict[int | VX4Minitile, Image]

	def __init__(self, parent, settings, delegate, tiletype=TileType.group, select=None, editing=False): # type: (Misc, Settings, TilePaletteDelegate, TileType, int | list[int] | None, bool) -> None
		TilePalette.OPEN_PALETTE_COUNT += 1
		self.settings = settings
		self.tiletype = tiletype
		self.start_selected = [] # type: list[int]
		if select is not None:
			if isinstance(select, list):
				self.start_selected.extend(sorted(select))
			else:
				self.start_selected.append(select)
		self.delegate = delegate
		self.editing = editing
		self.edited = False
		PyMSDialog.__init__(self, parent, self.get_title(), resizable=(tiletype != TileType.group,True), set_min_size=(True,True))

	def widgetize(self): # type: () -> None
		typename = ''
		smallertype = ''
		if self.tiletype == TileType.group:
			typename = 'MegaTile Groups'
			smallertype = 'MegaTiles'
		elif self.tiletype == TileType.mega:
			typename = 'MegaTiles'
			smallertype = 'MiniTiles'
		elif self.tiletype == TileType.mini:
			typename = 'MiniTiles'
		self.toolbar = None
		if self.editing:
			self.toolbar = Toolbar(self)
			self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add', Key.Insert, enabled=False, tags='can_add')
			if self.tiletype != TileType.mini:
				self.toolbar.add_section()
				self.toolbar.add_button(Assets.get_image('colors'), self.select_smaller, 'Select %s' % smallertype, Ctrl.m)
			if self.tiletype != TileType.group:
				self.toolbar.add_section()
				self.toolbar.add_button(Assets.get_image('edit'), self.edit, 'Edit %s' % typename, Key.Return)
			self.toolbar.add_spacer(20)
			self.toolbar.add_button(Assets.get_image('exportc'), self.export_graphics, 'Export %s Graphics' % typename, Ctrl.e, enabled=False, tags='has_selection')
			self.toolbar.add_button(Assets.get_image('importc'), self.import_graphics, 'Import %s Graphics' % typename, Ctrl.i)
			if self.tiletype != TileType.mini:
				self.toolbar.add_section()
				self.toolbar.add_button(Assets.get_image('export'), self.export_settings, 'Export %s Settings' % typename, Shift.Ctrl.e, enabled=False, tags='has_selection')
				self.toolbar.add_button(Assets.get_image('import'), self.import_settings, 'Import %s Settings' % typename, Shift.Ctrl.i)
			self.toolbar.pack(fill=X)

		self.palette = TilePaletteView(self, self, self.tiletype, self.start_selected)
		self.palette.pack(side=TOP, fill=BOTH, expand=1)

		self.status = StringVar()
		self.update_status()
		self.update_state()

		statusbar = StatusBar(self)
		statusbar.add_label(self.status)
		statusbar.pack(side=BOTTOM, fill=X)

	def get_tileset(self): # type: () -> (Tileset | None)
		return self.delegate.get_tileset()

	def get_tile(self, id): # type: (int | VX4Minitile) -> Image
		return self.delegate.get_tile(id)

	def tile_palette_binding_widget(self): # type: () -> Misc
		return self

	def tile_palette_double_clicked(self, id): # type: (int) -> None
		self.delegate.change(self.tiletype, id)
		self.ok()

	def tile_palette_bind_updown(self): # type: () -> bool
		return True

	def tile_palette_selection_changed(self): # type: () -> None
		self.update_status()
		self.update_state()
		self.palette.draw_selections()

	def change(self, tile_type, id): # type: (TileType, int) -> None
		pass

	def megaload(self): # type: () -> None
		pass

	def update_ranges(self): # type () -> None
		pass

	def setup_complete(self): # type: () -> None
		self.settings.windows.palette.load_window_size(('group','mega','mini')[self.tiletype.value], self)

	def select_smaller(self): # type: () -> None
		tileset = self.get_tileset()
		if not tileset:
			return
		ids = [] # type: list[int]
		for id in self.palette.selected:
			if self.tiletype == TileType.group:
				for sid in tileset.cv5.get_group(id).megatile_ids:
					if sid and not sid in ids:
						ids.append(sid)
			elif self.tiletype == TileType.mega:
				for minitile in tileset.vx4.get_megatile(id).minitiles:
					if not minitile.image_id in ids:
						ids.append(minitile.image_id)
		TilePalette(self, self.settings, self, TileType.mega if self.tiletype == TileType.group else TileType.mini, ids, editing=True)

	def mark_edited(self): # type: () -> None
		self.edited = True

	def get_title(self): # type: () -> str
		tileset = self.get_tileset()
		if not tileset:
			return 'Tile Palette'
		count = 0
		max_count = 0
		if self.tiletype == TileType.group:
			count = tileset.cv5.group_count()
			max_count = tileset.groups_max()
		elif self.tiletype == TileType.mega:
			count = tileset.vx4.megatile_count()
			max_count = tileset.megatiles_max()
		elif self.tiletype == TileType.mini:
			count = tileset.vr4.image_count()
			max_count = tileset.minitiles_max()
		return '%s Palette [%d/%d]' % (['Group','MegaTile','MiniTile Image'][self.tiletype.value], count, max_count)

	def update_title(self): # type: () -> None
		self.title(self.get_title())

	def update_state(self): # type: () -> None
		tileset = self.get_tileset()
		if not tileset or self.toolbar is None:
			return
		at_max = False
		if self.tiletype == TileType.group:
			at_max = (tileset.groups_remaining() == 0)
		elif self.tiletype == TileType.mega:
			at_max = (tileset.megatiles_remaining() == 0)
		elif self.tiletype == TileType.mini:
			at_max = (tileset.minitiles_remaining() == 0 and tileset.vx4.is_expanded())
		self.toolbar.tag_enabled('can_add', not at_max)

		has_selection = not not self.palette.selected
		self.toolbar.tag_enabled('has_selection', has_selection)

	def update_status(self): # type: () -> None
		status = 'Selected: '
		if len(self.palette.selected):
			for id in self.palette.selected:
				status += '%s ' % id
		else:
			status += 'None'
		self.status.set(status)

	def add(self): # type: () -> None
		tileset = self.get_tileset()
		if not tileset:
			return
		select = 0
		if self.tiletype == TileType.group:
			select = tileset.cv5.group_count()
			tileset.cv5.add_group(CV5Group())
		elif self.tiletype == TileType.mega:
			select = tileset.vx4.megatile_count()
			tileset.vf4.add_megatile(VF4Megatile())
			tileset.vx4.add_megatile(VX4Megatile())
		else:
			if tileset.minitiles_remaining() == 0:
				if not MessageBox.askyesno(parent=self, title='Expand VX4', message="You have run out of minitiles, would you like to expand the VX4 file? If you don't know what this is you should google 'VX4 Expander Plugin' before saying Yes"):
					return
				tileset.vx4.expand()
			select = tileset.vr4.image_count()
			# TODO: Why was there a for loop here?
			# for _ in range(1 if tileset.vx4.is_expanded() else tileset.minitiles_remaining()):
			tileset.vr4.add_image(((0,)*8,)*8)
		self.update_title()
		self.update_state()
		self.palette.update_size()
		self.palette.select(select, scroll_to=True)
		self.delegate.update_ranges()
		self.mark_edited()

	def export_graphics(self): # type: () -> None
		tileset = self.get_tileset()
		if not tileset:
			return
		typename = ''
		if self.tiletype == TileType.group:
			typename = 'MegaTile Group'
		elif self.tiletype == TileType.mega:
			typename = 'MegaTile'
		elif self.tiletype == TileType.mini:
			typename = 'MiniTile'
		path = self.settings.lastpath.graphics.select_save_file(self, key='export', title='Export %s Graphics' % typename, filetypes=[FileType.bmp()])
		if path:
			tileset.export_graphics(self.tiletype, path, self.palette.selected)

	def import_graphics(self): # type: () -> None
		from .GraphicsImporter import GraphicsImporter
		GraphicsImporter(self, self.settings, self, self.tiletype, self.palette.selected)

	def imported_graphics(self, new_ids): # type: (list[int]) -> None
		TilePalette.TILE_CACHE.clear()
		self.update_title()
		self.update_state()
		self.palette.update_size()
		if len(new_ids):
			self.palette.set_selection(new_ids)
			self.palette.scroll_to_selection()
		self.palette.draw_tiles(force=True)
		self.delegate.update_ranges()
		self.mark_edited()

	def export_settings(self): # type: () -> None
		tileset = self.get_tileset()
		if not tileset or not len(self.palette.selected):
			return
		if self.tiletype == TileType.group:
			path = self.settings.lastpath.graphics.select_save_file(self, key='export', title='Export MegaTile Group Settings', filetypes=[FileType.txt()])
			if path:
				tileset.export_group_settings(path, self.palette.selected)
		elif self.tiletype == TileType.mega:
			from .MegaTileSettingsExporter import MegaTileSettingsExporter
			MegaTileSettingsExporter(self, self.settings, self.palette.selected, self)

	def import_settings(self): # type: () -> None
		if not len(self.palette.selected):
			return
		from .SettingsImporter import SettingsImporter
		SettingsImporter(self, self.settings, self.tiletype, self.palette.selected, self)

	def edit(self, e=None): # type: (Any) -> None
		if not len(self.palette.selected):
			return
		if self.tiletype == TileType.mega:
			from .MegaEditor import MegaEditor
			MegaEditor(self, self.settings, self, self.palette.selected[0])
		elif self.tiletype == TileType.mini:
			from .MiniEditor import MiniEditor
			MiniEditor(self, self.palette.selected[0], self)

	def dismiss(self): # type: () -> None
		self.settings.windows.palette.save_window_size(('group','mega','mini')[self.tiletype.value], self)
		if self.edited:
			self.delegate.megaload()
			self.delegate.mark_edited()
		TilePalette.OPEN_PALETTE_COUNT -= 1
		if not TilePalette.OPEN_PALETTE_COUNT:
			TilePalette.TILE_CACHE.clear()
		PyMSDialog.dismiss(self)

	def draw_tiles(self, force: bool) -> None:
		self.palette.draw_tiles(force)
