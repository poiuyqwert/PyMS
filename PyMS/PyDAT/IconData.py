
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
	def __init__(self, data_context: DataContext) -> None:
		self.data_context = data_context
		self.grp: CacheGRP | None = None
		self.ticon_pcx: PCX | None = None
		self.names: tuple[str, ...] = ()
		self.images: dict[bool, dict[int, ImageWithBounds]] = {}

		self.update_cb: Callback[DataID] = Callback()

	def load_grp(self) -> None:
		try:
			grp = CacheGRP()
			path = self.data_context.config.settings.files.cmdicons.file_path
			grp.load_file(self.data_context.mpq_handler.load_file(path))
		except:
			pass
		else:
			self.grp = grp
			self.images = {}
			self.update_names()

	def load_ticon_pcx(self) -> None:
		try:
			pcx = PCX()
			path = self.data_context.config.settings.files.ticon.file_path
			pcx.load_file(self.data_context.mpq_handler.load_file(path))
		except:
			pass
		else:
			self.ticon_pcx = pcx
			self.images = {}

	def save_data(self) -> bytes:
		assert self.grp is not None
		return self.grp.save_data()

	def update_names(self) -> None:
		names = Assets.data_cache(Assets.DataReference.Icons)
		if self.grp:
			if self.grp.frames > len(names):
				names += ['Unknown'] * (len(names)-self.grp.frames)
			elif self.grp.frames < len(names):
				names = names[:self.grp.frames]
		self.names = tuple(names)
		self.update_cb(DataID.cmdicons)

	def frame_count(self) -> int:
		if self.grp:
			return self.grp.frames
		return len(self.names)

	def frame_size(self) -> tuple[int, int]:
		if self.grp:
			return (self.grp.width, self.grp.height)
		return (36, 34)
