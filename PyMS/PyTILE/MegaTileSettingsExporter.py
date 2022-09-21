
from ..FileFormats.Tileset.Tileset import TILETYPE_MEGA

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.FileType import FileType

class MegaTileSettingsExporter(PyMSDialog):
	def __init__(self, parent, settings, ids):
		self.settings = settings
		self.ids = ids
		self.tileset = parent.tileset
		PyMSDialog.__init__(self, parent, 'Export MegaTile Settings', resizable=(False,False))

	def widgetize(self):
		self.height = IntVar()
		self.height.set(self.settings.export.megatiles.get('height',True))
		self.walkability = IntVar()
		self.walkability.set(self.settings.export.megatiles.get('walkability',True))
		self.block_sight = IntVar()
		self.block_sight.set(self.settings.export.megatiles.get('block_sight',True))
		self.ramp = IntVar()
		self.ramp.set(self.settings.export.megatiles.get('ramp',True))

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

	def update_states(self, *_):
		any_on = self.height.get() or self.walkability.get() or self.block_sight.get() or self.ramp.get()
		self.export_button['state'] = NORMAL if any_on else DISABLED

	def export(self):
		path = self.settings.lastpath.settings.select_save_file(self, key='export', title='Export MegaTile Settings', filetypes=[FileType.txt()])
		if path:
			self.tileset.export_settings(TILETYPE_MEGA, path, self.ids)
			self.ok()

	def dismiss(self):
		self.settings.export.megatiles.height = not not self.height.get()
		self.settings.export.megatiles.walkability = not not self.walkability.get()
		self.settings.export.megatiles.block_sight = not not self.block_sight.get()
		self.settings.export.megatiles.ramp = not not self.ramp.get()
		PyMSDialog.dismiss(self)
