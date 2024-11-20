
from .BaseCompileStep import BaseCompileStep

class LoadMeta(BaseCompileStep):
	def execute(self) -> list[BaseCompileStep] | None:
		self.log('Loading `.build/meta.json`...')
		if not self.compile_thread.meta.exists():
			self.log("  `.build/meta.json` doesn't exist yet, continuing without it.")
			return None
		if not self.compile_thread.meta.load():
			self.log("  Coldn't load `.build/meta.json`, continuing without it.", tag='warning')
			return None
		self.log("  `.build/meta.json` loaded!")
		return None
