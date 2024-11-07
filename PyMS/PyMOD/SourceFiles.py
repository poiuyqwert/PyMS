
from __future__ import annotations

import os as _os
import re as _re

from typing import Type

class SourceFolder(object):
	@classmethod
	def matches(cls, folder_name: str) -> float:
		raise NotImplementedError(cls.__name__ + '.matches()')

	def __init__(self, path: str) -> None:
		self.path = path
		self.folders: list[SourceFolder] = []
		self.files: list[SourceFile] = []

	def display_name(self) -> str:
		return _os.path.basename(self.path)

	def compiled_name(self) -> str:
		return _os.path.basename(self.path)

	def add_folder(self, folder: SourceFolder) -> None:
		self.folders.append(folder)

	def add_file(self, file: SourceFile) -> None:
		self.files.append(file)

	def __repr__(self) -> str:
		result = ' - %s' % self.display_name()
		for file in self.files:
			result += '\n  ' + repr(file)
		for folder in self.folders:
			result += '\n  ' + repr(folder).replace('\n', '\n  ')
		return result

class RawSourceFolder(SourceFolder):
	@classmethod
	def matches(cls, folder_name: str) -> float:
		return 0.1

class MPQSourceFolder(SourceFolder):
	@classmethod
	def matches(cls, folder_name: str) -> float:
		if folder_name.endswith('.mpq'):
			return 1
		return 0

class SourceFile(object):
	@classmethod
	def matches(cls, file_name: str) -> float:
		raise NotImplementedError(cls.__name__ + '.matches()')

	def __init__(self, path: str) -> None:
		self.path = path

	def capture(self, file_path: str) -> bool:
		return False

	def display_name(self) -> str:
		raise NotImplementedError(self.__class__.__name__ + '.display_name()')

	def compiled_name(self) -> str:
		raise NotImplementedError(self.__class__.__name__ + '.compiled_name()')

	def __repr__(self) -> str:
		return ' - %s' % self.display_name()

class RawSourceFile(SourceFile):
	@classmethod
	def matches(cls, file_name: str) -> float:
		return 0.1

	def __init__(self, path: str) -> None:
		SourceFile.__init__(self, path)

	def display_name(self) -> str:
		return _os.path.basename(self.path)

	def compiled_name(self) -> str:
		return _os.path.basename(self.path)

class GRPSourceFile(SourceFile):
	RE_GRP_NAME = _re.compile(r'^(.+?\.grp)(.u)?(?:\.(sf|fs))?\.(\d+)\.bmp$')

	class Mode:
		ShadowFlare = 'sf'
		FrameSet = 'fs'

	@classmethod
	def matches(cls, file_name: str) -> float:
		if GRPSourceFile.RE_GRP_NAME.match(file_name):
			return 1
		return 0

	def __init__(self, path: str) -> None:
		SourceFile.__init__(self, path)
		file_name = _os.path.basename(path)
		match = GRPSourceFile.RE_GRP_NAME.match(file_name)
		assert match is not None
		self.grp_name = match.group(1)
		self.uncompressed = not not match.group(2)
		self.mode = match.group(3)
		self.frames = None
		if self.mode:
			self.frames = int(match.group(4))
		self.frame_paths = [path]

	def capture(self, path: str) -> bool:
		if self.mode:
			return False
		file_name = _os.path.basename(path)
		match = GRPSourceFile.RE_GRP_NAME.match(file_name)
		if not match:
			return False
		if match.group(1) != self.grp_name:
			return False
		self.frame_paths.append(path)
		return True

	def display_name(self) -> str:
		return self.grp_name

	def compiled_name(self) -> str:
		return self.grp_name

_FOLDER_TYPES: list[Type[SourceFolder]] = [
	MPQSourceFolder,
]
_FILE_TYPES: list[Type[SourceFile]] = [
	GRPSourceFile,
]

def build_source_graph(project_path: str) -> SourceFolder:
	root = RawSourceFolder(project_path)
	folders: dict[str, SourceFolder] = {}
	for folder_path, folder_names, file_names in _os.walk(project_path, topdown=True):
		folder_names[:] = list(folder_name for folder_name in folder_names if not folder_name.startswith('.'))
		parent_path, folder_name = _os.path.split(folder_path)
		detected_folder_type: Type[SourceFolder] = RawSourceFolder
		detected_folder_confidence: float = 0
		for folder_type in _FOLDER_TYPES:
			confidence = folder_type.matches(folder_name)
			if confidence > detected_folder_confidence:
				detected_folder_type = folder_type
				detected_folder_confidence = confidence
		folder = detected_folder_type(folder_path)
		folders[folder_path] = folder
		if root is None:
			root = folder
		parent_folder = folders.get(parent_path)
		if parent_folder:
			parent_folder.add_folder(folder)
		for file_name in file_names:
			if file_name.startswith('.'):
				continue
			file_path = _os.path.join(folder_path, file_name)
			captured = False
			for source_file in folder.files:
				captured = source_file.capture(file_path)
				if captured:
					break
			if captured:
				continue
			detected_file_type: Type[SourceFile] = RawSourceFile
			detected_file_confidence: float = 0
			for file_type in _FILE_TYPES:
				confidence = file_type.matches(file_name)
				if confidence > detected_file_confidence:
					detected_file_type = file_type
					detected_file_confidence = confidence
			file = detected_file_type(file_path)
			folder.add_file(file)
	return root

if __name__ == '__main__':
	print(repr(build_source_graph('/Users/zachzahos/Documents/Personal/PyMS/Mod')))
