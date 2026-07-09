
from .BaseCompileStep import BaseCompileStep, Bucket

class SaveMeta(BaseCompileStep):
	def bucket(self) -> Bucket:
		return Bucket.shutdown

	def execute(self) -> list[BaseCompileStep] | None:
		self.log('Saving `.build/meta.json`...')
		if not self.compile_thread.meta.save():
			self.log("  Coldn't save `.build/meta.json`, continuing without it.", tag='warning')
			return None
		self.log("  `.build/meta.json` saved!")
		return None
