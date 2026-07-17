
from __future__ import annotations

from .BaseCompileStep import BaseCompileStep, CompileError, Bucket
from .. import Source

from ...FileFormats.IScriptBIN import IScriptBIN, CodeHandlers

from ...Utilities import IO
from ...Utilities import Struct

import os as _os

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
		images_tbl: TBL | None = None
		sounds_tbl: TBL | None = None
		stat_txt_tbl: TBL | None = None
		images_dat: ImagesDAT | None = None
		sprites_dat: SpritesDAT | None = None
		flingy_dat: FlingyDAT | None = None
		sounds_dat: SoundsDAT | None = None
		weapons_dat: WeaponsDAT | None = None

		self.log('Attempting to load images.tbl for data context...')
		images_tbl_path = self.compile_thread.project.intermediates_relative_mpq_path(self.source_file.path, 'arr', 'images.tbl')
		if images_tbl_path and _os.path.isfile(images_tbl_path):
			try:
				tbl = TBL()
				tbl.load(images_tbl_path)
				images_tbl = tbl
				self.log('  images.tbl loaded!')
			except Exception:
				self.log("  Couldn't load images.tbl, continuing without it.", tag='warning')
		else:
			self.log('  images.tbl not found, continuing without it.')

		self.log('Attempting to load sfxdata.tbl for data context...')
		sounds_tbl_path = self.compile_thread.project.intermediates_relative_mpq_path(self.source_file.path, 'arr', 'sfxdata.tbl')
		if sounds_tbl_path and _os.path.isfile(sounds_tbl_path):
			try:
				tbl = TBL()
				tbl.load(sounds_tbl_path)
				sounds_tbl = tbl
				self.log('  sfxdata.tbl loaded!')
			except Exception:
				self.log("  Couldn't load sfxdata.tbl, continuing without it.", tag='warning')
		else:
			self.log('  sfxdata.tbl not found, continuing without it.')

		self.log('Attempting to load stat_txt.tbl for data context...')
		stat_txt_tbl_path = self.compile_thread.project.intermediates_relative_mpq_path(self.source_file.path, 'rez', 'stat_txt.tbl')
		if stat_txt_tbl_path and _os.path.isfile(stat_txt_tbl_path):
			try:
				tbl = TBL()
				tbl.load(stat_txt_tbl_path)
				stat_txt_tbl = tbl
				self.log('  stat_txt.tbl loaded!')
			except Exception:
				self.log("  Couldn't load stat_txt.tbl, continuing without it.", tag='warning')
		else:
			self.log('  stat_txt.tbl not found, continuing without it.')

		self.log('Attempting to load images.dat for data context...')
		images_dat_path = self.compile_thread.project.intermediates_relative_mpq_path(self.source_file.path, 'arr', 'images.dat')
		if images_dat_path and _os.path.isfile(images_dat_path):
			try:
				_images_dat = ImagesDAT()
				_images_dat.load(images_dat_path)
				images_dat = _images_dat
				self.log('  images.dat loaded!')
			except Exception:
				self.log("  Couldn't load images.dat, continuing without it.", tag='warning')
		else:
			self.log('  images.dat not found, continuing without it.')

		self.log('Attempting to load sprites.dat for data context...')
		sprites_dat_path = self.compile_thread.project.intermediates_relative_mpq_path(self.source_file.path, 'arr', 'sprites.dat')
		if sprites_dat_path and _os.path.isfile(sprites_dat_path):
			try:
				_sprites_dat = SpritesDAT()
				_sprites_dat.load(sprites_dat_path)
				sprites_dat = _sprites_dat
				self.log('  sprites.dat loaded!')
			except Exception:
				self.log("  Couldn't load sprites.dat, continuing without it.", tag='warning')
		else:
			self.log('  sprites.dat not found, continuing without it.')

		self.log('Attempting to load flingy.dat for data context...')
		flingy_dat_path = self.compile_thread.project.intermediates_relative_mpq_path(self.source_file.path, 'arr', 'flingy.dat')
		if flingy_dat_path and _os.path.isfile(flingy_dat_path):
			try:
				_flingy_dat = FlingyDAT()
				_flingy_dat.load(flingy_dat_path)
				flingy_dat = _flingy_dat
				self.log('  flingy.dat loaded!')
			except Exception:
				self.log("  Couldn't load flingy.dat, continuing without it.", tag='warning')
		else:
			self.log('  flingy.dat not found, continuing without it.')

		self.log('Attempting to load sfxdata.dat for data context...')
		sounds_dat_path = self.compile_thread.project.intermediates_relative_mpq_path(self.source_file.path, 'arr', 'sfxdata.dat')
		if sounds_dat_path and _os.path.isfile(sounds_dat_path):
			try:
				_sounds_dat = SoundsDAT()
				_sounds_dat.load(sounds_dat_path)
				sounds_dat = _sounds_dat
				self.log('  sfxdata.dat loaded!')
			except Exception:
				self.log("  Couldn't load sfxdata.dat, continuing without it.", tag='warning')
		else:
			self.log('  sfxdata.dat not found, continuing without it.')

		self.log('Attempting to load weapons.dat for data context...')
		weapons_dat_path = self.compile_thread.project.intermediates_relative_mpq_path(self.source_file.path, 'arr', 'weapons.dat')
		if weapons_dat_path and _os.path.isfile(weapons_dat_path):
			try:
				_weapons_dat = WeaponsDAT()
				_weapons_dat.load(weapons_dat_path)
				weapons_dat = _weapons_dat
				self.log('  weapons.dat loaded!')
			except Exception:
				self.log("  Couldn't load weapons.dat, continuing without it.", tag='warning')
		else:
			self.log('  weapons.dat not found, continuing without it.')

		return CodeHandlers.DataContext(images_tbl=images_tbl, images_dat=images_dat, sprites_dat=sprites_dat, flingy_dat=flingy_dat, sounds_tbl=sounds_tbl, sounds_dat=sounds_dat, stat_txt_tbl=stat_txt_tbl, weapons_dat=weapons_dat)

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
		self.compile_thread.meta.update_input_metas(inputs)
		self.compile_thread.meta.update_output_metas(output_paths)
		return None
