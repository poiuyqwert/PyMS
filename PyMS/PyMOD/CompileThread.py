
from __future__ import annotations

from . import CompileStep
from .Meta import MetaHandler
from .Project import Project

from threading import Thread as _Thread
from queue import Queue as _Queue
from datetime import datetime as _datetime
import enum as _enum
import os as _os
import traceback as _traceback

class CompileResult(_enum.Enum):
	success = _enum.auto()
	failure = _enum.auto()
	aborted = _enum.auto()

class CompileThread(_Thread):
	class OutputMessage:
		class _Base:
			pass

		class Log(_Base):
			def __init__(self, text: str, tag: str | None = None) -> None:
				self.text = text
				self.tag = tag

		# Always the final message a compile emits, carrying the authoritative outcome (drivers
		# should not infer success from log messages)
		class Done(_Base):
			def __init__(self, result: CompileResult) -> None:
				self.result = result

	class InputMessage:
		class _Base:
			pass

		class Abort(_Base):
			pass

	def __init__(self, project: Project) -> None:
		_Thread.__init__(self)
		self.project = project
		self.input_queue: _Queue[CompileThread.InputMessage._Base] = _Queue()
		self.output_queue: _Queue[CompileThread.OutputMessage._Base] = _Queue()
		self.meta = MetaHandler(project.meta_path, project.path)

	def log(self, message: str, tag: str | None = None) -> None:
		self.output_queue.put(CompileThread.OutputMessage.Log(message, tag=tag))

	def check_abort(self) -> bool:
		abort = False
		while True:
			try:
				message = self.input_queue.get(False)
			except Exception:
				break
			if isinstance(message, CompileThread.InputMessage.Abort):
				abort = True
			self.input_queue.task_done()
			if abort:
				break
		if abort:
			self.log('Compile aborted.')
		return abort

	def save_partial_meta(self) -> None:
		# Preserve the hash bookkeeping from steps that completed before the abort/error, but only
		# once the on-disk meta has been loaded (otherwise saving would discard prior build info).
		# Entries are not pruned since not every step got a chance to mark its files as used.
		if not self.meta.ready:
			return
		self.log('\n')
		CompileStep.SaveMeta(self, prune=False).execute()

	def run(self) -> None:
		result = self._compile()
		self.output_queue.put(CompileThread.OutputMessage.Done(result))

	def _compile(self) -> CompileResult:
		started = _datetime.now()
		self.log(f"Compile started at {started.strftime('%H:%M:%S')}...")

		buckets: dict[CompileStep.Bucket, list[CompileStep.BaseCompileStep]] = {
			CompileStep.Bucket.setup: [
				CompileStep.CreateDirectory(self, self.project.build_path, CompileStep.Bucket.setup),
				# Clear out any staged artifacts left behind by an aborted or crashed compile
				CompileStep.CleanupFolder(self, self.project.staging_path),
				CompileStep.CreateDirectory(self, self.project.staging_path, CompileStep.Bucket.setup),
				CompileStep.LoadMeta(self),
				CompileStep.DetermineSourceFiles(self),
			],
			CompileStep.Bucket.make_intermediates: [],
			CompileStep.Bucket.use_intermediates: [],
			CompileStep.Bucket.make_artifacts: [
				CompileStep.CleanupIntermediates(self),
			],
			CompileStep.Bucket.shutdown: [
				CompileStep.SwapArtifacts(self),
				CompileStep.SaveMeta(self)
			]
		}
		for bucket in CompileStep.Bucket.order():
			steps = buckets[bucket]
			for step in steps:
				if self.check_abort():
					self.save_partial_meta()
					return CompileResult.aborted
				try:
					self.log('\n')
					new_steps = step.execute()
					if new_steps:
						for new_step in new_steps:
							if new_step.bucket() < bucket:
								raise CompileStep.CompileError(f'Attempting to add new compile step to bucket `{new_step.bucket()}` when in bucket `{bucket}`')
							buckets[new_step.bucket()].append(new_step)
				except CompileStep.CompileError as e:
					self.log('ERROR: ' + str(e), tag='error')
					if e.internal_exception:
						self.log('INTERNAL ERROR:\n' + '\n'.join(_traceback.format_exception(e.internal_exception)), tag='error')
					self.save_partial_meta()
					return CompileResult.failure
				except Exception:
					self.log('ERROR:\n' + _traceback.format_exc(), tag='error')
					self.save_partial_meta()
					return CompileResult.failure

		ended = _datetime.now()
		duration = ended - started
		self.log(f"\nCompile completed at {ended.strftime('%H:%M:%S')} ({duration.total_seconds()} seconds total)...", tag='success')
		return CompileResult.success
