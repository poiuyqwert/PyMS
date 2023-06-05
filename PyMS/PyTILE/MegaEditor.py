
from . import MegaEditorView
from .Delegates import MegaEditorDelegate, MegaEditorViewDelegate

from ..FileFormats.Tileset.Tileset import Tileset
from ..FileFormats.Tileset.VX4 import VX4Minitile

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.Settings import Settings

class MegaEditor(PyMSDialog, MegaEditorViewDelegate):
	def __init__(self, parent, settings, delegate, id): # type: (Misc, Settings, MegaEditorDelegate, int) -> None
		self.settings = settings
		self.delegate = delegate
		self.id = id
		self.edited = False
		PyMSDialog.__init__(self, parent, 'MegaTile Editor [%s]' % id)

	def widgetize(self):
		self.editor = MegaEditorView.MegaEditorView(self, self.settings, self, self.id)
		self.editor.pack(side=TOP, padx=3, pady=(3,0))
		ok = Button(self, text='Ok', width=10, command=self.ok)
		ok.pack(side=BOTTOM, padx=3, pady=3)
		return ok

	def get_tileset(self): # type: () -> (Tileset | None)
		return self.delegate.get_tileset()

	def get_tile(self, id): # type: (int | VX4Minitile) -> Image
		return self.delegate.get_tile(id)

	def mega_edit_mode_updated(self, mode): # type: (MegaEditorView.MegaEditorView.Mode) -> None
		pass

	def draw_group(self): # type: () -> None
		pass

	def mark_edited(self):
		self.edited = True

	def megaload(self):
		self.editor.draw()

	def ok(self):
		if self.edited:
			from .TilePalette import TilePalette
			if self.editor.megatile_id in TilePalette.TILE_CACHE:
				del TilePalette.TILE_CACHE[self.editor.megatile_id]
			self.delegate.megaload()
			self.delegate.draw_tiles(force=True)
			self.delegate.mark_edited()
		PyMSDialog.ok(self)
