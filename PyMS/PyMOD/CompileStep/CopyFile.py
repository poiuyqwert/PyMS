
from .BaseCompileStep import BaseCompileStep, CompileError, Bucket

import shutil as _shutil

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class CopyFile(BaseCompileStep):
	def __init__(self, compile_thread: 'CompileThread', source_path: str, destination_path: str) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.source_path = source_path
		self.destination_path = destination_path

	def bucket(self) -> Bucket:
		return Bucket.make_intermediates

	def execute(self) -> list[BaseCompileStep] | None:
		if not self.compile_thread.meta.check_requires_update([self.source_path], [self.destination_path]):
			self.log(f'No changes required for `{self.source_path}`.')
			return None
		self.log(f'Copying `{self.source_path}` to `{self.destination_path}`...')
		try:
			_shutil.copy2(self.source_path, self.destination_path)
		except:
			raise CompileError("Couldn't copy file")
		self.log('  Copy completed!')
		self.compile_thread.meta.update_output_metas([self.destination_path])
		return None
