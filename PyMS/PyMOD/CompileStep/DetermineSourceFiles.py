
from .BaseCompileStep import BaseCompileStep
from .CreateDirectory import CreateDirectory
from .BuildMPQ import BuildMPQ
from .CompileGRP import CompileGRP
from .CompileAIScript import CompileAIScript
from .CompileTBL import CompileTBL
from .CopyFile import CopyFile
from .. import Source

import os as _os

class DetermineSourceFiles(BaseCompileStep):
	def handle_source_item(self, source_item: Source.Item) -> list[BaseCompileStep]:
		steps: list[BaseCompileStep] = []
		if isinstance(source_item, Source.Folder):
			steps.extend(self.handle_source_folder(source_item))
		elif isinstance(source_item, Source.File):
			steps.extend(self.handle_source_file(source_item))
		return steps

	def handle_source_folder(self, source_folder: Source.Folder) -> list[BaseCompileStep]:
		steps: list[BaseCompileStep] = [
			CreateDirectory(self.compile_thread, self.compile_thread.project.source_path_to_intermediates_path(source_folder.path))
		]
		for source_item in source_folder.children:
			steps.extend(self.handle_source_item(source_item))
		if isinstance(source_folder, Source.MPQ):
			steps.append(BuildMPQ(self.compile_thread, source_folder))
		return steps

	def handle_source_file(self, source_file: Source.File) -> list[BaseCompileStep]:
		steps: list[BaseCompileStep] = []
		if isinstance(source_file, Source.GRP):
			steps.append(CompileGRP(self.compile_thread, source_file))
		elif isinstance(source_file, Source.AIScript):
			steps.append(CompileAIScript(self.compile_thread, source_file))
		elif isinstance(source_file, Source.TBL):
			steps.append(CompileTBL(self.compile_thread, source_file))
		else:
			destination_path = _os.path.join(_os.path.split(self.compile_thread.project.source_path_to_intermediates_path(source_file.path))[0], source_file.compiled_name())
			steps.append(CopyFile(self.compile_thread, source_file.path, destination_path))
		return steps

	def execute(self) -> list[BaseCompileStep] | None:
		self.log('Determining compile steps...')
		source_graph = self.compile_thread.project.source_graph
		if not source_graph:
			self.log('  No source files to compile')
			return None
		compile_steps = self.handle_source_item(source_graph)
		self.log('  Compile steps determined.')
		return compile_steps
