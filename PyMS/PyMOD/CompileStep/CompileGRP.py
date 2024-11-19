
from .BaseCompileStep import BaseCompileStep, CompileError, Bucket
from .. import Source

import os as _os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class CompileGRP(BaseCompileStep):
	def __init__(self, compile_thread: 'CompileThread', source_file: Source.GRP) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.source_file = source_file

	def bucket(self) -> Bucket:
		return Bucket.make_intermediates

	def _determine_frame_paths(self) -> list[str]:
		frame_paths: list[str] = []
		for filename in _os.listdir(self.source_file.path):
			if filename.endswith('.bmp'):
				frame_paths.append(_os.path.join(self.source_file.path, filename))
		return sorted(frame_paths)

	def execute(self) -> list[BaseCompileStep] | None:
		self.log(f'Determining GRP frames for `{self.source_file.display_name()}`...')
		frame_paths = self._determine_frame_paths()
		self.log(f'  {len(frame_paths)} frames found.', tag='warning' if not frame_paths else None)
		if not frame_paths:
			return None
		destination_path = _os.path.join(_os.path.dirname(self.compile_thread.source_path_to_intermediates_path(self.source_file.path)), self.source_file.compiled_name())
		if not self.compile_thread.meta.check_requires_update(frame_paths, [destination_path]):
			self.log(f'No changes required for `{self.source_file.display_name()}`.')
			return None
		self.log(f'Compiling `{self.source_file.display_name()}`...')
		from ...FileFormats.BMP import BMP
		from ...FileFormats.GRP import GRP
		grp = GRP()
		bmp = BMP()
		size = None
		# TODO: Support "GRPSourecFile.Mode"'s
		for frame_path in sorted(frame_paths):
			try:
				bmp.load_file(frame_path, issize=size)
			except Exception as e:
				raise CompileError(f"Couldn't load '{frame_path}'", internal_exception=e)
			if size == None:
				size = (bmp.width, bmp.height)
			grp.add_frame(bmp.image)
		try:
			grp.save_file(destination_path)
		except Exception as e:
			raise CompileError("Couldn't save GRP", internal_exception=e)
		self.log('  GRP compiled!')
		self.compile_thread.meta.update_input_metas(frame_paths)
		self.compile_thread.meta.update_output_metas([destination_path])
		return None
