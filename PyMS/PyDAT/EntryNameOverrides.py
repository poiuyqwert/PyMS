
from __future__ import annotations

from ..Utilities.utils import lpad
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import UIKit as UI
from ..Utilities import Assets
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.PyMSError import PyMSError

import re

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .DataContext import DataContext
	from .DataID import DATID

RE_OVERRIDE = re.compile(r'\s*(\d{1,5})\s*(\+?)\s*:(.*)')

def apply_name_override(name_overrides: dict[int, tuple[bool, str]], entry_id: int, name: str, append: bool) -> None:
	# A non-blank name inserts/updates the override; a blank name removes any existing one.
	if name:
		name_overrides[entry_id] = (append, name)
	elif entry_id in name_overrides:
		del name_overrides[entry_id]

def remove_name_override(name_overrides: dict[int, tuple[bool, str]], entry_id: int) -> None:
	if entry_id in name_overrides:
		del name_overrides[entry_id]

class EntryNameOverrides(PyMSDialog):
	def __init__(self, parent: UI.Misc, data_context: DataContext, dat_id: DATID, entry_id: int | None = None) -> None:
		self.data_context = data_context
		self.dat_id = dat_id
		self.entry_id = UI.IntegerVar(val_range=(0, 99999))
		if entry_id:
			self.entry_id.set(entry_id)
		self.name = UI.StringVar()
		self.append = UI.IntVar()
		PyMSDialog.__init__(self, parent, f'{data_context.dat_data(dat_id).entry_type_name} Name Overrides', center=True, grabwait=True, escape=True, set_min_size=(True,True))

	def widgetize(self) -> UI.Misc | None:
		toolbar = UI.Toolbar(self)
		toolbar.add_button(Assets.get_image('open'), self.open, 'Open', UI.Ctrl.o)
		toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', UI.Ctrl.Alt.s)
		toolbar.pack(side=UI.TOP, fill=UI.X)

		self.listbox = UI.ScrolledListbox(self, font=UI.Font.fixed(), width=1, height=6)
		self.listbox.pack(side=UI.TOP, fill=UI.BOTH, expand=1, padx=3, pady=3)
		self.listbox.bind(UI.WidgetEvent.Listbox.Select(), self.selection_updated)

		f = UI.Frame(self)
		f.pack(side=UI.TOP, fill=UI.X, padx=3)

		UI.Label(f, text='ID:').pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.entry_id, width=5).pack(side=UI.LEFT, padx=3)
		UI.Label(f, text='Name:').pack(side=UI.LEFT)
		name_entry = UI.Entry(f, textvariable=self.name)
		name_entry.pack(side=UI.LEFT, fill=UI.X, expand=1)
		UI.Checkbutton(f, text="Append", variable=self.append).pack(side=UI.LEFT)
		UI.Button(f, text='Update', command=self.update_override).pack(side=UI.LEFT, padx=3)
		UI.Button(f, image=Assets.get_image('remove'), width=20, height=20, command=self.remove).pack(side=UI.LEFT)

		f = UI.Frame(self)
		f.pack(side=UI.TOP, fill=UI.X, padx=3, pady=3)

		UI.Button(f, text='Ok', command=self.ok).pack(side=UI.TOP)

		self.bind(UI.Key.Return(), self.update_override)

		self.refresh_list()

		name_overrides = self.data_context.dat_data(self.dat_id).name_overrides
		entry_id = self.entry_id.get()
		if entry_id in name_overrides:
			index = sorted(name_overrides.keys()).index(entry_id)
			self.listbox.select_set(index)
			self.listbox.see(index)
			self.selection_updated()

		name_entry.focus_set()
		name_entry.icursor(UI.END)

		return None

	def setup_complete(self) -> None:
		self.data_context.config.windows.entry_name_overrides.load_size(self)

	def refresh_list(self) -> None:
		y = self.listbox.yview()[0]
		self.listbox.delete(0,UI.END)
		name_overrides = self.data_context.dat_data(self.dat_id).name_overrides
		self.listbox.insert(UI.END, *[f' {lpad(str(entry_id), 5)} {"+" if name_overrides[entry_id][0] else " "} {name_overrides[entry_id][1]}' for entry_id in sorted(name_overrides.keys())])
		self.listbox.yview_moveto(y)

	def selection_updated(self, _: UI.Event | None = None) -> None:
		name_overrides = self.data_context.dat_data(self.dat_id).name_overrides
		entry_id = sorted(name_overrides.keys())[int(self.listbox.curselection()[0])]
		self.entry_id.set(entry_id)
		self.name.set(name_overrides[entry_id][1])
		self.append.set(name_overrides[entry_id][0])

	def open(self, _: UI.Event | None = None) -> None:
		path = self.data_context.config.last_path.entry_name_overrides.select_open(self)
		if not path:
			return
		try:
			self.data_context.dat_data(self.dat_id).load_name_overrides(path, update_names=False)
		except PyMSError as e:
			ErrorDialog(self, e)
		except Exception:
			ErrorDialog(self, PyMSError('Open', f"Couldn't open name overrides '{path}'"))
		self.refresh_list()

	def saveas(self, _: UI.Event | None = None) -> None:
		path = self.data_context.config.last_path.entry_name_overrides.select_save(self, filename=self.dat_id.filename.replace('.dat', '.txt'))
		if not path:
			return
		try:
			self.data_context.dat_data(self.dat_id).save_name_overrides(path)
		except Exception:
			ErrorDialog(self, PyMSError('Save', f"Couldn't save name overrides to '{path}'"))

	def update_override(self, _: UI.Event | None = None) -> None:
		name_overrides = self.data_context.dat_data(self.dat_id).name_overrides
		apply_name_override(name_overrides, self.entry_id.get(), self.name.get(), not not self.append.get())
		self.refresh_list()

	def remove(self) -> None:
		name_overrides = self.data_context.dat_data(self.dat_id).name_overrides
		remove_name_override(name_overrides, self.entry_id.get())
		self.refresh_list()

	def dismiss(self) -> None:
		self.data_context.config.windows.entry_name_overrides.save_size(self)
		self.data_context.dat_data(self.dat_id).update_names()
		PyMSDialog.dismiss(self)
