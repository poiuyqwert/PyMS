
from .TilePaletteView import TilePaletteView

from ..FileFormats.Tileset.Tileset import TILETYPE_GROUP, TILETYPE_MEGA, TILETYPE_MINI

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Assets
from ..Utilities.Toolbar import Toolbar
from ..Utilities.FileType import FileType

class TilePalette(PyMSDialog):
	OPEN_PALETTE_COUNT = 0
	TILE_CACHE = {}

	def __init__(self, parent, settings, tiletype=TILETYPE_GROUP, select=None, delegate=None, editing=False):
		TilePalette.OPEN_PALETTE_COUNT += 1
		self.settings = settings
		self.tiletype = tiletype
		self.start_selected = []
		if select != None:
			if isinstance(select, list):
				self.start_selected.extend(sorted(select))
			else:
				self.start_selected.append(select)
		self.delegate = delegate or parent
		self.tileset = parent.tileset
		self.gettile = parent.gettile
		self.editing = editing
		self.edited = False
		PyMSDialog.__init__(self, parent, self.get_title(), resizable=(tiletype != TILETYPE_GROUP,True), set_min_size=(True,True))

	def widgetize(self):
		typename = ''
		smallertype = ''
		if self.tiletype == TILETYPE_GROUP:
			typename = 'MegaTile Groups'
			smallertype = 'MegaTiles'
		elif self.tiletype == TILETYPE_MEGA:
			typename = 'MegaTiles'
			smallertype = 'MiniTiles'
		elif self.tiletype == TILETYPE_MINI:
			typename = 'MiniTiles'
		self.toolbar = None
		if self.editing:
			self.toolbar = Toolbar(self)
			self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add', Key.Insert, enabled=False, tags='can_add')
			if self.tiletype != TILETYPE_MINI:
				self.toolbar.add_section()
				self.toolbar.add_button(Assets.get_image('colors'), self.select_smaller, 'Select %s' % smallertype, Ctrl.m)
			if self.tiletype != TILETYPE_GROUP:
				self.toolbar.add_section()
				self.toolbar.add_button(Assets.get_image('edit'), self.edit, 'Edit %s' % typename, Key.Return)
			self.toolbar.add_spacer(20)
			self.toolbar.add_button(Assets.get_image('exportc'), self.export_graphics, 'Export %s Graphics' % typename, Ctrl.e, enabled=False, tags='has_selection')
			self.toolbar.add_button(Assets.get_image('importc'), self.import_graphics, 'Import %s Graphics' % typename, Ctrl.i)
			if self.tiletype != TILETYPE_MINI:
				self.toolbar.add_section()
				self.toolbar.add_button(Assets.get_image('export'), self.export_settings, 'Export %s Settings' % typename, Shift.Ctrl.e, enabled=False, tags='has_selection')
				self.toolbar.add_button(Assets.get_image('import'), self.import_settings, 'Import %s Settings' % typename, Shift.Ctrl.i)
			self.toolbar.pack(fill=X)

		self.palette = TilePaletteView(self, self.tiletype, self.start_selected)
		self.palette.pack(side=TOP, fill=BOTH, expand=1)

		self.status = StringVar()
		self.update_status()
		self.update_state()

		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, fill=X, expand=1, padx=1)
		statusbar.pack(side=BOTTOM, fill=X)

	def tile_palette_get_tileset(self):
		return self.tileset

	def tile_palette_get_tile(self):
		return self.gettile

	def tile_palette_binding_widget(self):
		return self

	def tile_palette_double_clicked(self, id):
		if not hasattr(self.delegate, 'change'):
			return
		self.delegate.change(self.tiletype, id)
		self.ok()

	def tile_palette_selection_changed(self):
		self.update_status()
		self.update_state()
		self.palette.draw_selections()

	def setup_complete(self):
		self.settings.windows.palette.load_window_size(('group','mega','mini')[self.tiletype], self)

	def select_smaller(self):
		ids = []
		for id in self.palette.selected:
			if self.tiletype == TILETYPE_GROUP:
				for sid in self.tileset.cv5.groups[id][13]:
					if sid and not sid in ids:
						ids.append(sid)
			elif self.tiletype == TILETYPE_MEGA:
				for sid,_ in self.tileset.vx4.graphics[id]:
					if not sid in ids:
						ids.append(sid)
		TilePalette(self, self.settings, TILETYPE_MEGA if self.tiletype == TILETYPE_GROUP else TILETYPE_MINI, ids, editing=True)

	def mark_edited(self):
		self.edited = True

	def get_title(self):
		count = 0
		max_count = 0
		if self.tiletype == TILETYPE_GROUP:
			count = len(self.tileset.cv5.groups)
			max_count = self.tileset.groups_max()
		elif self.tiletype == TILETYPE_MEGA:
			count = len(self.tileset.vx4.graphics)
			max_count = self.tileset.megatiles_max()
		elif self.tiletype == TILETYPE_MINI:
			count = len(self.tileset.vr4.images)
			max_count = self.tileset.minitiles_max()
		return '%s Palette [%d/%d]' % (['Group','MegaTile','MiniTile Image'][self.tiletype], count,max_count)
	def update_title(self):
		self.title(self.get_title())

	def update_state(self):
		if self.toolbar == None:
			return
		at_max = False
		if self.tiletype == TILETYPE_GROUP:
			at_max = (self.tileset.groups_remaining() == 0)
		elif self.tiletype == TILETYPE_MEGA:
			at_max = (self.tileset.megatiles_remaining() == 0)
		elif self.tiletype == TILETYPE_MINI:
			at_max = (self.tileset.minitiles_remaining() == 0 and self.tileset.vx4.expanded)
		self.toolbar.tag_enabled('can_add', not at_max)

		has_selection = not not self.palette.selected
		self.toolbar.tag_enabled('has_selection', has_selection)

	def update_status(self):
		status = 'Selected: '
		if len(self.palette.selected):
			for id in self.palette.selected:
				status += '%s ' % id
		else:
			status += 'None'
		self.status.set(status)

	def add(self):
		select = 0
		if self.tiletype == TILETYPE_GROUP:
			self.tileset.cv5.groups.append([0] * 13 + [[0] * 16])
			select = len(self.tileset.cv5.groups)-1
		elif self.tiletype == TILETYPE_MEGA:
			self.tileset.vf4.flags.append([0]*16)
			self.tileset.vx4.add_tile(((0,0),)*16)
			select = len(self.tileset.vx4.graphics)-1
		else:
			if self.tileset.minitiles_remaining() == 0:
				if not MessageBox.askyesno(parent=self, title='Expand VX4', message="You have run out of minitiles, would you like to expand the VX4 file? If you don't know what this is you should google 'VX4 Expander Plugin' before saying Yes"):
					return
				self.tileset.vx4.expanded = True
			for _ in range(1 if self.tileset.vx4.expanded else self.tileset.minitiles_remaining()):
				self.tileset.vr4.add_image(((0,)*8,)*8)
			select = len(self.tileset.vr4.images)-1
		self.update_title()
		self.update_state()
		self.palette.update_size()
		self.palette.select(select, scroll_to=True)
		self.parent.update_ranges()
		self.mark_edited()

	def export_graphics(self):
		typename = ''
		if self.tiletype == TILETYPE_GROUP:
			typename = 'MegaTile Group'
		elif self.tiletype == TILETYPE_MEGA:
			typename = 'MegaTile'
		elif self.tiletype == TILETYPE_MINI:
			typename = 'MiniTile'
		path = self.settings.lastpath.graphics.select_save_file(self, key='export', title='Export %s Graphics' % typename, filetypes=[FileType.bmp()])
		if path:
			self.tileset.export_graphics(self.tiletype, path, self.palette.selected)

	def import_graphics(self):
		from .GraphicsImporter import GraphicsImporter
		GraphicsImporter(self, self.settings, self.tiletype, self.palette.selected)

	def imported_graphics(self, new_ids):
		TilePalette.TILE_CACHE.clear()
		self.update_title()
		self.update_state()
		self.palette.update_size()
		if len(new_ids):
			self.palette.select(new_ids)
			self.palette.scroll_to_selection()
		self.palette.draw_tiles(force=True)
		self.parent.update_ranges()
		self.mark_edited()

	def export_settings(self):
		if not len(self.palette.selected):
			return
		if self.tiletype == TILETYPE_GROUP:
			path = self.settings.lastpath.graphics.select_save_file(self, key='export', title='Export MegaTile Group Settings', filetypes=[FileType.txt()])
			if path:
				self.tileset.export_settings(TILETYPE_GROUP, path, self.palette.selected)
		elif self.tiletype == TILETYPE_MEGA:
			from .MegaTileSettingsExporter import MegaTileSettingsExporter
			MegaTileSettingsExporter(self, self.settings, self.palette.selected)

	def import_settings(self):
		if not len(self.palette.selected):
			return
		from .SettingsImporter import SettingsImporter
		SettingsImporter(self, self.settings, self.tiletype, self.palette.selected)

	def edit(self, e=None):
		if not len(self.palette.selected):
			return
		if self.tiletype == TILETYPE_MEGA:
			from .MegaEditor import MegaEditor
			MegaEditor(self, self.settings, self.palette.selected[0])
		elif self.tiletype == TILETYPE_MINI:
			from .MiniEditor import MiniEditor
			MiniEditor(self, self.palette.selected[0])

	def dismiss(self):
		self.settings.windows.palette.save_window_size(('group','mega','mini')[self.tiletype], self)
		if hasattr(self.delegate,'selecting'):
			self.delegate.selecting = None
		elif hasattr(self.delegate, 'megaload'):
			self.delegate.megaload()
		if self.edited and hasattr(self.delegate, 'mark_edited'):
			self.delegate.mark_edited()
		TilePalette.OPEN_PALETTE_COUNT -= 1
		if not TilePalette.OPEN_PALETTE_COUNT:
			TilePalette.TILE_CACHE.clear()
		PyMSDialog.dismiss(self)
