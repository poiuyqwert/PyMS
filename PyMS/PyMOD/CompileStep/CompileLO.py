
from .BaseCompileStep import BaseCompileStep, CompileError, Bucket
from .. import Source

import os as _os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class CompileLO(BaseCompileStep):
	def __init__(self, compile_thread: 'CompileThread', source_file: Source.LO) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.source_file = source_file

	def bucket(self) -> Bucket:
		return Bucket.make_intermediates

	def execute(self) -> list[BaseCompileStep] | None:
		from ...FileFormats.LO import LO
		source_path = _os.path.join(self.source_file.path, _os.path.splitext(self.source_file.name)[0] + '.txt')
		destination_path = self.compile_thread.project.source_path_to_intermediates_path(self.source_file.path, self.source_file.name)
		if not self.compile_thread.meta.check_requires_update([source_path], [destination_path]):
			self.log(f'No changes required for `{self.source_file.display_name()}`.')
			return None
		self.log(f'Parsing `{source_path}` to compile to LO*...')
		lo = LO()
		try:
			lo.interpret(source_path)
		except Exception as e:
			raise CompileError(f"Couldn't parse `{source_path}`", internal_exception=e) from e
		self.log('  Parsing completed!')
		self.log(f'Compiling `{self.source_file.display_name()}`...')
		try:
			lo.save(destination_path)
		except Exception as e:
			raise CompileError("Couldn't save LO*", internal_exception=e) from e
		self.log('  LO* compiled!')
		self.compile_thread.meta.update_metas([source_path], [destination_path])
		return None
