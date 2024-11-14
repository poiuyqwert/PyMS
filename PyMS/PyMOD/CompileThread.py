
from __future__ import annotations

from . import Source
from . import CompileStep
from .Meta import MetaHandler

from threading import Thread as _Thread
from queue import Queue as _Queue
from datetime import datetime as _datetime
import os as _os
import traceback as _traceback

class CompileThread(_Thread):
	class OutputMessage:
		class _Base:
			pass

		class Log(_Base):
			def __init__(self, text: str, tag: str | None = None) -> None:
				self.text = text
				self.tag = tag

	class InputMessage:
		class _Base:
			pass

		class Abort(_Base):
			pass

	def __init__(self, project_path: str, source_graph: Source.Item) -> None:
		_Thread.__init__(self)
		self.project_path = project_path
		self.build_path = _os.path.join(self.project_path, '.build')
		self.intermediates_path = _os.path.join(self.build_path, 'intermediates')
		self.artifacts_path = _os.path.join(self.build_path, 'artifacts')
		self.source_graph = source_graph
		self.input_queue: _Queue[CompileThread.InputMessage._Base] = _Queue()
		self.output_queue: _Queue[CompileThread.OutputMessage._Base] = _Queue()
		self.meta = MetaHandler(_os.path.join(self.build_path, 'meta.json'))

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

	def log(self, message: str, tag: str | None = None) -> None:
		self.output_queue.put(CompileThread.OutputMessage.Log(message, tag=tag))

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
			self.log('Compile aborted.')
		return abort

	def run(self) -> None:
		started = _datetime.now()
		self.log(f"Compile started at {started.strftime('%H:%M:%S')}...")

		buckets: dict[CompileStep.Bucket, list[CompileStep.BaseCompileStep]] = {
			CompileStep.Bucket.setup: [
				CompileStep.CreateDirectory(self, self.build_path),
				CompileStep.CleanupFolder(self, self.artifacts_path),
				CompileStep.CreateDirectory(self, self.artifacts_path),
				CompileStep.LoadMeta(self),
				CompileStep.DetermineSourceFiles(self),
			],
			CompileStep.Bucket.make_intermediates: [],
			CompileStep.Bucket.use_intermediates: [
				CompileStep.CleanupIntermediates(self),
			],
			CompileStep.Bucket.cleanup: [
				CompileStep.SaveMeta(self)
			]
		}
		for bucket in CompileStep.Bucket.order():
			steps = buckets[bucket]
			for step in steps:
				if self.check_abort():
					return
				try:
					self.log('\n')
					new_steps = step.execute()
					if new_steps:
						for new_step in new_steps:
							if new_step.bucket() < bucket:
								raise CompileStep.CompileError(f'Attempting to add new compile step to bucket `{new_step.bucket}` when in bucket `{bucket}')
							buckets[new_step.bucket()].append(new_step)
				except CompileStep.CompileError as e:
					self.log('ERROR: ' + str(e), tag='error')
					if e.internal_exception:
						self.log('INTERNAL ERROR:\n' + '\n'.join(_traceback.format_exception(e.internal_exception)), tag='error')
					return
				except:
					self.log('ERROR:\n' + _traceback.format_exc(), tag='error')
					return

		ended = _datetime.now()
		duration = ended - started
		self.log(f"\nCompile completed at {ended.strftime('%H:%M:%S')} ({duration.total_seconds()} seconds total)...", tag='success')
