
from .BaseCompileStep import BaseCompileStep, CompileError, Bucket

import os as _os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class CreateDirectory(BaseCompileStep):
	# Directories are legitimately created in multiple phases, so the bucket is caller-provided
	def __init__(self, compile_thread: 'CompileThread', path: str, bucket: Bucket) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.path = path
		self._bucket = bucket

	def bucket(self) -> Bucket:
		return self._bucket

	def execute(self) -> list[BaseCompileStep] | None:
		self.log(f'Checking directory: {self.path}')
		if _os.path.isdir(self.path):
			self.log('  Directory already exists!')
			return None
		self.log('  Creating directory...')
		try:
			_os.mkdir(self.path)
		except Exception as exc:
			raise CompileError(f"Couldn't create directory: {self.path}") from exc
		self.log('  Directory created!')
		return None
