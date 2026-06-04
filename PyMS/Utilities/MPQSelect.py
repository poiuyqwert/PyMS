
from __future__ import annotations

from .PyMSDialog import PyMSDialog
from . import UIKit as UI
from . import Assets
from . import Config

import os, re
from enum import Enum

from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
	from .MPQHandler import MPQHandler

class MPQSelect(PyMSDialog):
	class Action(Enum):
		open = 0
		save = 1
		select = 2

		@property
		def cta(self) -> str:
			match self:
				case MPQSelect.Action.open:
					return 'Open'
				case MPQSelect.Action.save:
					return 'Save'
				case MPQSelect.Action.select:
					return 'Select'

		def title(self, name: str) -> str:
			return f'{self.cta} {name}'

	def __init__(self, *, parent: UI.Misc, mpqhandler: MPQHandler, name: str, filetype: UI.FileType, history_config: Config.List, window_geometry_config: Config.WindowGeometry, default_search: str | None = None, action: MPQSelect.Action = Action.select) -> None:
		self.mpqhandler = mpqhandler
		self.search = UI.StringVar()
		search = default_search or filetype.extensions_tuple[0]
		self.search.set(search)
		self.search.trace_add('write', self.updatesearch)
		self.history_config = history_config
		self.window_geometry_config = window_geometry_config
		self.regex = UI.IntVar()
		self.regex.set(0)
		self.files: list[str] = []
		self.file: str | None = None
		self.resettimer: str | None = None
		self.searchtimer: str | None = None
		self.action = action
		PyMSDialog.__init__(self, parent, self.action.title(name))

	def widgetize(self) -> UI.Misc | None:
		self.listbox = UI.ScrolledListbox(self, width=35, height=10)
		self.listbox.pack(fill=UI.BOTH, padx=1, pady=1, expand=1)
		self.listbox.focus_set()

		s = UI.Frame(self)
		history = self.history_config.data[::-1]
		self.textdrop = UI.TextDropDown(s, self.search, history)
		self.textdrop_entry_c = self.textdrop.entry['bg']
		self.textdrop.pack(side=UI.LEFT, fill=UI.X, padx=1, pady=2)
		self.open = UI.Button(s, text=self.action.cta, width=10, command=self.ok)
		self.open.pack(side=UI.RIGHT, padx=1, pady=3)
		s.pack(fill=UI.X)
		s = UI.Frame(self)
		UI.Radiobutton(s, text='Wildcard', variable=self.regex, value=0, command=self.updatelist).pack(side=UI.LEFT, padx=1, pady=2)
		UI.Radiobutton(s, text='Regex', variable=self.regex, value=1, command=self.updatelist).pack(side=UI.LEFT, padx=1, pady=2)
		UI.Button(s, text='Cancel', width=10, command=self.cancel).pack(side=UI.RIGHT, padx=1, pady=3)
		s.pack(fill=UI.X)

		self.listfiles()
		self.updatelist()

		return self.open

	def setup_complete(self) -> None:
		self.window_geometry_config.load_size(self)

	def listfiles(self) -> None:
		self.files = []
		for file_entry in self.mpqhandler.list_files():
			if not file_entry.file_name in self.files:
				self.files.append(file_entry.file_name.decode('utf-8'))
		for path,_,filenames in os.walk(Assets.mpq_dir):
			for filename in filenames:
				mpq_filename = Assets.mpq_file_path_to_file_name(os.path.join(path, filename))
				if not mpq_filename in self.files:
					self.files.append(mpq_filename)
		self.files.sort()

	def updatelist(self) -> None:
		if self.searchtimer:
			self.after_managed_cancel(self.searchtimer)
			self.searchtimer = None
		self.listbox.delete(0,UI.END)
		s = self.search.get()
		if not self.regex.get():
			s = '^' + re.escape(s).replace('\\?','.').replace('\\*','.+?') + '$'
		try:
			r = re.compile(s)
		except Exception:
			self.resettimer = self.after_managed(1000, self.updatecolor)
			self.textdrop.entry['bg'] = '#FFB4B4'
		else:
			for f in [p for p in self.files if r.match(p)]:
				self.listbox.insert(UI.END,f)
		if self.listbox.size():
			self.listbox.select_set(0)
			self.open['state'] = UI.NORMAL
		else:
			self.open['state'] = UI.DISABLED

	def updatecolor(self) -> None:
		if self.resettimer:
			self.after_managed_cancel(self.resettimer)
			self.resettimer = None
		self.textdrop.entry['bg'] = self.textdrop_entry_c

	def updatesearch(self, *_: Any) -> None:
		if self.searchtimer:
			self.after_managed_cancel(self.searchtimer)
		self.searchtimer = self.after_managed(200, self.updatelist)

	def ok(self, _: UI.Event | None = None) -> None:
		f = self.listbox.get(self.listbox.curselection()[0])
		self.file = 'MPQ:' + f
		history = self.history_config.data
		if f in history:
			history.remove(f)
		history.append(f)
		if len(history) > 10:
			del history[0]
		PyMSDialog.ok(self)

	def dismiss(self) -> None:
		self.window_geometry_config.save_size(self)
		PyMSDialog.dismiss(self)
