
from .BaseCompileStep import BaseCompileStep

class SaveMeta(BaseCompileStep):
	def execute(self) -> list[BaseCompileStep] | None:
		self.log('Saving `.build/meta.json`...')
		if not self.compile_thread.meta.save():
			self.log("  Coldn't save `.build/meta.json`, continuing without it.", tag='warning')
			return None
		self.log("  `.build/meta.json` saved!")
		return None
