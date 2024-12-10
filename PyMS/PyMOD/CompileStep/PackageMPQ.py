
from __future__ import annotations

from .BaseCompileStep import BaseCompileStep, Bucket
from .. import Source

from ...FileFormats.MPQ.MPQ import MPQ
from ...PyMPQ.CompressionSetting import CompressionOption, CompressionSetting
from ...Utilities import JSON

import os
from dataclasses import dataclass

from typing import TYPE_CHECKING, Self
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class PackageMPQ(BaseCompileStep):
	@dataclass
	class Config(JSON.Decodable):
		max_files: int
		block_size: int
		autocompression: dict[str, str]

		@classmethod
		def from_json(cls, json: JSON.Object) -> Self:
			defaults = PackageMPQ.Config.default()
			return cls(
				max_files = JSON.get_available(json, 'max_files', int, defaults.max_files),
				block_size = JSON.get_available(json, 'block_size', int, defaults.block_size),
				autocompression = JSON.get_available(json, 'autocompression', dict, defaults.autocompression)
			)

		@staticmethod
		def default() -> PackageMPQ.Config:
			return PackageMPQ.Config(
				max_files = 1024,
				block_size = 3,
				autocompression = {
					'Default': str(CompressionOption.Standard.setting()),
					'.smk': str(CompressionOption.NoCompression.setting()),
					'.mpq': str(CompressionOption.NoCompression.setting()),
					'.wav': str(CompressionOption.Audio.setting(level=1))
				}
			)

	@dataclass
	class FileConfig(JSON.Decodable):
		compression: str

		@classmethod
		def from_json(cls, json: JSON.Object) -> Self:
			return cls(
				compression = JSON.get(json, 'compression', str)
			)

	def __init__(self, compile_thread: 'CompileThread', source_folder: Source.MPQ) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.source_folder = source_folder
		self.mpq_intermediates_path = self.compile_thread.project.source_path_to_intermediates_path(self.source_folder.path)
		self.config = PackageMPQ.Config.default()

	def bucket(self) -> Bucket:
		return Bucket.make_artifacts

	def handle_source_item(self, source_item: Source.Item, mpq: MPQ) -> None:
		if isinstance(source_item, Source.Folder):
			self.handle_source_folder(source_item, mpq)
		elif isinstance(source_item, Source.File):
			self.handle_source_file(source_item, mpq)

	def handle_source_folder(self, source_folder: Source.Folder, mpq: MPQ) -> None:
		for source_item in source_folder.children:
			self.handle_source_item(source_item, mpq)

	def handle_source_file(self, source_file: Source.File, mpq: MPQ) -> None:
		intermediates_folder = self.compile_thread.project.source_path_to_intermediates_path(os.path.dirname(source_file.path))
		for file_name in source_file.output_files():
			file_path = os.path.join(intermediates_folder, file_name)
			if os.path.isfile(file_path):
				mpq_file_name = '\\'.join(os.path.normpath(os.path.relpath(file_path, self.mpq_intermediates_path)).split(os.path.sep))
				self.log(f'  Adding `{mpq_file_name}`...')
				compression_source = 'autocompression settings'
				compression = CompressionSetting.find(file_name, self.config.autocompression)
				self.log(f'    Checking `config.json` for `{source_file.display_name()}...')
				if file_config := self.load_config(PackageMPQ.FileConfig, source_file, optional=True, log=False):
					compression = CompressionSetting.parse_value(file_config.compression)
					compression_source = f'`config.json` for `{source_file.display_name()}`'
				self.log(f'    Using `{compression}` compression based on {compression_source}.')
				mpq.add_file(file_path, mpq_file_name, compression=compression.type.compression_type(), compression_level=compression.compression_level())

	def execute(self) -> list[BaseCompileStep] | None:
		if config := self.load_config(PackageMPQ.Config, self.source_folder):
			self.config = config

		self.log(f'Packaging `{self.source_folder.name}`...')
		artifact_path = self.compile_thread.project.source_path_to_artifacts_path(self.source_folder.path)
		if artifact_path.endswith(os.pathsep):
			artifact_path = artifact_path[:-1]
		mpq = MPQ.of(artifact_path)
		with mpq.create():
			self.handle_source_item(self.source_folder, mpq)
		self.log('  MPQ packaged!')
		return None
