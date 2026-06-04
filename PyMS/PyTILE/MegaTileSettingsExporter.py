
from __future__ import annotations

from .Config import PyTILEConfig
from .Delegates import MainDelegate

from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog

from typing import Any

class MegaTileSettingsExporter(PyMSDialog):
	def __init__(self, parent: UI.Misc, config: PyTILEConfig, ids: list[int], delegate: MainDelegate) -> None:
		self.config_ = config
		self.ids = ids
		self.delegate = delegate
		PyMSDialog.__init__(self, parent, 'Export MegaTile Settings', resizable=(False,False))

	def widgetize(self) -> UI.Misc | None:
		self.height = UI.IntVar()
		self.height.set(self.config_.export.megatiles.height.value)
		self.walkability = UI.IntVar()
		self.walkability.set(self.config_.export.megatiles.walkability.value)
		self.block_sight = UI.IntVar()
		self.block_sight.set(self.config_.export.megatiles.block_sight.value)
		self.ramp = UI.IntVar()
		self.ramp.set(self.config_.export.megatiles.ramp.value)

		f = UI.LabelFrame(self, text='Export')
		UI.Checkbutton(f, text='Height', variable=self.height, anchor=UI.W).grid(column=0,row=0, sticky=UI.W)
		UI.Checkbutton(f, text='Walkability', variable=self.walkability, anchor=UI.W).grid(column=1,row=0, sticky=UI.W)
		UI.Checkbutton(f, text='Block Sight', variable=self.block_sight, anchor=UI.W).grid(column=0,row=1, sticky=UI.W)
		UI.Checkbutton(f, text='Ramp', variable=self.ramp, anchor=UI.W).grid(column=1,row=1, sticky=UI.W)
		f.pack(side=UI.TOP, padx=3, pady=(3,0))

		buts = UI.Frame(self)
		self.export_button = UI.Button(buts, text='Export', state=UI.DISABLED, command=self.export)
		self.export_button.pack(side=UI.LEFT)
		UI.Button(buts, text='Cancel', command=self.cancel).pack(side=UI.RIGHT, padx=(10,0))
		buts.pack(side=UI.BOTTOM, padx=3, pady=3)

		self.height.trace_add('write', self.update_states)
		self.walkability.trace_add('write', self.update_states)
		self.block_sight.trace_add('write', self.update_states)
		self.ramp.trace_add('write', self.update_states)
		self.update_states()

		return self.export_button

	def update_states(self, *_: Any) -> None:
		any_on = self.height.get() or self.walkability.get() or self.block_sight.get() or self.ramp.get()
		self.export_button['state'] = UI.NORMAL if any_on else UI.DISABLED

	def export(self) -> None:
		tileset = self.delegate.get_tileset()
		if not tileset:
			return
		path = self.config_.last_path.settings.select_save(self, title='Export MegaTile Settings')
		if not path:
			return
		tileset.export_megatile_settings(path, self.ids)
		self.ok()

	def dismiss(self) -> None:
		self.config_.export.megatiles.height.value = not not self.height.get()
		self.config_.export.megatiles.walkability.value = not not self.walkability.get()
		self.config_.export.megatiles.block_sight.value = not not self.block_sight.get()
		self.config_.export.megatiles.ramp.value = not not self.ramp.get()
		PyMSDialog.dismiss(self)
