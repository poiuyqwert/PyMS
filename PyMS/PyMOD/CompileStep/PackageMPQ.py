
from __future__ import annotations

from .BaseCompileStep import BaseCompileStep, CompileError, Bucket
from .. import Source

from ...FileFormats.MPQ.MPQ import MPQ
from ...PyMPQ.CompressionSetting import CompressionOption, CompressionSetting
from ...Utilities import JSON
from ...Utilities.PyMSError import PyMSError

import os
from dataclasses import dataclass

from typing import TYPE_CHECKING, Self
if TYPE_CHECKING:
	from ..CompileThread import CompileThread
	from ..Project import Project

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

	# An embedded (nested) MPQ is packaged into a hidden file in the intermediates (dot-names can
	# never collide with source-derived intermediates, since dot-files are never sources), which the
	# containing MPQ's own package step then embeds as a file
	def __init__(self, compile_thread: 'CompileThread', source_folder: Source.MPQ, embedded: bool = False) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.source_folder = source_folder
		self.embedded = embedded
		self.mpq_intermediates_path = self.compile_thread.project.source_path_to_intermediates_path(self.source_folder.path)
		self.config = PackageMPQ.Config.default()

	def bucket(self) -> Bucket:
		return Bucket.make_artifacts

	def archive_path(self) -> str:
		if self.embedded:
			return PackageMPQ.embedded_archive_path(self.compile_thread.project, self.source_folder)
		return self.compile_thread.project.source_path_to_artifacts_path(self.source_folder.path).rstrip(os.sep)

	@staticmethod
	def embedded_archive_path(project: 'Project', source_mpq: Source.MPQ) -> str:
		return project.source_path_to_intermediates_path(source_mpq.path, '.' + source_mpq.name)

	def handle_source_item(self, source_item: Source.Item, mpq: MPQ) -> None:
		if isinstance(source_item, Source.MPQ):
			self.handle_nested_mpq(source_item, mpq)
		elif isinstance(source_item, Source.Folder):
			self.handle_source_folder(source_item, mpq)
		elif isinstance(source_item, Source.File):
			self.handle_source_file(source_item, mpq)

	def handle_source_folder(self, source_folder: Source.Folder, mpq: MPQ) -> None:
		for source_item in source_folder.children:
			self.handle_source_item(source_item, mpq)

	def handle_nested_mpq(self, source_mpq: Source.MPQ, mpq: MPQ) -> None:
		archive_path = PackageMPQ.embedded_archive_path(self.compile_thread.project, source_mpq)
		if not os.path.isfile(archive_path):
			raise CompileError(f'The packaged archive for nested MPQ `{source_mpq.display_name()}` is missing (expected at `{archive_path}`)')
		mpq_file_name = self.mpq_file_name(self.compile_thread.project.source_path_to_intermediates_path(source_mpq.path))
		self.add_file(mpq, file_path=archive_path, mpq_file_name=mpq_file_name, file_name=source_mpq.name, source_item=source_mpq)

	def handle_source_file(self, source_file: Source.File, mpq: MPQ) -> None:
		intermediates_folder = self.compile_thread.project.source_path_to_intermediates_path(os.path.dirname(source_file.path))
		for file_name in source_file.output_files():
			file_path = os.path.join(intermediates_folder, file_name)
			if os.path.isfile(file_path):
				self.add_file(mpq, file_path=file_path, mpq_file_name=self.mpq_file_name(file_path), file_name=file_name, source_item=source_file)

	def mpq_file_name(self, intermediates_path: str) -> str:
		return '\\'.join(os.path.normpath(os.path.relpath(intermediates_path, self.mpq_intermediates_path)).split(os.path.sep))

	def add_file(self, mpq: MPQ, *, file_path: str, mpq_file_name: str, file_name: str, source_item: Source.Item) -> None:
		self.log(f'  Adding `{mpq_file_name}`...')
		compression_source = 'autocompression settings'
		compression = CompressionSetting.find(file_name, self.config.autocompression)
		self.log(f'    Checking `config.json` for `{source_item.display_name()}`...')
		if file_config := self.load_config(PackageMPQ.FileConfig, source_item, optional=True, log=False):
			compression = CompressionSetting.parse_value(file_config.compression)
			compression_source = f'`config.json` for `{source_item.display_name()}`'
		self.log(f'    Using `{compression}` compression based on {compression_source}.')
		mpq.add_file(file_path, mpq_file_name, compression=compression.type.compression_type(), compression_level=compression.compression_level())

	def execute(self) -> list[BaseCompileStep] | None:
		if config := self.load_config(PackageMPQ.Config, self.source_folder):
			self.config = config

		self.log(f'Packaging `{self.source_folder.name}`...')
		archive_path = self.archive_path()
		try:
			os.makedirs(os.path.dirname(archive_path), exist_ok=True)
		except Exception as e:
			raise CompileError(f"Couldn't create archive directory for `{self.source_folder.name}`", internal_exception=e) from e
		try:
			mpq = MPQ.of(archive_path)
			with mpq.create(max_files=self.config.max_files, sector_size_shift=self.config.block_size):
				self.handle_source_folder(self.source_folder, mpq)
		except PyMSError as e:
			raise CompileError(str(e), internal_exception=e) from e
		self.log('  MPQ packaged!')
		return None
