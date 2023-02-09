
from .SourceFiles import *

from threading import Thread as _Thread
from Queue import Queue as _Queue
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
	pass

class BaseCompileStep(object):
	def __init__(self, compile_thread): # type: (CompileThread) -> BaseCompileStep
		self.compile_thread = compile_thread

	def execute(self): # type: () -> (list[BaseCompileStep] | None)
		raise NotImplementedError(self.__class__.__name__ + '.execute()')

class CompileStep:
	class CreateDirectory(BaseCompileStep):
		def __init__(self, compile_thread, path): # type: (CompileThread, str) -> CompileStep.CreateDirectory
			BaseCompileStep.__init__(self, compile_thread)
			self.path = path

		def execute(self): # type: () -> (list[BaseCompileStep] | None)
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nChecking directory: %s' % self.path))
			if _os.path.isdir(self.path):
				self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  Directory already exists!'))
				return
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  Creating directory...'))
			try:
				_os.mkdir(self.path)
			except:
				raise CompileError("Couldn't create directory: %s" % self.path)
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  Directory created!'))

	class LoadMeta(BaseCompileStep):
		def execute(self): # type: () -> (list[BaseCompileStep] | None)
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nLoading `.build/meta.json`...'))
			if not _os.path.isfile(self.compile_thread.meta_path):
				self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log("  `.build/meta.json` doesn't exist yet, continuing without it..."))
				return
			try:
				with open(self.compile_thread.meta_path, 'r') as meta_file:
					meta = _json.load(meta_file)
			except:
				self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log("  Coldn't load `.build/meta.json`, continuing without it...", tag='warning'))
				return
			self.compile_thread.meta = meta
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log("  `.build/meta.json` loaded!"))

	class SaveMeta(BaseCompileStep):
		def execute(self): # type: () -> (list[BaseCompileStep] | None)
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nSaving `.build/meta.json`...'))
			try:
				with open(self.compile_thread.meta_path, 'w') as meta_file:
					_json.dump(self.compile_thread.meta, meta_file, indent=4)
			except:
				self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log("  Coldn't save `.build/meta.json`, continuing without it...", tag='warning'))
				return
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log("  `.build/meta.json` saved!"))

	class DetermineSourceFiles(BaseCompileStep):
		def handle_source_folder(self, source_folder): # type: (SourceFolder) -> list[BaseCompileStep]
			steps = [CompileStep.CreateDirectory(self.compile_thread, self.compile_thread.source_path_to_intermediates_path(source_folder.path))]
			for source_file in source_folder.files:
				if isinstance(source_file, RawSourceFile):
					destination_path = _os.path.join(_os.path.split(self.compile_thread.source_path_to_intermediates_path(source_file.path))[0], source_file.compiled_name())
					steps.append(CompileStep.CopyFile(self.compile_thread, source_file.path, destination_path))
			for sub_source_folder in source_folder.folders:
				steps.extend(self.handle_source_folder(sub_source_folder))
			return steps

		def execute(self): # type: () -> (list[BaseCompileStep] | None)
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nDetermining compile steps...'))
			compile_steps = self.handle_source_folder(self.compile_thread.source_graph)
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  Compile steps determined.'))
			return compile_steps

	class CopyFile(BaseCompileStep):
		def __init__(self, compile_thread, source_path, destination_path): # type: (CompileThread, str, str) -> CompileStep.CopyFile
			BaseCompileStep.__init__(self, compile_thread)
			self.source_path = source_path
			self.destination_path = destination_path

		def execute(self): # type: () -> (list[BaseCompileStep] | None)
			if not requires_update(self.compile_thread.meta, [self.source_path], [self.destination_path]):
				self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nNo changes required for `%s`.' % self.source_path))
				return
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('\nCopying `%s` to `%s`...' % (self.source_path, self.destination_path)))
			try:
				_shutil.copy2(self.source_path, self.destination_path)
			except:
				raise CompileError("Couldn't copy file")
			self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log('  Copy completed!'))
			file_hash = self.compile_thread.update_input_meta(self.source_path)
			self.compile_thread.update_meta_hash(MetaField.outputs, self.destination_path, file_hash)

