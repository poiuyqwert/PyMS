
from . import MegaEditorView

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog

class MegaEditor(PyMSDialog):
	def __init__(self, parent, settings, id):
		self.settings = settings
		self.id = id
		self.tileset = parent.tileset
		self.gettile = parent.gettile
		self.edited = False
		PyMSDialog.__init__(self, parent, 'MegaTile Editor [%s]' % id)

	def widgetize(self):
		self.editor = MegaEditorView.MegaEditorView(self, self.settings, self, self.id)
		self.editor.pack(side=TOP, padx=3, pady=(3,0))
		ok = Button(self, text='Ok', width=10, command=self.ok)
		ok.pack(side=BOTTOM, padx=3, pady=3)
		return ok

	def mark_edited(self):
		self.edited = True

	def megaload(self):
		self.editor.draw()

	def ok(self):
		if self.edited:
			from .TilePalette import TilePalette
			if self.editor.megatile_id in TilePalette.TILE_CACHE:
				del TilePalette.TILE_CACHE[self.editor.megatile_id]
			if hasattr(self.parent, 'megaload'):
				self.parent.megaload()
			if hasattr(self.parent, 'draw_tiles'):
				self.parent.draw_tiles(force=True)
			if hasattr(self.parent, 'mark_edited'):
				self.parent.mark_edited()
		PyMSDialog.ok(self)
