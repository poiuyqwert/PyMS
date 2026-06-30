
from __future__ import annotations

from .DataID import DATID, DataID

from ..FileFormats.MPQ.MPQ import MPQ, MPQCompressionFlag
from ..FileFormats.IScriptBIN.IScriptBIN import IScriptBIN

from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities import UIKit as UI
from ..Utilities import IO

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .Delegates import MainDelegate

class SaveMPQDialog(PyMSDialog):
	OPTIONS = (
		('units.dat', 'arr\\units.dat', DATID.units),
		('weapons.dat', 'arr\\weapons.dat', DATID.weapons),
		('flingy.dat', 'arr\\flingy.dat', DATID.flingy),
		('sprites.dat', 'arr\\sprites.dat', DATID.sprites),
		('images.dat', 'arr\\images.dat', DATID.images),
		('upgrades.dat', 'arr\\upgrades.dat', DATID.upgrades),
		('techdata.dat', 'arr\\techdata.dat', DATID.techdata),
		('sfxdata.dat', 'arr\\sfxdata.dat', DATID.sfxdata),
		('portdata.dat', 'arr\\portdata.dat', DATID.portdata),
		('mapdata.dat', 'arr\\mapdata.dat', DATID.mapdata),
		('orders.dat', 'arr\\orders.dat', DATID.orders),
		('stat_txt.tbl', 'rez\\stat_txt.tbl', DataID.stat_txt),
		('images.tbl', 'arr\\images.tbl', DataID.imagestbl),
		('sfxdata.tbl', 'arr\\sfxdata.tbl', DataID.sfxdatatbl),
		('portdata.tbl', 'arr\\portdata.tbl', DataID.portdatatbl),
		('mapdata.tbl', 'arr\\mapdata.tbl', DataID.mapdatatbl),
		('cmdicons.grp', 'unit\\cmdbtns\\cmdicons.grp', DataID.cmdicons)
	)

	def __init__(self, parent: UI.Misc, delegate: MainDelegate) -> None:
		self.delegate = delegate
		PyMSDialog.__init__(self, parent, 'Save MPQ', resizable=(False, False))

	def widgetize(self) -> UI.Misc | None:
		UI.Label(self, text='Select the files you want to save:', justify=UI.LEFT, anchor=UI.W).pack(fill=UI.X)
		self.listbox = UI.ScrolledListbox(self, selectmode=UI.MULTIPLE, font=UI.Font.fixed(), width=14, height=len(SaveMPQDialog.OPTIONS))
		self.listbox.pack(fill=UI.BOTH, expand=1, padx=5)
		sel = UI.Frame(self)
		UI.Button(sel, text='Select All', command=lambda: self.listbox.select_set(0,UI.END)).pack(side=UI.LEFT, fill=UI.X, expand=1)
		UI.Button(sel, text='Unselect All', command=lambda: self.listbox.select_clear(0,UI.END)).pack(side=UI.LEFT, fill=UI.X, expand=1)
		sel.pack(fill=UI.X, padx=5)
		for filename,_,_ in SaveMPQDialog.OPTIONS:
			self.listbox.insert(UI.END, filename)
			if filename in self.delegate.data_context.config.mpq_export.data:
				self.listbox.select_set(UI.END)
		btns = UI.Frame(self)
		save = UI.Button(btns, text='Save', width=10, command=self.save)
		save.pack(side=UI.LEFT, pady=5, padx=3)
		UI.Button(btns, text='Ok', width=10, command=self.ok).pack(side=UI.LEFT, pady=5, padx=3)
		btns.pack()
		return save

	def save(self) -> None:
		selected_options = [SaveMPQDialog.OPTIONS[i] for i in self.listbox.curselection()]
		if not selected_options:
			UI.MessageBox.showinfo(parent=self, title='Nothing to save', message='Please choose at least one item to save.')
		else:
			file = self.delegate.data_context.config.last_path.mpq.select_save(self)
			if file:
				not_saved: list[tuple[str, str]] = []
				try:
					mpq = MPQ.of(file)
					with mpq.open_or_create():
						buffer = None
						for filename,filepath,item_id in selected_options:
							try:
								if isinstance(item_id, DATID):
									dat_data = self.delegate.data_context.dat_data(item_id)
									buffer = dat_data.save_data()
								else:
									data_data = self.delegate.data_context.data_data(item_id)
									if isinstance(data_data, IScriptBIN):
										iscript_bin = data_data
										buffer = IO.output_to_bytes(iscript_bin.save)
									else:
										buffer = data_data.save_data()
								mpq.add_data(buffer, filepath, compression=MPQCompressionFlag.pkware)
								buffer = None
							except Exception as e:
								not_saved.append((filename, str(e)))
				except PyMSError as e:
					ErrorDialog(self, e)
					return
				if not_saved:
					details = '\n'.join(f'{filename}: {reason}' for filename,reason in not_saved)
					UI.MessageBox.showwarning(parent=self, title='Save problems', message=f'The following files could not be saved to the MPQ:\n\n{details}')

	def ok(self, _event: UI.Event | None = None) -> None:
		self.delegate.data_context.config.mpq_export.data = [self.listbox.get(i) for i in self.listbox.curselection()]
		PyMSDialog.ok(self)
