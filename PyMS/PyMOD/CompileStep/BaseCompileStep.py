
from __future__ import annotations

from .. import Source

from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities import JSON

import os, enum

from typing import TYPE_CHECKING, TypeVar, Type
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class Bucket(enum.StrEnum):
	setup = enum.auto()
	make_intermediates = enum.auto()
	use_intermediates = enum.auto()
	make_artifacts = enum.auto()
	shutdown = enum.auto()

	@staticmethod
	def order() -> tuple[Bucket, ...]:
		return (Bucket.setup, Bucket.make_intermediates, Bucket.use_intermediates, Bucket.make_artifacts, Bucket.shutdown)

	def __lt__(self, other: str) -> bool:
		return Bucket.order().index(self) < Bucket.order().index(other)

class CompileError(Exception):
	def __init__(self, message: str, internal_exception: Exception | None = None):
		super().__init__(message)
		self.internal_exception = internal_exception

C = TypeVar('C', bound=JSON.Decodable)
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

	def warning(self, warning: PyMSWarning) -> None:
		self.compile_thread.output_queue.put(CompileThread.OutputMessage.Log(repr(warning), tag='warning'))

	def warnings(self, warnings: list[PyMSWarning]) -> None:
		for warning in warnings:
			self.warning(warning)

	def load_config(self, type: Type[C], source_item: Source.Item, optional: bool = False, log: bool = True) -> C | None:
		config_path = source_item.config_path()
		if log:
			self.log(f'Checking for `config.json` for `{source_item.name}`...')
		if not os.path.isfile(config_path):
			if log:
				self.log('  No `config.json` found, using default settings')
			return None
		try:
			config = JSON.load_file(config_path, type)
			if log:
				self.log('  Config loaded!')
			return config
		except Exception as e:
			if optional:
				if log:
					self.log("  Error loading `config.json`, continuing without it")
				return None
			raise CompileError("Couldn't load `config.json`", internal_exception=e)
