
from __future__ import annotations

from .Delegates import MainDelegate

from ..FileFormats.Tileset.Tileset import TileType, ImportSettingsOptions

from ..Utilities import Assets
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities import Serialize

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Utilities import Config

class SettingsImporter(PyMSDialog):
	REPEATERS = (
		('Ignore',				'ignore',		Serialize.repeater_ignore),
		('Repeat All Settings',	'repeat_all',	Serialize.repeater_loop),
		('Repeat Last Setting',	'repeat_last',	Serialize.repeater_repeat_last)
	)
	def __init__(self, parent, settings, tiletype, ids, delegate): # type: (Misc, Settings, TileType, list[int], MainDelegate) -> None
		self.settings = settings
		self.tiletype = tiletype
		self.ids = ids
		self.delegate = delegate
		typename = ''
		if self.tiletype == TileType.group:
			typename = 'MegaTile Group'
		elif self.tiletype == TileType.mega:
			typename = 'MegaTile'
		PyMSDialog.__init__(self, parent, 'Import %s Settings' % typename, resizable=(True,False), set_min_size=(True,True))

	def widgetize(self): # type: () -> (Misc | None)
		self.settings_path = StringVar()
		self.repeater = IntVar()
		repeater_n = 0
		repeater_setting = self.settings['import'].settings.get('repeater',SettingsImporter.REPEATERS[0][1])
		for n,(_,setting,_) in enumerate(SettingsImporter.REPEATERS):
			if setting == repeater_setting:
				repeater_n = n
				break
		self.repeater.set(repeater_n)
		self.auto_close = IntVar()
		self.auto_close.set(self.settings['import'].settings.get('auto_close', True))

		f = Frame(self)
		Label(f, text='TXT:', anchor=W).pack(side=TOP, fill=X, expand=1)
		entryframe = Frame(f)
		self.settings_entry = Entry(entryframe, textvariable=self.settings_path, state=DISABLED)
		self.settings_entry.pack(side=LEFT, fill=X, expand=1)
		Button(entryframe, image=Assets.get_image('find'), width=20, height=20, command=self.select_path).pack(side=LEFT, padx=(1,0))
		entryframe.pack(side=TOP, fill=X, expand=1)
		f.pack(side=TOP, fill=X, padx=3)

		sets = LabelFrame(self, text='Settings')
		f = Frame(sets)
		Label(f, text='Extra Tiles:', anchor=W).pack(side=TOP, fill=X)
		DropDown(f, self.repeater, [r[0] for r in SettingsImporter.REPEATERS], width=20).pack(side=TOP, fill=X)
		Checkbutton(f, text='Auto-close', variable=self.auto_close).pack(side=BOTTOM, padx=3, pady=(3,0))
		f.pack(side=TOP, fill=X, padx=3, pady=(0,3))
		sets.pack(side=TOP, fill=X, padx=3)

		buts = Frame(self)
		self.import_button = Button(buts, text='Import', state=DISABLED, command=self.iimport)
		self.import_button.pack(side=LEFT)
		Button(buts, text='Cancel', command=self.cancel).pack(side=RIGHT, padx=(10,0))
		buts.pack(side=BOTTOM, fill=X, padx=3, pady=3)

		self.settings_path.trace('w', self.update_states)

		return self.import_button

	def select_path(self): # type: () -> None
		typename = ''
		if self.tiletype == TileType.group:
			typename = 'MegaTile Group'
		elif self.tiletype == TileType.mega:
			typename = 'MegaTile'
		path = self.settings.lastpath.settings.select_open_file(self, key='import', title='Import %s Settings' % typename, filetypes=[FileType.txt()])
		if not path:
			return
		self.settings_path.set(path)
		self.settings_entry.xview(END)
		self.update_states()

	def update_states(self, *_): # type: (Any) -> None
		self.import_button['state'] = NORMAL if self.settings_path.get() else DISABLED

	def iimport(self): # type: () -> None
		tileset = self.delegate.get_tileset()
		if not tileset:
			return
		options = ImportSettingsOptions()
		options.repeater = SettingsImporter.REPEATERS[self.repeater.get()][2]
		try:
			if self.tiletype == TileType.group:
				tileset.import_group_settings(self.settings_path.get(), self.ids, options)
			elif self.tiletype == TileType.mega:
				tileset.import_megatile_settings(self.settings_path.get(), self.ids, options)
		except PyMSError as e:
			ErrorDialog(self, e)
		else:
			self.delegate.mark_edited()
			if self.auto_close.get():
				self.ok()

	def dismiss(self):
		self.settings['import'].settings.repeater = SettingsImporter.REPEATERS[self.repeater.get()][1]
		self.settings['import'].settings.auto_close = not not self.auto_close.get()
		PyMSDialog.dismiss(self)
