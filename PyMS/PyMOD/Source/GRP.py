
from .File import File

import re as _re

class GRP(File):
	RE_GRP_NAME = _re.compile(r'.+?\.grp$')

	class Mode:
		Frames = 'f'
		ShadowFlare = 'sf'
		FrameSet = 'fs'

	@classmethod
	def matches(cls, folder_name: str) -> float:
		if GRP.RE_GRP_NAME.match(folder_name):
			return 1
		return 0

	def __init__(self, path: str) -> None:
		File.__init__(self, path)
		self.uncompressed = False
		self.mode = GRP.Mode.Frames
