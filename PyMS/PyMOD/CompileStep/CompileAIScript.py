
from __future__ import annotations

from .BaseCompileStep import BaseCompileStep, CompileError, Bucket
from .. import Source

from ...FileFormats.AIBIN import AIBIN, CodeHandlers

from ...Utilities import IO
from ...Utilities import JSON
from ...Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler

import os as _os

from dataclasses import dataclass

from typing import TYPE_CHECKING, Self, assert_never
if TYPE_CHECKING:
	from ..CompileThread import CompileThread

class CompileAIScript(BaseCompileStep):
	@dataclass
	class Config(JSON.Decodable):
		expanded: bool

		@classmethod
		def from_json(cls, json: JSON.Object) -> Self:
			defaults = CompileAIScript.Config.default()
			return cls(
				expanded = JSON.get_available(json, 'expanded', bool, defaults.expanded)
			)

		@staticmethod
		def default() -> CompileAIScript.Config:
			return CompileAIScript.Config(
				expanded = False
			)

	def __init__(self, compile_thread: 'CompileThread', source_file: Source.AIScript) -> None:
		BaseCompileStep.__init__(self, compile_thread)
		self.source_file = source_file

	def bucket(self) -> Bucket:
		return Bucket.use_intermediates

	def data_context(self) -> CodeHandlers.DataContext:
		from ...FileFormats.TBL import TBL
		from ...FileFormats.DAT import UnitsDAT, UpgradesDAT, TechDAT
		return CodeHandlers.DataContext(
			stattxt_tbl = self.load_data_context_file(TBL, self.source_file, 'rez', 'stat_txt.tbl'),
			unitnames_tbl = self.load_data_context_file(TBL, self.source_file, 'rez', 'unitnames.tbl'),
			units_dat = self.load_data_context_file(UnitsDAT, self.source_file, 'arr', 'units.dat'),
			upgrades_dat = self.load_data_context_file(UpgradesDAT, self.source_file, 'arr', 'upgrades.dat'),
			techdata_dat = self.load_data_context_file(TechDAT, self.source_file, 'arr', 'techdata.dat'),
		)

	def load_base_aibin(self, config: CompileAIScript.Config) -> AIBIN.AIBIN:
		aibin = AIBIN.AIBIN()
		base_aiscript_path = self.source_file.base_aiscript_path()
		base_bwscript_path = self.source_file.base_bwscript_path()
		if base_aiscript_path:
			filenames = f'`{base_aiscript_path}`'
			if base_bwscript_path:
				filenames += f' and `{base_bwscript_path}`'
			self.log(f'Loading base file(s) {filenames}...')
			try:
				issues = aibin.load(base_aiscript_path, base_bwscript_path)
			except Exception as e:
				raise CompileError(f"Couldn't load base file(s) {filenames}", internal_exception=e) from e
			self.log('  Base file(s) loaded!')
			for issue in issues:
				match issue.reason:
					case AIBIN.LoadIssueReason.unreferenced_bw:
						reason = 'exists in the base bwscript.bin but is not referenced by the base aiscript.bin'
					case AIBIN.LoadIssueReason.duplicate_bw:
						reason = 'is in the base aiscript.bin but also exists in the base bwscript.bin'
					case _:
						assert_never(issue.reason)
				self.log(f'  Script `{issue.script_id}` {reason}, it will not be included.', tag='warning')
		elif base_bwscript_path:
			raise CompileError(f"A base `{base_bwscript_path}` was found but there is no base aiscript.bin beside it (bwscript.bin can't be used without the aiscript.bin that references its scripts)")
		if config.expanded and not aibin.expanded:
			self.log('Expanding aiscript.bin/bwscript.bin...')
			aibin.expand()
			self.log('  Expanded!')
		if aibin.expanded:
			self.log('`aiscript.bin/bwscript.bin` is expanded, a plugin will be required for the game to use it.', tag='warning')
		return aibin

	def execute(self) -> list[BaseCompileStep] | None:
		self.log(f'Determining scripts for `{self.source_file.display_name()}`...')
		script_paths = self.source_file.script_paths()
		self.log(f'  {len(script_paths)} scripts found.', tag='warning' if not script_paths else None)
		if not script_paths:
			return None

		self.log(f'Determining extdefs for `{self.source_file.display_name()}`...')
		extdef_paths = self.source_file.extdef_paths()
		self.log(f'  {len(extdef_paths)} extdefs found.')

		config: CompileAIScript.Config = CompileAIScript.Config.default()
		if loaded_config := self.load_config(CompileAIScript.Config, self.source_file):
			config = loaded_config

		inputs = script_paths + extdef_paths
		if base_aiscript_path := self.source_file.base_aiscript_path():
			inputs.append(base_aiscript_path)
		if base_bwscript_path := self.source_file.base_bwscript_path():
			inputs.append(base_bwscript_path)
		config_path = self.source_file.config_path()
		if _os.path.isfile(config_path):
			inputs.append(config_path)

		aiscript_path = self.compile_thread.project.source_path_to_intermediates_path(self.source_file.path, 'aiscript.bin')
		bwscript_path = self.compile_thread.project.source_path_to_intermediates_path(self.source_file.path, 'bwscript.bin')
		# `bwscript.bin` is only an output when the scripts require it, so only include it in the
		# incremental check when the previous compile produced it
		output_paths = [aiscript_path]
		if self.compile_thread.meta.has_output(bwscript_path):
			output_paths.append(bwscript_path)
		if not self.compile_thread.meta.check_requires_update(inputs, output_paths):
			self.log(f'No changes required for `{self.source_file.display_name()}`.')
			return None
		data_context = self.data_context()
		parse_settings = CodeHandlers.AIParseSettings()
		definitions_handler = DefinitionsHandler()

		if extdef_paths:
			defs_source_handler = CodeHandlers.AIDefsSourceCodeHandler()
			for extdef_path in extdef_paths:
				self.log(f'Loading extdef `{extdef_path}`...')
				with IO.InputText(extdef_path) as f:
					code = f.read()
				lexer = CodeHandlers.AILexer(code)
				parse_context = CodeHandlers.AIParseContext(lexer, parse_settings, definitions_handler, data_context)
				try:
					defs_source_handler.parse(parse_context)
					parse_context.finalize()
				except Exception as e:
					raise CompileError(f"Couldn't load extdef '{extdef_path}'", internal_exception=e) from e
				if parse_context.warnings:
					self.warnings(parse_context.warnings)
			self.log('  Extdef loaded!')

		aibin = self.load_base_aibin(config)
		script_ids: set[str] = set()
		for script_path in script_paths:
			self.log(f'Parsing script `{script_path}`...')
			with IO.InputText(script_path) as f:
				code = f.read()
			lexer = CodeHandlers.AILexer(code)
			parse_context = CodeHandlers.AIParseContext(lexer, parse_settings, definitions_handler, data_context)
			try:
				scripts = AIBIN.AIBIN.compile(parse_context)
			except Exception as e:
				raise CompileError(f"Couldn't parse script '{script_path}'", internal_exception=e) from e
			for script in scripts:
				if script.id in script_ids:
					self.log(f'  Script `{script.id}` already exists and will be overwritten...', tag='warning')
				script_ids.add(script.id)
			new_ai_size, new_bw_size = aibin.can_add_scripts(scripts)
			if new_ai_size is not None:
				ai_size, _ = aibin.calculate_sizes()
				raise CompileError(f"There is not enough room in your aiscript.bin to add `{script_path}`. The current file is {ai_size}B out of the max {aibin.max_size()}B, these changes would make the file {new_ai_size}B.")
			if new_bw_size is not None:
				_, bw_size = aibin.calculate_sizes()
				raise CompileError(f"There is not enough room in your bwscript.bin to add `{script_path}`. The current file is {bw_size}B out of the max {aibin.max_size()}B, these changes would make the file {new_bw_size}B.")
			if parse_context.warnings:
				self.warnings(parse_context.warnings)
			aibin.add_scripts(scripts)
			self.log('  Script parsed!')

		# Only write `bwscript.bin` when the scripts require it — a stub `bwscript.bin` packaged
		# into the MPQ would shadow the game's real one and wipe out all vanilla Brood War AI
		has_bwscripts = aibin.has_bwscripts()
		filenames = 'aiscript.bin'
		if has_bwscripts:
			filenames += ' and bwscript.bin'
		self.log(f'Compiling {filenames}...')
		try:
			aibin.save(aiscript_path, bwscript_path if has_bwscripts else None)
		except Exception as e:
			raise CompileError(f"Couldn't compile {filenames}", internal_exception=e) from e

		self.log(f'  {filenames} compiled!')
		output_paths = [aiscript_path]
		if has_bwscripts:
			output_paths.append(bwscript_path)
		self.compile_thread.meta.update_metas(inputs, output_paths)
		return None
