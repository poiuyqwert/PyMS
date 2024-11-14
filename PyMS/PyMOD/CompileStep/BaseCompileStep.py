
from __future__ import annotations

from enum import StrEnum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class Bucket(StrEnum):
	setup = 'setup'
	make_intermediates = 'make_intermediates'
	use_intermediates = 'use_intermediates'
	cleanup = 'cleanup'

	@staticmethod
	def order() -> tuple[Bucket, ...]:
		return (Bucket.setup, Bucket.make_intermediates, Bucket.use_intermediates, Bucket.cleanup)

	def __lt__(self, other: str) -> bool:
		return Bucket.order().index(self) < Bucket.order().index(other)

class CompileError(Exception):
	def __init__(self, message: str, internal_exception: Exception | None = None):
		super().__init__(message)
		self.internal_exception = internal_exception

class BaseCompileStep:
	def __init__(self, compile_thread: 'CompileThread') -> None:
		self.compile_thread = compile_thread

	def bucket(self) -> Bucket:
		raise NotImplementedError(self.__class__.__name__ + '.bucket()')

	def execute(self) -> list[BaseCompileStep] | None:
		raise NotImplementedError(self.__class__.__name__ + '.execute()')

	def log(self, message: str, tag: str | None = None) -> None:
		from ..CompileThread import CompileThread
		self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log(message, tag=tag))
