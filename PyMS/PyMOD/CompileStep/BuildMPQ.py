
from .BaseCompileStep import BaseCompileStep, Bucket
from .. import Source

import os as _os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class BuildMPQ(BaseCompileStep):
	def __init__(self, compile_thread: 'CompileThread', source_folder: Source.MPQ) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.source_folder = source_folder

	def bucket(self) -> Bucket:
		return Bucket.use_intermediates

	def execute(self) -> list[BaseCompileStep] | None:
		self.log(f'Building `{_os.path.basename(self.source_folder.path)}`...')
		intermediates_path = self.compile_thread.source_path_to_intermediates_path(self.source_folder.path)
		artifact_path = self.compile_thread.source_path_to_artifacts_path(self.source_folder.path)
		if artifact_path.endswith(_os.pathsep):
			artifact_path = artifact_path[:-1]
		from ...FileFormats.MPQ import MPQ
		mpq = MPQ.MPQ.of(artifact_path)
		with mpq.create():
			# TODO: Double check file is a used input?
			for folder_path, _, file_names in _os.walk(intermediates_path):
				for file_name in file_names:
					if file_name.startswith('.'):
						continue
					file_path = _os.path.join(folder_path, file_name)
					mpq_file_name = '\\'.join(_os.path.normpath(_os.path.relpath(file_path, intermediates_path)).split(_os.path.sep))
					self.log(f'  Adding `{mpq_file_name}`...')
					# TODO: Compression?
					mpq.add_file(file_path, mpq_file_name)
		self.log('  MPQ built!')
		return None
