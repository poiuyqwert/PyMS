
from __future__ import annotations

from .SourceFiles import *

from ..Utilities.PyMSError import PyMSError

from threading import Thread as _Thread
from queue import Queue as _Queue
from datetime import datetime as _datetime
import os as _os
import traceback as _traceback
import json as _json
import hashlib as _hashlib
import shutil as _shutil

class MetaField:
	inputs = 'inputs'
	outputs = 'outputs'

class CompileError(Exception):
	def __init__(self, message: str, internal_exception: Exception | None = None):
		super().__init__(message)
		self.internal_exception = internal_exception

class BaseCompileStep:
	def __init__(self, compile_thread: CompileThread) -> None:
		self.compile_thread = compile_thread

	def execute(self) -> list[BaseCompileStep] | None:
		raise NotImplementedError(self.__class__.__name__ + '.execute()')

class CompileStep:
	class CreateDirectory(BaseCompileStep):
		def __init__(self, compile_thread: CompileThread, path: str) -> None:
			BaseCompileStep.__init__(self, compile_thread)
			self.path = path

		def execute(self) -> list[BaseCompileStep] | None:
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nChecking directory: %s' % self.path))
			if _os.path.isdir(self.path):
				self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  Directory already exists!'))
				return None
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  Creating directory...'))
			try:
				_os.mkdir(self.path)
			except:
				raise CompileError("Couldn't create directory: %s" % self.path)
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  Directory created!'))
			return None

	class LoadMeta(BaseCompileStep):
		def execute(self) -> list[BaseCompileStep] | None:
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nLoading `.build/meta.json`...'))
			if not _os.path.isfile(self.compile_thread.meta_path):
				self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log("  `.build/meta.json` doesn't exist yet, continuing without it..."))
				return None
			try:
				with open(self.compile_thread.meta_path, 'r') as meta_file:
					meta = _json.load(meta_file)
			except:
				self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log("  Coldn't load `.build/meta.json`, continuing without it...", tag='warning'))
				return None
			self.compile_thread.meta = meta
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log("  `.build/meta.json` loaded!"))
			return None

	class SaveMeta(BaseCompileStep):
		def execute(self) -> list[BaseCompileStep] | None:
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nSaving `.build/meta.json`...'))
			try:
				with open(self.compile_thread.meta_path, 'w') as meta_file:
					_json.dump(self.compile_thread.meta, meta_file, indent=4)
			except:
				self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log("  Coldn't save `.build/meta.json`, continuing without it...", tag='warning'))
				return None
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log("  `.build/meta.json` saved!"))
			return None

	class DetermineSourceFiles(BaseCompileStep):
		def handle_source_folder(self, source_folder: SourceFolder) -> list[BaseCompileStep]:
			steps: list[BaseCompileStep] = [
				CompileStep.CreateDirectory(self.compile_thread, self.compile_thread.source_path_to_intermediates_path(source_folder.path))
			]
			for source_file in source_folder.files:
				# TODO: Move logic into `SourceFile` classes?
				if isinstance(source_file, RawSourceFile):
					destination_path = _os.path.join(_os.path.split(self.compile_thread.source_path_to_intermediates_path(source_file.path))[0], source_file.compiled_name())
					steps.append(CompileStep.CopyFile(self.compile_thread, source_file.path, destination_path))
				elif isinstance(source_file, GRPSourceFile):
					steps.append(CompileStep.CompileGRP(self.compile_thread, source_file))
			for sub_source_folder in source_folder.folders:
				steps.extend(self.handle_source_folder(sub_source_folder))
			if isinstance(source_folder, MPQSourceFolder):
				steps.append(CompileStep.BuildMPQ(self.compile_thread, source_folder))
			return steps

		def execute(self) -> list[BaseCompileStep] | None:
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nDetermining compile steps...'))
			compile_steps = self.handle_source_folder(self.compile_thread.source_graph)
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  Compile steps determined.'))
			return compile_steps

	class CopyFile(BaseCompileStep):
		def __init__(self, compile_thread: CompileThread, source_path: str, destination_path: str) -> None:
			BaseCompileStep.__init__(self, compile_thread)
			self.source_path = source_path
			self.destination_path = destination_path

		def execute(self) -> list[BaseCompileStep] | None:
			if not _check_requires_update(self.compile_thread.meta, [self.source_path], [self.destination_path]):
				self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nNo changes required for `%s`.' % self.source_path))
				return None
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nCopying `%s` to `%s`...' % (self.source_path, self.destination_path)))
			try:
				_shutil.copy2(self.source_path, self.destination_path)
			except:
				raise CompileError("Couldn't copy file")
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  Copy completed!'))
			file_hashes = self.compile_thread.update_input_metas([self.source_path])
			self.compile_thread.update_meta_hashes(MetaField.outputs, [self.destination_path], file_hashes)
			return None

	class CompileGRP(BaseCompileStep):
		def __init__(self, compile_thread: CompileThread, source_file: GRPSourceFile) -> None:
			BaseCompileStep.__init__(self, compile_thread)
			self.source_file = source_file

		def execute(self) -> list[BaseCompileStep] | None:
			destination_path = _os.path.join(_os.path.split(self.compile_thread.source_path_to_intermediates_path(self.source_file.frame_paths[0]))[0], self.source_file.compiled_name())
			if not _check_requires_update(self.compile_thread.meta, self.source_file.frame_paths, [destination_path]):
				self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nNo changes required for `%s`.' % self.source_file.display_name()))
				return None
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nCompiling `%s`...' % self.source_file.display_name()))
			from ..FileFormats.BMP import BMP
			from ..FileFormats.GRP import GRP
			grp = GRP()
			bmp = BMP()
			size = None
			# TODO: Support "GRPSourecFile.Mode"'s
			for frame_path in sorted(self.source_file.frame_paths):
				try:
					bmp.load_file(frame_path, issize=size)
				except Exception as e:
					raise CompileError("Couldn't load '%s'" % frame_path, internal_exception=e)
				if size == None:
					size = (bmp.width, bmp.height)
				grp.add_frame(bmp.image)
			try:
				grp.save_file(destination_path)
			except Exception as e:
				raise CompileError("Couldn't save GRP", internal_exception=e)
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  GRP compiled!'))
			self.compile_thread.update_input_metas(self.source_file.frame_paths)
			self.compile_thread.update_output_metas([destination_path])
			return None

	class BuildMPQ(BaseCompileStep):
		def __init__(self, compile_thread: CompileThread, source_folder: MPQSourceFolder) -> None:
			BaseCompileStep.__init__(self, compile_thread)
			self.source_folder = source_folder

		def execute(self) -> list[BaseCompileStep] | None:
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nBuilding `%s`...' % _os.path.basename(self.source_folder.path)))
			intermediates_path = self.compile_thread.source_path_to_intermediates_path(self.source_folder.path)
			artifact_path = self.compile_thread.source_path_to_artifacts_path(self.source_folder.path)
			if artifact_path.endswith(_os.pathsep):
				artifact_path = artifact_path[:-1]
			from ..FileFormats.MPQ import MPQ
			mpq = MPQ.MPQ.of(artifact_path)
			with mpq.create():
				# TODO: Either need to build tree of intermediates to work on, or need to cleanup old intermediates
				for folder_path, _, file_names in _os.walk(intermediates_path):
					for file_name in file_names:
						if file_name.startswith('.'):
							continue
						file_path = _os.path.join(folder_path, file_name)
						mpq_file_name = '\\'.join(_os.path.normpath(_os.path.relpath(file_path, intermediates_path)).split(_os.path.sep))
						self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  Adding `%s`...' % mpq_file_name))
						# TODO: Compression?
						mpq.add_file(file_path, mpq_file_name)
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  MPQ built!'))
			return None

	class CleanupFolder(BaseCompileStep):
		def __init__(self, compile_thread: CompileThread, folder_path: str, required: bool = True) -> None:
			BaseCompileStep.__init__(self, compile_thread)
			self.folder_path = folder_path
			self.required = required

		def execute(self) -> list[BaseCompileStep] | None:
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nCleaning up contents of folder `%s`...' % self.folder_path))
			if not _os.path.isdir(self.folder_path):
				self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log("  Folder doesn't exit, no cleanup required"))
				return None
			had_error = False
			for name in _os.listdir(self.folder_path):
				path = _os.path.join(self.folder_path, name)
				try:
					if _os.path.isfile(path):
						_os.unlink(path)
					elif _os.path.isdir(path):
						_shutil.rmtree(path)
				except:
					if self.required:
						raise CompileError("Couldn't cleanup contents")
					else:
						had_error = True
						return None
			if had_error:
				self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  Cleanup done, but not fully complete.', tag='warning'))
			else:
				self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  Cleanup completed!'))
			return None

