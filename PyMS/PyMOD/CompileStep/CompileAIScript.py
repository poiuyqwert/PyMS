
from .BaseCompileStep import BaseCompileStep, CompileError, Bucket
from .. import Source

from ...FileFormats.AIBIN import AIBIN, CodeHandlers

from ...Utilities import IO

import os as _os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class CompileAIScript(BaseCompileStep):
	def __init__(self, compile_thread: 'CompileThread', source_file: Source.AIScript) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.source_file = source_file

	def bucket(self) -> Bucket:
		return Bucket.use_intermediates

	def data_context(self) -> CodeHandlers.DataContext:
		from ...FileFormats.TBL import TBL
		from ...FileFormats.DAT import UnitsDAT, UpgradesDAT, TechDAT
		stattxt_tbl: TBL | None = None
		unitnames_tbl: TBL | None = None
		units_dat: UnitsDAT | None = None
		upgrades_dat: UpgradesDAT | None = None
		techdata_dat: TechDAT | None = None

		self.log('Attempting to load stat_txt.tbl for data context...')
		stattxt_tbl_path = self.compile_thread.project.intermediates_relative_mpq_path(self.source_file.path, 'rez', 'stat_txt.tbl')
		if stattxt_tbl_path and _os.path.isfile(stattxt_tbl_path):
			try:
				tbl = TBL()
				tbl.load_file(stattxt_tbl_path)
				stattxt_tbl = tbl
				self.log('  stat_txt.tbl loadad!')
			except:
				self.log("  Couldn't load stat_txt.tbl, continuing without it.", tag='warning')
		else:
			self.log('  stat_txt.tbl not found, continuing without it.')

		self.log('Attempting to load unitnames.tbl for data context...')
		unitnames_tbl_path = self.compile_thread.project.intermediates_relative_mpq_path(self.source_file.path, 'rez', 'unitnames.tbl')
		if unitnames_tbl_path and _os.path.isfile(unitnames_tbl_path):
			try:
				tbl = TBL()
				tbl.load_file(unitnames_tbl_path)
				unitnames_tbl = tbl
				self.log('  unitnames.tbl loadad!')
			except:
				self.log("  Couldn't load unitnames.tbl, continuing without it.", tag='warning')
		else:
			self.log('  unitnames.tbl not found, continuing without it.')

		self.log('Attempting to load units.dat for data context...')
		units_dat_path = self.compile_thread.project.intermediates_relative_mpq_path(self.source_file.path, 'arr', 'units.dat')
		if units_dat_path and _os.path.isfile(units_dat_path):
			try:
				_units_dat = UnitsDAT()
				_units_dat.load_file(units_dat_path)
				units_dat = _units_dat
				self.log('  units.dat loadad!')
			except:
				self.log("  Couldn't load units.dat, continuing without it.", tag='warning')
		else:
			self.log('  units.dat not found, continuing without it.')

		self.log('Attempting to load upgrades.dat for data context...')
		upgrades_dat_path = self.compile_thread.project.intermediates_relative_mpq_path(self.source_file.path, 'arr', 'upgrades.dat')
		if upgrades_dat_path and _os.path.isfile(upgrades_dat_path):
			try:
				_upgrades_dat = UpgradesDAT()
				_upgrades_dat.load_file(upgrades_dat_path)
				upgrades_dat = _upgrades_dat
				self.log('  upgrades.dat loadad!')
			except:
				self.log("  Couldn't load upgrades.dat, continuing without it.", tag='warning')
		else:
			self.log('  upgrades.dat not found, continuing without it.')

		self.log('Attempting to load techdata.dat for data context...')
		techdata_dat_path = self.compile_thread.project.intermediates_relative_mpq_path(self.source_file.path, 'arr', 'techdata.dat')
		if techdata_dat_path and _os.path.isfile(techdata_dat_path):
			try:
				_techdata_dat = TechDAT()
				_techdata_dat.load_file(techdata_dat_path)
				techdata_dat = _techdata_dat
				self.log('  techdata.dat loadad!')
			except:
				self.log("  Couldn't load techdata.dat, continuing without it.", tag='warning')
		else:
			self.log('  techdata.dat not found, continuing without it.')

		return CodeHandlers.DataContext(stattxt_tbl, unitnames_tbl, units_dat, upgrades_dat, techdata_dat)

	def execute(self) -> list[BaseCompileStep] | None:
		self.log(f'Determining scripts for `{self.source_file.display_name()}`...')
		script_paths = self.source_file.script_paths()
		self.log(f'  {len(script_paths)} scripts found.', tag='warning' if not script_paths else None)
		if not script_paths:
			return None
		
		self.log(f'Determining extdefs for `{self.source_file.display_name()}`...')
		extdef_paths = self.source_file.extdef_paths()
		self.log(f'  {len(extdef_paths)} extdefs found.')
		
		aiscript_path = self.compile_thread.project.source_path_to_intermediates_path(self.source_file.path, 'aiscript.bin')
		bwscript_path = self.compile_thread.project.source_path_to_intermediates_path(self.source_file.path, 'bwscript.bin')
		# TODO: What if bwscript.bin is not needed?
		if not self.compile_thread.meta.check_requires_update(script_paths + extdef_paths, [aiscript_path, bwscript_path]):
			self.log(f'No changes required for `{self.source_file.display_name()}`.')
			return None
		# TODO: Base files to build on top of?
		data_context = self.data_context()
		definitions_handler = CodeHandlers.AIDefinitionsHandler()

		if extdef_paths:
			defs_source_handler = CodeHandlers.AIDefsSourceCodeHandler()
			for extdef_path in extdef_paths:
				self.log(f'Loading extdef `{extdef_path}`...')
				with IO.InputText(extdef_path) as f:
					code = f.read()
				lexer = CodeHandlers.AILexer(code)
				parse_context = CodeHandlers.AIParseContext(lexer, definitions_handler, data_context)
				try:
					defs_source_handler.parse(parse_context)
					parse_context.finalize()
				except Exception as e:
					raise CompileError(f"Couldn't load extdef '{extdef_path}'", internal_exception=e)
				if parse_context.warnings:
					self.warnings(parse_context.warnings)
			self.log('  Extdef loaded!')

		aibin = AIBIN.AIBIN()
		script_ids: set[str] = set()
		for script_path in script_paths:
			self.log(f'Parsing script `{script_path}`...')
			with IO.InputText(script_path) as f:
				code = f.read()
			lexer = CodeHandlers.AILexer(code)
			parse_context = CodeHandlers.AIParseContext(lexer, definitions_handler, data_context)
			try:
				scripts = AIBIN.AIBIN.compile(parse_context)
			except Exception as e:
				raise CompileError(f"Couldn't parse script '{script_path}'", internal_exception=e)
			for script in scripts:
				if script.id in script_ids:
					self.log(f'  Script `{script.id}` already exists and will be overwritten...', tag='warning')
				script_ids.add(script.id)
			new_ai_size, new_bw_size = aibin.can_add_scripts(scripts)
			if new_ai_size is not None:
				ai_size, _ = aibin.calculate_sizes()
				raise CompileError(f"There is not enough room in your aiscript.bin to add `{script_path}`. The current file is {ai_size}B out of the max 65535B, these changes would make the file {new_ai_size}B.")
			if new_bw_size is not None:
				_, bw_size = aibin.calculate_sizes()
				raise CompileError(f"There is not enough room in your bwscript.bin to add `{script_path}`. The current file is {bw_size}B out of the max 65535B, these changes would make the file {new_bw_size}B.")
			if parse_context.warnings:
				self.warnings(parse_context.warnings)
			aibin.add_scripts(scripts)
			self.log('  Script parsed!')

		filenames = 'aiscript.bin'
		if aibin.has_bwscripts():
			filenames += ' and bwscript.bin'
		self.log(f'Compiling {filenames}...')
		try:
			aibin.save(aiscript_path, bwscript_path)
		except Exception as e:
			raise CompileError(f"Couldn't compile {filenames}", internal_exception=e)
		
		self.log(f'  {filenames} compiled!')
		self.compile_thread.meta.update_input_metas(script_paths + extdef_paths)
		self.compile_thread.meta.update_output_metas([aiscript_path, bwscript_path])
		return None
