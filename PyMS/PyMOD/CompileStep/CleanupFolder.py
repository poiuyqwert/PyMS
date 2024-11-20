
from .BaseCompileStep import BaseCompileStep, CompileError

import os as _os
import shutil as _shutil

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class CleanupFolder(BaseCompileStep):
	def __init__(self, compile_thread: 'CompileThread', folder_path: str, required: bool = True) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.folder_path = folder_path
		self.required = required

	def execute(self) -> list[BaseCompileStep] | None:
		self.log(f'Cleaning up contents of folder `{self.folder_path}`...')
		if not _os.path.isdir(self.folder_path):
			self.log("  Folder doesn't exist, no cleanup required")
			return None
		had_error = False
		for name in _os.listdir(self.folder_path):
			path = _os.path.join(self.folder_path, name)
			try:
				if _os.path.isfile(path):
					_os.unlink(path)
				elif _os.path.isdir(path):
					_shutil.rmtree(path)
			except:
				if self.required:
					raise CompileError("Couldn't cleanup contents")
				else:
					had_error = True
					return None
		if had_error:
			self.log('  Cleanup done, but not fully complete.', tag='warning')
		else:
			self.log('  Cleanup completed!')
		return None
