
from ..FileFormats.GRP import CacheGRP

from ..Utilities.DataCache import DATA_CACHE

class IconData(object):
	def __init__(self, data_context):
		self.data_context = data_context
		self.grp = None
		self.names = ()
		self.images = {}

	def load_grp(self):
		try:
			grp = CacheGRP()
			path = self.data_context.settings.settings.files.get('cmdicons', 'MPQ:unit\\cmdbtns\\cmdicons.grp')
			grp.load_file(self.data_context.mpqhandler.get_file(path))
		except:
			pass
		else:
			self.grp = grp
			self.images = {}
			self.update_names()

	def update_names(self):
		names = DATA_CACHE['Icons.txt']
		if self.grp:
			if self.grp.frames > len(names):
				names += ['Unknown'] * (len(names)-self.grp.frames)
			elif self.grp.frames < len(names):
				names = names[:self.grp.frames]
		self.names = tuple(names)

	def frame_count(self):
		if self.grp:
			return self.grp.frames
		return len(self.names)
