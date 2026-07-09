
from __future__ import annotations

from .Config import PyTILEConfig
from .Delegates import MainDelegate
from .RepeaterID import RepeaterID

from ..FileFormats.Tileset.Tileset import TileType, ImportSettingsOptions

from ..Utilities import Assets
from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities import Serialize

from typing import Any

class SettingsImporter(PyMSDialog):
	REPEATERS = (
		('Ignore',				RepeaterID.ignore,		Serialize.repeater_ignore),
		('Repeat All Settings',	RepeaterID.repeat_all,	Serialize.repeater_loop),
		('Repeat Last Setting',	RepeaterID.repeat_last,	Serialize.repeater_repeat_last)
	)
	def __init__(self, *, parent: UI.Misc, config: PyTILEConfig, tiletype: TileType, ids: list[int], delegate: MainDelegate) -> None:
		self.config_ = config
		self.tiletype = tiletype
		self.ids = ids
		self.delegate = delegate
		PyMSDialog.__init__(self, parent, f'Import {TileType.display_name(self.tiletype)} Settings', resizable=(True,False), set_min_size=(True,True))

	def widgetize(self) -> UI.Misc | None:
		self.settings_path = UI.StringVar()
		self.repeater = UI.IntVar()
		repeater_n = 0
		repeater_setting = self.config_.import_.settings.repeater.value
		for n,(_,setting,_) in enumerate(SettingsImporter.REPEATERS):
			if setting == repeater_setting:
				repeater_n = n
				break
		self.repeater.set(repeater_n)
		self.auto_close = UI.IntVar()
		self.auto_close.set(self.config_.import_.settings.auto_close.value)

		f = UI.Frame(self)
		UI.Label(f, text='TXT:', anchor=UI.W).pack(side=UI.TOP, fill=UI.X, expand=1)
		entryframe = UI.Frame(f)
		self.settings_entry = UI.Entry(entryframe, textvariable=self.settings_path, state=UI.DISABLED)
		self.settings_entry.pack(side=UI.LEFT, fill=UI.X, expand=1)
		UI.Button(entryframe, image=Assets.get_image('find'), width=20, height=20, command=self.select_path).pack(side=UI.LEFT, padx=(1,0))
		entryframe.pack(side=UI.TOP, fill=UI.X, expand=1)
		f.pack(side=UI.TOP, fill=UI.X, padx=3)

		sets = UI.LabelFrame(self, text='Settings')
		f = UI.Frame(sets)
		UI.Label(f, text='Extra Tiles:', anchor=UI.W).pack(side=UI.TOP, fill=UI.X)
		UI.DropDown(f, self.repeater, [r[0] for r in SettingsImporter.REPEATERS], width=20).pack(side=UI.TOP, fill=UI.X)
		UI.Checkbutton(f, text='Auto-close', variable=self.auto_close).pack(side=UI.BOTTOM, padx=3, pady=(3,0))
		f.pack(side=UI.TOP, fill=UI.X, padx=3, pady=(0,3))
		sets.pack(side=UI.TOP, fill=UI.X, padx=3)

		buts = UI.Frame(self)
		self.import_button = UI.Button(buts, text='Import', state=UI.DISABLED, command=self.iimport)
		self.import_button.pack(side=UI.LEFT)
		UI.Button(buts, text='Cancel', command=self.cancel).pack(side=UI.RIGHT, padx=(10,0))
		buts.pack(side=UI.BOTTOM, fill=UI.X, padx=3, pady=3)

		self.settings_path.trace_add('write', self.update_states)

		return self.import_button

	def select_path(self) -> None:
		path = self.config_.last_path.settings.select_open(self, title=f'Import {TileType.display_name(self.tiletype)} Settings')
		if not path:
			return
		self.settings_path.set(path)
		self.settings_entry.xview(UI.END)
		self.update_states()

	def update_states(self, *_: Any) -> None:
		self.import_button['state'] = UI.NORMAL if self.settings_path.get() else UI.DISABLED

	def iimport(self) -> None:
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

	def dismiss(self) -> None:
		self.config_.import_.settings.repeater.value = SettingsImporter.REPEATERS[self.repeater.get()][1]
		self.config_.import_.settings.auto_close.value = not not self.auto_close.get()
		PyMSDialog.dismiss(self)
