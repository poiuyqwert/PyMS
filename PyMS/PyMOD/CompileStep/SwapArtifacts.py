
from .BaseCompileStep import BaseCompileStep, CompileError, Bucket

import os as _os
import shutil as _shutil

# Artifacts are built into the staging folder, and only swapped into the artifacts folder once the
# whole build has succeeded — so a failed or aborted compile never destroys the previous artifacts.
# The previous artifacts are moved aside first (rather than deleted) so they can be restored if
# publishing the staged artifacts fails.
class SwapArtifacts(BaseCompileStep):
	def bucket(self) -> Bucket:
		return Bucket.shutdown

	def execute(self) -> list[BaseCompileStep] | None:
		project = self.compile_thread.project
		self.log('Publishing artifacts...')
		if not _os.path.isdir(project.staging_path):
			raise CompileError(f'The staged artifacts are missing (expected at `{project.staging_path}`)')
		try:
			if _os.path.isdir(project.previous_artifacts_path):
				_shutil.rmtree(project.previous_artifacts_path)
			if _os.path.isdir(project.artifacts_path):
				_os.rename(project.artifacts_path, project.previous_artifacts_path)
		except Exception as exc:
			raise CompileError("Couldn't move the previous artifacts aside") from exc
		try:
			_os.rename(project.staging_path, project.artifacts_path)
		except Exception as exc:
			# Restore the previous artifacts so the user is never left without any
			if _os.path.isdir(project.previous_artifacts_path):
				try:
					_os.rename(project.previous_artifacts_path, project.artifacts_path)
				except Exception:
					pass
			raise CompileError("Couldn't publish the staged artifacts") from exc
		try:
			if _os.path.isdir(project.previous_artifacts_path):
				_shutil.rmtree(project.previous_artifacts_path)
		except Exception:
			self.log(f"  Previous artifacts at `{project.previous_artifacts_path}` couldn't be removed, continuing...", tag='warning')
		self.log('  Artifacts published!')
		return None
