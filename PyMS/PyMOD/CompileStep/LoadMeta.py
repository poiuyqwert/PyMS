
from .BaseCompileStep import BaseCompileStep, Bucket

class LoadMeta(BaseCompileStep):
	def bucket(self) -> Bucket:
		return Bucket.setup

	def execute(self) -> list[BaseCompileStep] | None:
		self.log('Loading `.build/meta.json`...')
		if not self.compile_thread.meta.exists():
			self.log("  `.build/meta.json` doesn't exist yet, continuing without it.")
			self.compile_thread.meta.ready = True
			return None
		if not self.compile_thread.meta.load():
			self.log("  Couldn't load `.build/meta.json`, continuing without it.", tag='warning')
			self.compile_thread.meta.ready = True
			return None
		self.log("  `.build/meta.json` loaded!")
		self.compile_thread.meta.ready = True
		return None
