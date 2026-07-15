
from __future__ import annotations

from .BaseCompileStep import BaseCompileStep, CompileError, Bucket
from .. import Source

from ...Utilities import Assets
from ...Utilities import JSON

import os as _os

from dataclasses import dataclass

from typing import TYPE_CHECKING, Self
if TYPE_CHECKING:
	from ..CompileThread import CompileThread
	from ...FileFormats.DAT.AbstractDAT import AbstractDAT

class CompileDAT(BaseCompileStep):
	@dataclass
	class Config(JSON.Decodable):
		entry_count: int | None

		@classmethod
		def from_json(cls, json: JSON.Object) -> Self:
			defaults = CompileDAT.Config.default()
			return cls(
				entry_count = JSON.get_available(json, 'entry_count', int, defaults.entry_count)
			)

		@staticmethod
		def default() -> CompileDAT.Config:
			return CompileDAT.Config(
				entry_count = None
			)

	def __init__(self, compile_thread: 'CompileThread', source_file: Source.DAT) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.source_file = source_file

	def bucket(self) -> Bucket:
		return Bucket.make_intermediates

	def base_dat_path(self) -> str:
		if base_dat_path := self.source_file.base_dat_path():
			return base_dat_path
		return Assets.mpq_file_path('arr', self.source_file.name)

	def load_base_dat(self, config: CompileDAT.Config) -> AbstractDAT:
		base_dat_path = self.base_dat_path()
		self.log(f'Loading base file `{base_dat_path}`...')
		dat = self.source_file.dat_type()()
		try:
			dat.load(base_dat_path)
		except Exception as e:
			raise CompileError(f"Couldn't load base file `{base_dat_path}`", internal_exception=e) from e
		self.log('  Base file loaded!')
		if config.entry_count is not None and config.entry_count > dat.entry_count():
			add = config.entry_count - dat.entry_count()
			if not dat.can_expand(add):
				raise CompileError(f"`{self.source_file.name}` can't be expanded to {config.entry_count} entries (max is {dat.FORMAT.expanded_max_entries})")
			self.log(f'Expanding `{self.source_file.name}` to {dat.expanded_count(dat.entry_count() + add)} entries...')
			dat.expand_entries(add)
			self.log('  Expanded!')
		if dat.is_expanded():
			self.log(f'`{self.source_file.name}` is expanded ({dat.entry_count()} entries), a plugin will be required for the game to use it.', tag='warning')
		return dat

	def execute(self) -> list[BaseCompileStep] | None:
		self.log(f'Determining DAT input files for `{self.source_file.display_name()}`...')
		text_paths = self.source_file.text_paths()
		self.log(f'  {len(text_paths)} input files found.', tag='warning' if not text_paths else None)
		if not text_paths:
			return None

		config: CompileDAT.Config = CompileDAT.Config.default()
		if loaded_config := self.load_config(CompileDAT.Config, self.source_file):
			config = loaded_config

		base_dat_path = self.base_dat_path()
		inputs = list(text_paths)
		inputs.append(base_dat_path)
		config_path = self.source_file.config_path()
		if _os.path.isfile(config_path):
			inputs.append(config_path)

		destination_path = self.compile_thread.project.source_path_to_intermediates_path(self.source_file.path, self.source_file.name)
		if not self.compile_thread.meta.check_requires_update(inputs, [destination_path]):
			self.log(f'No changes required for `{self.source_file.display_name()}`.')
			return None

		dat = self.load_base_dat(config)
		for text_path in text_paths:
			self.log(f'Importing `{text_path}`...')
			try:
				dat.import_file(text_path)
			except Exception as e:
				raise CompileError(f"Couldn't import `{text_path}`", internal_exception=e) from e
			self.log('  Imported!')
		self.log(f'Compiling `{self.source_file.display_name()}`...')
		try:
			dat.save(destination_path)
		except Exception as e:
			raise CompileError("Couldn't save DAT", internal_exception=e) from e
		self.log('  DAT compiled!')
		self.compile_thread.meta.update_input_metas(inputs)
		self.compile_thread.meta.update_output_metas([destination_path])
		return None
