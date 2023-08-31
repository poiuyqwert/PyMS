
from __future__ import annotations

from .Config import PyTILEConfig
from .Delegates import MainDelegate

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog

class MegaTileSettingsExporter(PyMSDialog):
	def __init__(self, parent: Misc, config: PyTILEConfig, ids: list[int], delegate: MainDelegate) -> None:
		self.config_ = config
		self.ids = ids
		self.delegate = delegate
		PyMSDialog.__init__(self, parent, 'Export MegaTile Settings', resizable=(False,False))

	def widgetize(self): # type: () -> (Misc | None)
		self.height = IntVar()
		self.height.set(self.config_.export.megatiles.height.value)
		self.walkability = IntVar()
		self.walkability.set(self.config_.export.megatiles.walkability.value)
		self.block_sight = IntVar()
		self.block_sight.set(self.config_.export.megatiles.block_sight.value)
		self.ramp = IntVar()
		self.ramp.set(self.config_.export.megatiles.ramp.value)

		f = LabelFrame(self, text='Export')
		Checkbutton(f, text='Height', variable=self.height, anchor=W).grid(column=0,row=0, sticky=W)
		Checkbutton(f, text='Walkability', variable=self.walkability, anchor=W).grid(column=1,row=0, sticky=W)
		Checkbutton(f, text='Block Sight', variable=self.block_sight, anchor=W).grid(column=0,row=1, sticky=W)
		Checkbutton(f, text='Ramp', variable=self.ramp, anchor=W).grid(column=1,row=1, sticky=W)
		f.pack(side=TOP, padx=3, pady=(3,0))

		buts = Frame(self)
		self.export_button = Button(buts, text='Export', state=DISABLED, command=self.export)
		self.export_button.pack(side=LEFT)
		Button(buts, text='Cancel', command=self.cancel).pack(side=RIGHT, padx=(10,0))
		buts.pack(side=BOTTOM, padx=3, pady=3)

		self.height.trace('w', self.update_states)
		self.walkability.trace('w', self.update_states)
		self.block_sight.trace('w', self.update_states)
		self.ramp.trace('w', self.update_states)
		self.update_states()

		return self.export_button

	def update_states(self, *_): # type: (Any) -> None
		any_on = self.height.get() or self.walkability.get() or self.block_sight.get() or self.ramp.get()
		self.export_button['state'] = NORMAL if any_on else DISABLED

	def export(self): # type: () -> None
		tileset = self.delegate.get_tileset()
		if not tileset:
			return
		path = self.config_.last_path.settings.select_save(self, title='Export MegaTile Settings')
		if not path:
			return
		tileset.export_megatile_settings(path, self.ids)
		self.ok()

	def dismiss(self): # type: () -> None
		self.config_.export.megatiles.height.value = not not self.height.get()
		self.config_.export.megatiles.walkability.value = not not self.walkability.get()
		self.config_.export.megatiles.block_sight.value = not not self.block_sight.get()
		self.config_.export.megatiles.ramp.value = not not self.ramp.get()
		PyMSDialog.dismiss(self)
