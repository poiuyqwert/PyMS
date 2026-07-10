
from .BaseCompileStep import BaseCompileStep, Bucket

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class SaveMeta(BaseCompileStep):
	def __init__(self, compile_thread: 'CompileThread', prune: bool = True) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.prune = prune

	def bucket(self) -> Bucket:
		return Bucket.shutdown

	def execute(self) -> list[BaseCompileStep] | None:
		self.log('Saving `.build/meta.json`...')
		if not self.compile_thread.meta.save(prune=self.prune):
			self.log("  Couldn't save `.build/meta.json` — incremental build info will be lost.", tag='warning')
			return None
		self.log("  `.build/meta.json` saved!")
		return None
