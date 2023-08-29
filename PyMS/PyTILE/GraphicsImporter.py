
from __future__ import annotations

from PyMS.FileFormats.Tileset.Tileset import Tileset
from PyMS.FileFormats.Tileset.VX4 import VX4Minitile
from PyMS.Utilities.UIKit import Image
from .Delegates import GraphicsImporterDelegate, TilePaletteDelegate

from ..FileFormats.Tileset.Tileset import TileType, ImportGraphicsOptions

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities import Assets

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Utilities import Config

class GraphicsImporter(PyMSDialog, TilePaletteDelegate):
	def __init__(self, parent, settings, delegate, tiletype=TileType.group, ids=None): # type: (Misc, Settings, GraphicsImporterDelegate, TileType, list[int] | None) -> None
		self.settings = settings
		self.tiletype = tiletype
		self.ids = ids
		self.delegate = delegate
		title = 'Import '
		if tiletype == TileType.group:
			title += 'MegaTile Group'
		elif tiletype == TileType.mega:
			title += 'MegaTile'
		elif tiletype == TileType.mini:
			title += 'MiniTile'
		title += ' Graphics'
		PyMSDialog.__init__(self, parent, title, resizable=(True,True), set_min_size=(True,True))

	def widgetize(self): # type: () -> (Misc | None)
		tileset = self.delegate.get_tileset()
		assert tileset is not None
	
		self.replace_selections = BooleanVar()
		self.auto_close = BooleanVar()
		self.megatiles_reuse_duplicates_old = BooleanVar()
		self.megatiles_reuse_duplicates_new = BooleanVar()
		self.megatiles_reuse_null = BooleanVar()
		self.megatiles_null_id = IntegerVar(0,[0,tileset.vf4.megatile_count()-1])
		self.minitiles_reuse_duplicates_old = BooleanVar()
		self.minitiles_reuse_duplicates_new = BooleanVar()
		self.minitiles_reuse_null = BooleanVar()
		self.minitiles_null_id = IntegerVar(0,[0,tileset.vr4.image_count()-1])
		self.load_settings()

		frame = LabelFrame(self, text="BMP's:")
		self.graphics_list = ScrolledListbox(frame, auto_bind=self, selectmode=EXTENDED, height=3)
		self.graphics_list.pack(side=TOP, fill=BOTH, expand=1, padx=2,pady=2)
		self.graphics_list.bind(WidgetEvent.Listbox.Select(), self.update_states)
		buts = Frame(frame)
		button = Button(buts, image=Assets.get_image('find'), width=20, height=20, command=lambda *_: self.select_paths(replace=True))
		button.pack(side=LEFT, padx=(1,0))
		Tooltip(button, "Set BMP's")
		button = Button(buts, image=Assets.get_image('add'), width=20, height=20, command=lambda *_: self.select_paths(replace=False))
		button.pack(side=LEFT)
		Tooltip(button, "Add BMP's")
		button = Button(buts, image=Assets.get_image('remove'), width=20, height=20, command=self.remove_paths)
		button.pack(side=LEFT)
		Tooltip(button, "Remove BMP's")
		self.sel_buttons = [button]
		button = Button(buts, image=Assets.get_image('down'), width=20, height=20, command=self.shift_down)
		button.pack(side=RIGHT, padx=(0,1))
		Tooltip(button, "Move Selections Down")
		self.sel_buttons.append(button)
		button = Button(buts, image=Assets.get_image('up'), width=20, height=20, command=self.shift_up)
		button.pack(side=RIGHT)
		Tooltip(button, "Move Selections Up")
		self.sel_buttons.append(button)
		buts.pack(fill=X)
		frame.pack(side=TOP, fill=BOTH, expand=1, padx=3, pady=2)
		self.settings_frame = LabelFrame(self, text='Settings')
		sets = Frame(self.settings_frame)
		if self.tiletype == TileType.group:
			g = LabelFrame(sets, text='Reuse MegaTiles')
			f = Frame(g)
			Checkbutton(f, text='Duplicates (Old)', variable=self.megatiles_reuse_duplicates_old, anchor=W).pack(side=LEFT)
			f.pack(side=TOP, fill=X)
			f = Frame(g)
			Checkbutton(f, text='Duplicates (New)', variable=self.megatiles_reuse_duplicates_new, anchor=W).pack(side=LEFT)
			f.pack(side=TOP, fill=X)
			f = Frame(g)
			Checkbutton(f, text='Null:', variable=self.megatiles_reuse_null, anchor=W).pack(side=LEFT)
			Entry(f, textvariable=self.megatiles_null_id, font=Font.fixed(), width=5).pack(side=LEFT)
			Button(f, image=Assets.get_image('find'), width=20, height=20, command=lambda *_: self.select_null(TileType.mega)).pack(side=LEFT, padx=1)
			f.pack(side=TOP, fill=X)
			g.grid(column=0,row=0, padx=(0,3), sticky=W+E)
			sets.grid_columnconfigure(0, weight=1)
		g = LabelFrame(sets, text='Reuse MiniTiles')
		f = Frame(g)
		Checkbutton(f, text='Duplicates (Old)', variable=self.minitiles_reuse_duplicates_old, anchor=W).pack(side=LEFT)
		f.pack(side=TOP, fill=X)
		f = Frame(g)
		Checkbutton(f, text='Duplicates (New)', variable=self.minitiles_reuse_duplicates_new, anchor=W).pack(side=LEFT)
		f.pack(side=TOP, fill=X)
		f = Frame(g)
		Checkbutton(f, text='Null:', variable=self.minitiles_reuse_null, anchor=W).pack(side=LEFT)
		Entry(f, textvariable=self.minitiles_null_id, font=Font.fixed(), width=5).pack(side=LEFT)
		Button(f, image=Assets.get_image('find'), width=20, height=20, command=lambda *_: self.select_null(TileType.mini)).pack(side=LEFT, padx=1)
		f.pack(side=TOP, fill=X)
		g.grid(column=1,row=0, sticky=W+E)
		sets.grid_columnconfigure(1, weight=1)
		f = Frame(sets)
		Button(f, text='Reset to recommended settings', command=self.reset_options).pack(side=BOTTOM)
		s = Frame(f)
		Checkbutton(s, text='Replace palette selection', variable=self.replace_selections).pack(side=LEFT)
		Checkbutton(s, text='Auto-close', variable=self.auto_close).pack(side=LEFT, padx=(10,0))
		s.pack(side=BOTTOM)
		f.grid(column=0,row=1, columnspan=2, sticky=W+E)
		sets.pack(fill=X, expand=1, padx=3)
		self.settings_frame.pack(side=TOP, fill=X, padx=3, pady=(3,0))

		buts = Frame(self)
		self.import_button = Button(buts, text='Import', state=DISABLED, command=self.iimport)
		self.import_button.grid(column=0,row=0)
		Button(buts, text='Cancel', command=self.cancel).grid(column=2,row=0)
		buts.grid_columnconfigure(1, weight=1)
		buts.pack(side=BOTTOM, padx=3, pady=3, fill=X)

		self.update_states()

		return self.import_button

	def setup_complete(self): # type: () -> None
		self.settings.windows['import'].graphics.load_window_size(('group','mega','mini')[self.tiletype.value], self)

	def load_settings(self): # type: () -> None
		match self.tiletype:
			case TileType.group:
				type_key = 'groups'
			case TileType.mega:
				type_key = 'megatiles' 
			case TileType.mini:
				type_key = 'minitiles'
		type_settings = self.settings['import'].graphics[type_key]
		self.megatiles_reuse_duplicates_old.set(type_settings.get('megatiles_reuse_duplicates_old',False))
		self.megatiles_reuse_duplicates_new.set(type_settings.get('megatiles_reuse_duplicates_new',False))
		self.megatiles_reuse_null.set(type_settings.get('megatiles_reuse_null',True))
		self.megatiles_null_id.set(type_settings.get('megatiles_null_id',0))
		self.minitiles_reuse_duplicates_old.set(type_settings.get('minitiles_reuse_duplicates_old',True))
		self.minitiles_reuse_duplicates_new.set(type_settings.get('minitiles_reuse_duplicates_new',True))
		self.minitiles_reuse_null.set(type_settings.get('minitiles_reuse_null',True))
		self.minitiles_null_id.set(type_settings.get('minitiles_null_id',0))
		self.replace_selections.set(type_settings.get('replace_selections',True))
		self.auto_close.set(type_settings.get('auto_close',True))

	def update_states(self, *_): # type: (Any) -> None
		self.import_button['state'] = NORMAL if self.graphics_list.size() else DISABLED
		sel = NORMAL if self.graphics_list.curselection() else DISABLED
		for b in self.sel_buttons:
			b['state'] = sel

	def iimport(self, *_): # type: (Any) -> None
		tileset = self.delegate.get_tileset()
		if not tileset:
			return
		def can_expand():
			return MessageBox.askyesno(parent=self, title='Expand VX4', message="You have run out of minitiles, would you like to expand the VX4 file? If you don't know what this is you should google 'VX4 Expander Plugin' before saying Yes")
		options = ImportGraphicsOptions()
		options.minitiles_reuse_duplicates_old = self.minitiles_reuse_duplicates_old.get()
		options.minitiles_reuse_duplicates_new = self.minitiles_reuse_duplicates_new.get()
		options.minitiles_reuse_null_with_id = self.minitiles_null_id.get() if self.minitiles_reuse_null.get() else None
		options.minitiles_expand_allowed = can_expand
		options.megatiles_reuse_duplicates_old = self.megatiles_reuse_duplicates_old.get()
		options.megatiles_reuse_duplicates_new = self.megatiles_reuse_duplicates_new.get()
		options.megatiles_reuse_null_with_id = self.megatiles_null_id.get() if self.megatiles_reuse_null.get() else None
		ids = None
		if self.replace_selections.get():
			ids = self.ids
		try:
			new_ids = tileset.import_graphics(self.tiletype, self.graphics_list.get(0,END), ids, options)
		except PyMSError as e:
			ErrorDialog(self, e)
		else:
			self.delegate.imported_graphics(new_ids)
			if self.auto_close.get():
				self.ok()

	def select_paths(self, replace=False): # type: (bool) -> None
		paths = self.settings.lastpath.graphics.select_open_files(self, key='import', title='Choose Graphics', filetypes=[FileType.bmp()])
		if paths:
			if replace:
				self.graphics_list.delete(0, END)
			self.graphics_list.insert(END, *paths)
			self.graphics_list.xview_moveto(1.0)
			self.graphics_list.yview_moveto(1.0)
		self.update_states()

	def remove_paths(self, *_): # type: (Any) -> None
		for index in sorted(self.graphics_list.curselection(), reverse=True):
			self.graphics_list.delete(index)
		self.update_states()

	def shift_up(self): # type: () -> None
		min_index = -1
		select = []
		for index in sorted(self.graphics_list.curselection()):
			move_to = index-1
			if move_to > min_index:
				select.append(move_to)
				item = self.graphics_list.get(index)
				self.graphics_list.delete(index)
				self.graphics_list.insert(move_to, item)
			else:
				min_index = index
				select.append(index)
		self.graphics_list.select_clear(0,END)
		for index in select:
			self.graphics_list.select_set(index)

	def shift_down(self): # type: () -> None
		max_index = self.graphics_list.size()
		select = []
		for index in sorted(self.graphics_list.curselection(), reverse=True):
			move_to = index+1
			if move_to < max_index:
				select.append(move_to)
				item = self.graphics_list.get(index)
				self.graphics_list.delete(index)
				self.graphics_list.insert(move_to, item)
			else:
				max_index = index
				select.append(index)
		self.graphics_list.select_clear(0,END)
		for index in select:
			self.graphics_list.select_set(index)

	def select_null(self, tiletype): # type: (TileType) -> None
		id = 0
		if tiletype == TileType.mega:
			id = self.megatiles_null_id.get()
		elif tiletype == TileType.mini:
			id = self.minitiles_null_id.get()
		from .TilePalette import TilePalette
		TilePalette(self, self.settings, self, tiletype, id)

	def get_tileset(self) -> Tileset | None:
		return self.delegate.get_tileset()

	def get_tile(self, id: int | VX4Minitile) -> Image:
		return self.delegate.get_tile(id)

	def mark_edited(self) -> None:
		return self.delegate.mark_edited()

	def change(self, tiletype, id):
		if tiletype == TileType.mega:
			self.megatiles_null_id.set(id)
		elif tiletype == TileType.mini:
			self.minitiles_null_id.set(id)

	def megaload(self): # type: () -> None
		pass

	def update_ranges(self): # type: () -> None
		pass

	def reset_options(self): # type: () -> None
		if 'import' in self.settings:
			match self.tiletype:
				case TileType.group:
					type_key = 'groups'
				case TileType.mega:
					type_key = 'megatiles'
				case TileType.mini:
					type_key = 'minitiles'
			del self.settings['import'].graphics[type_key]
		self.load_settings()

	def dismiss(self): # type: () -> None
		type_settings = {
			'minitiles_reuse_duplicates_old': not not self.minitiles_reuse_duplicates_old.get(),
			'minitiles_reuse_duplicates_new': not not self.minitiles_reuse_duplicates_new.get(),
			'minitiles_reuse_null': not not self.minitiles_reuse_null.get(),
			'minitiles_null_id': self.minitiles_null_id.get(),
			'replace_selections': not not self.replace_selections.get(),
			'auto_close': not not self.auto_close.get()
		}
		if self.tiletype != TileType.mini:
			type_settings['megatiles_reuse_duplicates_old'] = not not self.megatiles_reuse_duplicates_old.get()
			type_settings['megatiles_reuse_duplicates_new'] = not not self.megatiles_reuse_duplicates_new.get()
			type_settings['megatiles_reuse_null'] = not not self.megatiles_reuse_null.get()
			type_settings['megatiles_null_id'] = self.megatiles_null_id.get()
		match self.tiletype:
			case TileType.group:
				type_key = 'groups'
			case TileType.mega:
				type_key = 'megatiles'
			case TileType.mini:
				type_key = 'minitiles'
		self.settings['import'].graphics[type_key] = type_settings
		self.settings.windows['import'].graphics.save_window_size(('group','mega','mini')[self.tiletype.value], self)
		PyMSDialog.dismiss(self)
