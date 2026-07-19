
from __future__ import annotations

from .BaseCompileStep import BaseCompileStep, CompileError, Bucket
from .. import Source

from ...FileFormats.IScriptBIN import IScriptBIN, CodeHandlers

from ...Utilities import IO
from ...Utilities import Struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class CompileIScript(BaseCompileStep):
	def __init__(self, compile_thread: 'CompileThread', source_file: Source.IScript) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.source_file = source_file

	def bucket(self) -> Bucket:
		return Bucket.use_intermediates

	def data_context(self) -> CodeHandlers.DataContext:
		from ...FileFormats.TBL import TBL
		from ...FileFormats.DAT import ImagesDAT, SpritesDAT, FlingyDAT, SoundsDAT, WeaponsDAT
		return CodeHandlers.DataContext(
			images_tbl = self.load_data_context_file(TBL, self.source_file, 'arr', 'images.tbl'),
			sounds_tbl = self.load_data_context_file(TBL, self.source_file, 'arr', 'sfxdata.tbl'),
			stat_txt_tbl = self.load_data_context_file(TBL, self.source_file, 'rez', 'stat_txt.tbl'),
			images_dat = self.load_data_context_file(ImagesDAT, self.source_file, 'arr', 'images.dat'),
			sprites_dat = self.load_data_context_file(SpritesDAT, self.source_file, 'arr', 'sprites.dat'),
			flingy_dat = self.load_data_context_file(FlingyDAT, self.source_file, 'arr', 'flingy.dat'),
			sounds_dat = self.load_data_context_file(SoundsDAT, self.source_file, 'arr', 'sfxdata.dat'),
			weapons_dat = self.load_data_context_file(WeaponsDAT, self.source_file, 'arr', 'weapons.dat'),
		)

	def load_base_iscript_bin(self) -> IScriptBIN.IScriptBIN:
		iscript_bin = IScriptBIN.IScriptBIN()
		base_iscript_path = self.source_file.base_iscript_path()
		if base_iscript_path:
			self.log(f'Loading base file `{base_iscript_path}`...')
			try:
				iscript_bin.load(base_iscript_path)
			except Exception as e:
				raise CompileError(f"Couldn't load base file `{base_iscript_path}`", internal_exception=e) from e
			self.log('  Base file loaded!')
		return iscript_bin

	def execute(self) -> list[BaseCompileStep] | None:
		self.log(f'Determining scripts for `{self.source_file.display_name()}`...')
		script_paths = self.source_file.script_paths()
		self.log(f'  {len(script_paths)} scripts found.', tag='warning' if not script_paths else None)
		if not script_paths:
			return None

		inputs = list(script_paths)
		if base_iscript_path := self.source_file.base_iscript_path():
			inputs.append(base_iscript_path)

		iscript_path = self.compile_thread.project.source_path_to_intermediates_path(self.source_file.path, 'iscript.bin')
		output_paths = [iscript_path]
		if not self.compile_thread.meta.check_requires_update(inputs, output_paths):
			self.log(f'No changes required for `{self.source_file.display_name()}`.')
			return None

		data_context = self.data_context()
		iscript_bin = self.load_base_iscript_bin()
		script_ids: set[int] = set()
		for script_path in script_paths:
			self.log(f'Parsing script `{script_path}`...')
			with IO.InputText(script_path) as f:
				code = f.read()
			lexer = CodeHandlers.ICELexer(code)
			parse_context = CodeHandlers.ICEParseContext(lexer, data_context)
			try:
				scripts = IScriptBIN.IScriptBIN.compile(parse_context)
			except Exception as e:
				raise CompileError(f"Couldn't parse script '{script_path}'", internal_exception=e) from e
			for script in scripts:
				if script.id in script_ids:
					self.log(f'  Script `{script.id}` already exists and will be overwritten...', tag='warning')
				script_ids.add(script.id)
			new_size = iscript_bin.can_add_scripts(scripts)
			if new_size is not None:
				size = iscript_bin.calculate_size()
				raise CompileError(f"There is not enough room in your iscript.bin to add `{script_path}`. The current file is {size}B out of the max {Struct.l_u16.max}B, these changes would make the file {new_size}B.")
			if parse_context.warnings:
				self.warnings(parse_context.warnings)
			iscript_bin.add_scripts(scripts)
			self.log('  Script parsed!')

		self.log('Compiling iscript.bin...')
		try:
			iscript_bin.save(iscript_path)
		except Exception as e:
			raise CompileError("Couldn't compile iscript.bin", internal_exception=e) from e

		self.log('  iscript.bin compiled!')
		self.compile_thread.meta.update_metas(inputs, output_paths)
		return None
