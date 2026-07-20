
from __future__ import annotations

from .BaseCompileStep import BaseCompileStep, CompileError, Bucket
from .. import Source

from ...Utilities import JSON

import os as _os

from dataclasses import dataclass

from typing import TYPE_CHECKING, Self
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class CompileSPK(BaseCompileStep):
	@dataclass
	class Config(JSON.Decodable):
		layer_count: int

		@classmethod
		def from_json(cls, json: JSON.Object) -> Self:
			defaults = CompileSPK.Config.default()
			return cls(
				layer_count = JSON.get_available(json, 'layer_count', int, defaults.layer_count)
			)

		@staticmethod
		def default() -> CompileSPK.Config:
			from ...FileFormats.SPK import SPK
			return CompileSPK.Config(
				layer_count = SPK.MAX_LAYERS
			)

	def __init__(self, compile_thread: 'CompileThread', source_file: Source.SPK) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.source_file = source_file

	def bucket(self) -> Bucket:
		return Bucket.make_intermediates

	def execute(self) -> list[BaseCompileStep] | None:
		from ...FileFormats.SPK import SPK
		source_path = _os.path.join(self.source_file.path, _os.path.splitext(self.source_file.name)[0] + '.bmp')
		inputs = [source_path]

		config: CompileSPK.Config = CompileSPK.Config.default()
		if loaded_config := self.load_config(CompileSPK.Config, self.source_file):
			config = loaded_config
		config_path = self.source_file.config_path()
		if _os.path.isfile(config_path):
			inputs.append(config_path)

		destination_path = self.compile_thread.project.source_path_to_intermediates_path(self.source_file.path, self.source_file.name)
		if not self.compile_thread.meta.check_requires_update(inputs, [destination_path]):
			self.log(f'No changes required for `{self.source_file.display_name()}`.')
			return None

		if config.layer_count < 1 or config.layer_count > SPK.MAX_LAYERS:
			raise CompileError(f'`layer_count` must be between 1 and {SPK.MAX_LAYERS} (got {config.layer_count})')

		self.log(f'Compiling `{self.source_file.display_name()}` ({config.layer_count} layers)...')
		spk = SPK()
		try:
			spk.interpret_file(source_path, config.layer_count)
		except Exception as e:
			raise CompileError(f"Couldn't compile SPK from '{source_path}'", internal_exception=e) from e
		try:
			spk.save(destination_path)
		except Exception as e:
			raise CompileError("Couldn't save SPK", internal_exception=e) from e
		self.log('  SPK compiled!')

		self.compile_thread.meta.update_metas(inputs, [destination_path])
		return None