def _compute_file_hash(file_path: str) -> str:
	hash = _hashlib.sha256()

	with open(file_path, 'rb') as file:
		while True:
			# Reading is buffered, so we can read smaller chunks.
			chunk = file.read(hash.block_size)
			if not chunk:
				break
			hash.update(chunk)

	return hash.hexdigest()

def _check_requires_update(meta, input_file_paths, output_file_paths): # type: (dict, list[str], list[str]) -> bool
	if not meta:
		return True
	if not MetaField.inputs in meta or not isinstance(meta[MetaField.inputs], dict):
		return True
	if not MetaField.outputs in meta or not isinstance(meta[MetaField.outputs], dict):
		return True
	for output_file_path in output_file_paths:
		if not output_file_path in meta[MetaField.outputs]:
			return True
		if not _os.path.isfile(output_file_path):
			return True
		if _compute_file_hash(output_file_path) != meta[MetaField.outputs][output_file_path]:
			return True
	for input_file_path in input_file_paths:
		if not input_file_path in meta[MetaField.inputs]:
			return True
		if _compute_file_hash(input_file_path) != meta[MetaField.inputs][input_file_path]:
			return True
	return False

class CompileThread(_Thread):
	class OutputMessage:
		class _Base:
			pass

		class Log(_Base):
			def __init__(self, text, tag=None):
				self.text = text
				self.tag = tag

	class InputMessage:
		class _Base:
			pass

		class Abort(_Base):
			pass

	def __init__(self, project_path: str, source_graph: SourceFolder) -> None:
		_Thread.__init__(self)
		self.project_path = project_path
		self.build_path = _os.path.join(self.project_path, '.build')
		self.intermediates_path = _os.path.join(self.build_path, 'intermediates')
		self.meta_path = _os.path.join(self.build_path, 'meta.json')
		self.artifacts_path = _os.path.join(self.build_path, 'artifacts')
		self.source_graph = source_graph
		self.input_queue: _Queue[CompileThread.InputMessage._Base] = _Queue()
		self.output_queue: _Queue[CompileThread.OutputMessage._Base] = _Queue()
		self.meta: dict[str, dict[str, str]] = {}

	def source_path_to_intermediates_path(self, source_path: str, base_name: str | None = None) -> str:
		intermediates_path = source_path.replace(self.project_path, self.intermediates_path)
		if base_name:
			intermediates_path = _os.path.join(_os.path.split(intermediates_path)[0], base_name)
		return intermediates_path

	def source_path_to_artifacts_path(self, source_path: str, base_name: str | None = None) -> str:
		artifacts_path = source_path.replace(self.project_path, self.artifacts_path)
		if base_name:
			artifacts_path = _os.path.join(_os.path.split(artifacts_path)[0], base_name)
		return artifacts_path

	def check_abort(self) -> bool:
		abort = False
		while True:
			try:
				message = self.input_queue.get(False)
			except:
				break
			if isinstance(message, CompileThread.InputMessage.Abort):
				abort = True
				break
			self.input_queue.task_done()
		if abort:
			self.output_queue.put(CompileThread.OutputMessage.Log('Compile aborted.'))
		return abort

	def update_meta_hashes(self, type: str, file_paths: list[str], file_hashes: list[str] | None = None) -> list[str] | None:
		self.output_queue.put(CompileThread.OutputMessage.Log('Updating %s meta...' % type))
		if not file_hashes:
			try:
				file_hashes = list(_compute_file_hash(file_path) for file_path in file_paths)
			except:
				pass
		if not file_hashes:
			self.output_queue.put(CompileThread.OutputMessage.Log("  Couldn't update %s file hash meta." % type, tag='warning'))
			return None
		if not type in self.meta or not isinstance(self.meta[type], dict):
			self.meta[type] = {}
		for file_path,file_hash in zip(file_paths, file_hashes):
			self.meta[type][file_path] = file_hash
		self.output_queue.put(CompileThread.OutputMessage.Log('  %s file hash meta updated' % type.capitalize()))
		return file_hashes

	def update_input_metas(self, file_paths: list[str]) -> list[str] | None:
		return self.update_meta_hashes(MetaField.inputs, file_paths)

	def update_output_metas(self, file_paths: list[str]) -> list[str] | None:
		return self.update_meta_hashes(MetaField.outputs, file_paths)

	def run(self) -> None:
		started = _datetime.now()
		self.output_queue.put(CompileThread.OutputMessage.Log('Compile started at %s...' % started.strftime('%H:%M:%S')))

		steps: list[BaseCompileStep] = [
			CompileStep.CreateDirectory(self, self.build_path),
			CompileStep.CleanupFolder(self, self.artifacts_path),
			CompileStep.CreateDirectory(self, self.artifacts_path),
			CompileStep.LoadMeta(self),
			CompileStep.DetermineSourceFiles(self),
			CompileStep.SaveMeta(self)
		]
		for index,step in enumerate(steps):
			if self.check_abort():
				return
			try:
				new_steps = step.execute()
				if new_steps:
					steps[index+1:index+1] = new_steps
			except CompileError as e:
				self.output_queue.put(CompileThread.OutputMessage.Log('ERROR: ' + str(e), tag='error'))
				if e.internal_exception:
					self.output_queue.put(CompileThread.OutputMessage.Log('INTERNAL ERROR:\n' + '\n'.join(_traceback.format_exception(e.internal_exception)), tag='error'))
				return
			except:
				self.output_queue.put(CompileThread.OutputMessage.Log('ERROR:\n' + _traceback.format_exc(), tag='error'))
				return

		ended = _datetime.now()
		duration = ended - started
		self.output_queue.put(CompileThread.OutputMessage.Log('\nCompile completed at %s (%d seconds total)...' % (ended.strftime('%H:%M:%S'), duration.total_seconds()), tag='success'))
