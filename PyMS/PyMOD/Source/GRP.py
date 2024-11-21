
from .File import File

import re, os

class GRP(File):
	RE_GRP_NAME = re.compile(r'.+?\.grp$')

	@classmethod
	def matches(cls, folder_name: str) -> float:
		if GRP.RE_GRP_NAME.match(folder_name):
			return 1
		return 0

	def frame_paths(self) -> list[str]:
		frame_paths: list[str] = []
		for filename in os.listdir(self.path):
			if filename.endswith('.bmp'):
				frame_paths.append(os.path.join(self.path, filename))
		return sorted(frame_paths)
