
from .BaseCompileStep import BaseCompileStep

import os as _os

class CleanupIntermediates(BaseCompileStep):
	def execute(self) -> list[BaseCompileStep] | None:
		self.log(f'Cleaning up intermediate files...')
		if not _os.path.isdir(self.compile_thread.intermediates_path):
			self.log("  Folder doesn't exit, no cleanup required")
			return None
		for folder_path, _, file_names in _os.walk(self.compile_thread.intermediates_path):
			for file_name in file_names:
				file_path = _os.path.join(folder_path, file_name)
				if not file_path in self.compile_thread.meta.used_outputs:
					try:
						_os.unlink(file_path)
					except:
						self.log(f"  Old intermediate `{file_path}` couldn't be deleted, continuing...", tag='warning')
		self.log('  Cleanup completed!')
		return None
