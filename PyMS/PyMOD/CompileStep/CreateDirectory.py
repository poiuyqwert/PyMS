
from .BaseCompileStep import BaseCompileStep, CompileError, Bucket

import os as _os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class CreateDirectory(BaseCompileStep):
	def __init__(self, compile_thread: 'CompileThread', path: str) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.path = path

	def bucket(self) -> Bucket:
		return Bucket.make_intermediates

	def execute(self) -> list[BaseCompileStep] | None:
		self.log(f'Checking directory: {self.path}')
		if _os.path.isdir(self.path):
			self.log('  Directory already exists!')
			return None
		self.log('  Creating directory...')
		try:
			_os.mkdir(self.path)
		except:
			raise CompileError("Couldn't create directory: %s" % self.path)
		self.log('  Directory created!')
		return None