def compute_file_hash(file_path): # type: (str) -> (str | None)
	try:
		hash = _hashlib.sha256()

		with open(file_path, 'rb') as file:
			while True:
				# Reading is buffered, so we can read smaller chunks.
				chunk = file.read(hash.block_size)
				if not chunk:
					break
				hash.update(chunk)

		return hash.hexdigest()
	except:
		return None

def requires_update(meta, input_file_paths, output_file_paths): # type: (dict, list[str], list[str]) -> bool
	if not meta:
		return True
	if not MetaField.inputs in meta or not isinstance(meta[MetaField.inputs], dict):
		return True
	if not MetaField.outputs in meta or not isinstance(meta[MetaField.outputs], dict):
		return True
	for input_file_path in input_file_paths:
		if not input_file_path in meta[MetaField.inputs]:
			return True
		if compute_file_hash(input_file_path) != meta[MetaField.inputs][input_file_path]:
			return True
	for output_file_path in output_file_paths:
		if not output_file_path in meta[MetaField.outputs]:
			return True
		if not _os.path.isfile(output_file_path):
			return True
		if compute_file_hash(output_file_path) != meta[MetaField.outputs][output_file_path]:
			return True
	return False

class CompileThread(_Thread):
	class OutputMessage:
		class Log(object):
			def __init__(self, text, tag=None):
				self.text = text
				self.tag = tag

	class InputMessage:
		class Abort(object):
			pass

	def __init__(self, project_path, source_graph): # type: (str, SourceFolder) -> CompileThread
		_Thread.__init__(self)
		self.project_path = project_path
		self.build_path = _os.path.join(self.project_path, '.build')
		self.intermediates_path = _os.path.join(self.build_path, 'intermediates')
		self.meta_path = _os.path.join(self.build_path, 'meta.json')
		self.source_graph = source_graph
		self.input_queue = _Queue()
		self.output_queue = _Queue()
		self.meta = {}

	def source_path_to_intermediates_path(self, source_path):
		return source_path.replace(self.project_path, self.intermediates_path)

	def check_abort(self):
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

	def update_meta_hash(self, type, file_path, file_hash=None): # type: (str, str, str | None) -> str
		self.output_queue.put(CompileThread.OutputMessage.Log('Updating %s meta...' % type))
		if not file_hash:
			file_hash = compute_file_hash(file_path)
		if not file_hash:
			self.output_queue.put(CompileThread.OutputMessage.Log("  Couldn't update file hash meta.", tag='warning'))
			return
		if not type in self.meta or not isinstance(self.meta[type], dict):
			self.meta[type] = {}
		self.meta[type][file_path] = file_hash
		self.output_queue.put(CompileThread.OutputMessage.Log('  File hash meta updated'))
		return file_hash

	def update_input_meta(self, file_path): # type: (str) -> str
		return self.update_meta_hash(MetaField.inputs, file_path)

	def update_output_meta(self, file_path): # type: (str) -> str
		return self.update_meta_hash(MetaField.outputs, file_path)

	def run(self):
		started = _datetime.now()
		self.output_queue.put(CompileThread.OutputMessage.Log('Compile started at %s...' % started.strftime('%H:%M:%S')))

		steps = [
			CompileStep.CreateDirectory(self, self.build_path),
			CompileStep.LoadMeta(self),
			CompileStep.DetermineSourceFiles(self),
			CompileStep.SaveMeta(self)
		] # type: list[BaseCompileStep]
		for index,step in enumerate(steps):
			if self.check_abort():
				return
			try:
				new_steps = step.execute()
				if new_steps:
					steps[index+1:index+1] = new_steps
			except CompileError as e:
				self.output_queue.put(CompileThread.OutputMessage.Log('ERROR: ' + str(e), tag='error'))
				return
			except:
				self.output_queue.put(CompileThread.OutputMessage.Log('ERROR:\n' + _traceback.format_exc(), tag='error'))
				return

		ended = _datetime.now()
		duration = ended - started
		self.output_queue.put(CompileThread.OutputMessage.Log('\nCompile completed at %s (%d seconds total)...' % (ended.strftime('%H:%M:%S'), duration.total_seconds()), tag='success'))
