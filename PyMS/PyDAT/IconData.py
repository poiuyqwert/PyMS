
from .DataID import DataID

from ..FileFormats.GRP import CacheGRP, frame_to_photo
from ..FileFormats.PCX import PCX

from ..Utilities.Callback import Callback
from ..Utilities import Assets

class IconData(object):
	def __init__(self, data_context):
		self.data_context = data_context
		self.grp = None
		self.ticon_pcx = None
		self.names = ()
		self.images = {}

		self.update_cb = Callback()

	def load_grp(self):
		try:
			grp = CacheGRP()
			path = self.data_context.settings.settings.files.get('cmdicons', Assets.mpq_file_ref('unit', 'cmdbtns', 'cmdicons.grp'))
			grp.load_file(self.data_context.mpqhandler.get_file(path))
		except:
			pass
		else:
			self.grp = grp
			self.images = {}
			self.update_names()

	def load_ticon_pcx(self):
		try:
			pcx = PCX()
			path = self.data_context.settings.settings.files.get('ticon', Assets.mpq_file_ref('unit', 'cmdbtns', 'ticon.pcx'))
			pcx.load_file(self.data_context.mpqhandler.get_file(path))
		except:
			pass
		else:
			self.ticon_pcx = pcx
			self.images = {}

	def save_data(self):
		return self.grp.save_data()

	def update_names(self):
		names = Assets.data_cache(Assets.DataReference.Icons)
		if self.grp:
			if self.grp.frames > len(names):
				names += ['Unknown'] * (len(names)-self.grp.frames)
			elif self.grp.frames < len(names):
				names = names[:self.grp.frames]
		self.names = tuple(names)
		self.update_cb(DataID.cmdicons)

	def frame_count(self):
		if self.grp:
			return self.grp.frames
		return len(self.names)

	def frame_size(self):
		if self.grp:
			return (self.grp.width, self.grp.height)
		return (36, 34)
