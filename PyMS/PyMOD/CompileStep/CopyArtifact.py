
from .BaseCompileStep import BaseCompileStep, CompileError, Bucket

import os as _os
import shutil as _shutil

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

# Copies a compiled file from the intermediates into the artifacts. The artifacts folder is wiped
# at the start of every compile, so the copy is unconditional and needs no meta bookkeeping.
class CopyArtifact(BaseCompileStep):
	def __init__(self, compile_thread: 'CompileThread', source_path: str, destination_path: str) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.source_path = source_path
		self.destination_path = destination_path

	def bucket(self) -> Bucket:
		return Bucket.make_artifacts

	def execute(self) -> list[BaseCompileStep] | None:
		if not _os.path.isfile(self.source_path):
			self.log(f'No file at `{self.source_path}` to copy to artifacts.')
			return None
		self.log(f'Copying `{self.source_path}` to `{self.destination_path}`...')
		try:
			_os.makedirs(_os.path.dirname(self.destination_path), exist_ok=True)
			_shutil.copy2(self.source_path, self.destination_path)
		except Exception as exc:
			raise CompileError("Couldn't copy file to artifacts") from exc
		self.log('  Copy completed!')
		return None
