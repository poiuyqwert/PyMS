
from __future__ import annotations

from .BaseCompileStep import BaseCompileStep, CompileError, Bucket
from .. import Source

from ...Utilities import JSON

from dataclasses import dataclass
from enum import StrEnum

from typing import TYPE_CHECKING, Self
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class FramesMode(StrEnum):
	separate_bmps = 'separate_bmps'
	single_vertical = 'single_vertical'
	single_framesets = 'single_framesets'

class CompileGRP(BaseCompileStep):
	@dataclass
	class Config(JSON.Decodable):
		frames_mode: FramesMode
		frame_count: int | None
		uncompressed: bool

		@classmethod
		def from_json(cls, json: JSON.Object) -> Self:
			defaults = CompileGRP.Config.default()
			return cls(
				frames_mode = JSON.get_available(json, 'frames_mode', FramesMode, defaults.frames_mode),
				frame_count = JSON.get_available(json, 'frame_count', int, defaults.frame_count),
				uncompressed = JSON.get_available(json, 'uncompressed', bool, defaults.uncompressed)
			)

		@staticmethod
		def default() -> CompileGRP.Config:
			return CompileGRP.Config(
				frames_mode = FramesMode.separate_bmps,
				frame_count = None,
				uncompressed = False
			)

	def __init__(self, compile_thread: 'CompileThread', source_file: Source.GRP) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.source_file = source_file

	def bucket(self) -> Bucket:
		return Bucket.make_intermediates

	def execute(self) -> list[BaseCompileStep] | None:
		self.log(f'Determining GRP frames for `{self.source_file.display_name()}`...')
		frame_paths = self.source_file.frame_paths()
		if not frame_paths:
			raise CompileError(f'No frames found for `{self.source_file.display_name()}')
		self.log(f'  {len(frame_paths)} frames found.')
		inputs = list(frame_paths)

		self.log(f'Checking for `config.json` for `{self.source_file.display_name()}`...')
		config: CompileGRP.Config = CompileGRP.Config.default()
		try:
			loaded_config = self.load_config(CompileGRP.Config, self.source_file)
			if not loaded_config:
				self.log('  No `config.json` found, using default settings')
			else:
				config = loaded_config
				self.log('  Config loaded!')
				inputs.append(self.source_file.config_path())
		except Exception as e:
			raise CompileError("Couldn't load `config.json`", internal_exception=e)

		if config.frames_mode in (FramesMode.single_vertical, FramesMode.single_framesets) and len(frame_paths) > 1:
			raise CompileError(f'Too many frames for `{config.frames_mode.value}` frame mode')
		
		destination_path = self.compile_thread.project.source_path_to_intermediates_path(self.source_file.path, self.source_file.name)
		if not self.compile_thread.meta.check_requires_update(inputs, [destination_path]):
			self.log(f'No changes required for `{self.source_file.display_name()}`.')
			return None

		self.log(f'Compiling `{self.source_file.display_name()}`...')
		from ...FileFormats.BMP import BMP
		from ...FileFormats.GRP import GRP
		grp = GRP()
		bmp = BMP()
		if config.frames_mode == FramesMode.separate_bmps:
			size = None
			for frame_path in sorted(frame_paths):
				try:
					bmp.load_file(frame_path, issize=size)
				except Exception as e:
					raise CompileError(f"Couldn't load '{frame_path}'", internal_exception=e)
				if size == None:
					size = (bmp.width, bmp.height)
				grp.add_frame(bmp.image)
		else:
			if not config.frame_count:
				raise CompileError(f'Frame mode `{config.frames_mode}` requires `frame_count` to be set in `config.json`')
			frame_path = frame_paths[0]
			try:
				bmp.load_file(frame_path)
			except Exception as e:
				raise CompileError(f"Couldn't load '{frame_path}'", internal_exception=e)
			grp.add_frames(bmp.image, config.frame_count, config.frames_mode == FramesMode.single_vertical)
		try:
			grp.save_file(destination_path, uncompressed=config.uncompressed)
		except Exception as e:
			raise CompileError("Couldn't save GRP", internal_exception=e)
		self.log('  GRP compiled!')		

		self.compile_thread.meta.update_input_metas(inputs)
		self.compile_thread.meta.update_output_metas([destination_path])
		return None
