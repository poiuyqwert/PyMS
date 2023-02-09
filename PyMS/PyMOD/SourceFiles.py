
import os as _os

class SourceFolder(object):
	@classmethod
	def matches(cls, folder_name): # type: (str) -> float
		raise NotImplementedError(cls.__name__ + '.matches()')

	def __init__(self, path): # type: (str) -> SourceFolder
		self.path = path
		self.folders = [] # type: list[SourceFolder]
		self.files = [] # type: list[SourceFile]

	def display_name(self):
		return _os.path.basename(self.path)

	def compiled_name(self):
		return _os.path.basename(self.path)

	def add_folder(self, folder): # type: (SourceFolder) -> None
		self.folders.append(folder)

	def add_file(self, file): # type: (SourceFile) -> None
		self.files.append(file)

	def __repr__(self): # type: () -> str
		result = ' - %s' % self.display_name()
		for file in self.files:
			result += '\n  ' + repr(file)
		for folder in self.folders:
			result += '\n  ' + repr(folder).replace('\n', '\n  ')
		return result

class SourceFile(object):
	@classmethod
	def matches(cls, file_name): # type: (str) -> float
		raise NotImplementedError(cls.__name__ + '.matches()')

	def __init__(self, path): # type: (str) -> SourceFile
		raise NotImplementedError(self.__class__.__name__ + '.__init__()')

	def display_name(self): # type: () -> str
		raise NotImplementedError(self.__class__.__name__ + '.display_name()')

	def compiled_name(self): # type: () -> str
		raise NotImplementedError(self.__class__.__name__ + '.compiled_name()')

	def __repr__(self): # type: () -> str
		return ' - %s' % self.display_name()

class RawSourceFolder(SourceFolder):
	@classmethod
	def matches(cls, folder_name): # type: (str) -> float
		return 0.1

class MPQSourceFolder(SourceFolder):
	@classmethod
	def matches(cls, folder_name): # type: (str) -> float
		if folder_name.endswith('.mpq'):
			return 1
		return 0

class RawSourceFile(SourceFile):
	@classmethod
	def matches(cls, file_name): # type: (str) -> float
		return 0.1

	def __init__(self, path): # type: (str) -> RawSourceFile
		self.path = path

	def display_name(self): # type: () -> str
		return _os.path.basename(self.path)

	def compiled_name(self): # type: () -> str
		return _os.path.basename(self.path)

_FOLDER_TYPES = [
	MPQSourceFolder,
	RawSourceFolder
]
_FILE_TYPES = [
	RawSourceFile
]

def build_source_graph(project_path): # type: (str) -> SourceFolder
	root = None
	folders = {} # type: dict[str, SourceFolder]
	for folder_path, folder_names, file_names in _os.walk(project_path, topdown=True):
		folder_names[:] = list(folder_name for folder_name in folder_names if not folder_name.startswith('.'))
		parent_path, folder_name = _os.path.split(folder_path)
		detected_folder_type = None
		detected_folder_confidence = 0
		for folder_type in _FOLDER_TYPES:
			confidence = folder_type.matches(folder_name)
			if confidence > detected_folder_confidence:
				detected_folder_type = folder_type
				detected_folder_confidence = confidence
		folder = detected_folder_type(folder_path)
		folders[folder_path] = folder
		if root == None:
			root = folder
		parent_folder = folders.get(parent_path)
		if parent_folder:
			parent_folder.add_folder(folder)
		for file_name in file_names:
			if file_name.startswith('.'):
				continue
			detected_file_type = None
			detected_file_confidence = 0
			for file_type in _FILE_TYPES:
				confidence = file_type.matches(file_name)
				if confidence > detected_file_confidence:
					detected_file_type = file_type
					detected_file_confidence = confidence
			file = detected_file_type(_os.path.join(folder_path, file_name))
			folder.add_file(file)
	return root

if __name__ == '__main__':
	print(repr(build_source_graph('/Users/zachzahos/Documents/Personal/PyMS/Mod')))
