
from ..FileFormats.GRP import CacheGRP

from ..Utilities.DataCache import DATA_CACHE

class IconData(object):
	def __init__(self):
		self.grp = None
		# TODO: Make tuple
		self.names = []
		self.images = {}

	def load_grp(self, mpqhandler, settings):
		try:
			grp = CacheGRP()
			grp.load_file(mpqhandler.get_file(settings.settings.files.get('cmdicons', 'MPQ:unit\\cmdbtns\\cmdicons.grp')))
		except:
			pass
		else:
			self.grp = grp
			self.images = {}

	def update_names(self):
		names = DATA_CACHE['Icons.txt']
		if self.grp:
			if self.grp.frames > len(names):
				names += ['Unknown'] * (len(names)-self.grp.frames)
			elif self.grp.frames < len(names):
				names = names[:self.grp.frames]
		self.names = names

	def frame_count(self):
		if self.grp:
			return self.grp.frames
		return len(self.names)
