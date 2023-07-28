
from __future__ import annotations

from .DataID import DataID

from ..FileFormats.GRP import CacheGRP, ImageWithBounds
from ..FileFormats.PCX import PCX

from ..Utilities.Callback import Callback
from ..Utilities import Assets
from ..Utilities.UIKit import Image

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .DataContext import DataContext

class IconData(object):
	def __init__(self, data_context): # type: (DataContext) -> None
		self.data_context = data_context
		self.grp = None # type: CacheGRP | None
		self.ticon_pcx = None # type: PCX | None
		self.names = () # type: tuple[str, ...]
		self.images = {} # type: dict[bool, dict[int, ImageWithBounds]]

		self.update_cb = Callback()

	def load_grp(self): # type: () -> None
		try:
			grp = CacheGRP()
			path = self.data_context.settings.settings.files.get('cmdicons', Assets.mpq_file_ref('unit', 'cmdbtns', 'cmdicons.grp'))
			grp.load_file(self.data_context.mpqhandler.load_file(path))
		except:
			pass
		else:
			self.grp = grp
			self.images = {}
			self.update_names()

	def load_ticon_pcx(self): # type: () -> None
		try:
			pcx = PCX()
			path = self.data_context.settings.settings.files.get('ticon', Assets.mpq_file_ref('unit', 'cmdbtns', 'ticon.pcx'))
			pcx.load_file(self.data_context.mpqhandler.load_file(path))
		except:
			pass
		else:
			self.ticon_pcx = pcx
			self.images = {}

	def save_data(self): # type: () -> bytes
		assert self.grp is not None
		return self.grp.save_data()

	def update_names(self): # type: () -> None
		names = Assets.data_cache(Assets.DataReference.Icons)
		if self.grp:
			if self.grp.frames > len(names):
				names += ['Unknown'] * (len(names)-self.grp.frames)
			elif self.grp.frames < len(names):
				names = names[:self.grp.frames]
		self.names = tuple(names)
		self.update_cb(DataID.cmdicons)

	def frame_count(self): # type: () -> int
		if self.grp:
			return self.grp.frames
		return len(self.names)

	def frame_size(self): # type: () -> tuple[int, int]
		if self.grp:
			return (self.grp.width, self.grp.height)
		return (36, 34)
