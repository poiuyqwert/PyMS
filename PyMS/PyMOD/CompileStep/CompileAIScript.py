
from .BaseCompileStep import BaseCompileStep, CompileError, Bucket
from .. import Source

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
		return Bucket.make_intermediates

	def _determine_script_paths(self) -> list[str]:
		script_paths: list[str] = []
		for filename in _os.listdir(self.source_file.path):
			if filename.endswith('.txt') and not filename.endswith('def.txt'):
				script_paths.append(_os.path.join(self.source_file.path, filename))
		return sorted(script_paths)

	def _determine_extdef_paths(self) -> list[str]:
		extdef_paths: list[str] = []
		for filename in _os.listdir(self.source_file.path):
			if filename.endswith('def.txt'):
				extdef_paths.append(_os.path.join(self.source_file.path, filename))
		return sorted(extdef_paths)

	def execute(self) -> list[BaseCompileStep] | None:
		self.log(f'Determining scripts for `{self.source_file.display_name()}`...')
		script_paths = self._determine_script_paths()
		self.log(f'  {len(script_paths)} scripts found.', tag='warning' if not script_paths else None)
		if not script_paths:
			return None
		
		self.log(f'Determining extdefs for `{self.source_file.display_name()}`...')
		extdef_paths = self._determine_extdef_paths()
		self.log(f'  {len(extdef_paths)} extdefs found.')
		
		aiscript_path = _os.path.join(_os.path.dirname(self.compile_thread.source_path_to_intermediates_path(self.source_file.path)), 'aiscript.bin')
		bwscript_path = _os.path.join(_os.path.dirname(self.compile_thread.source_path_to_intermediates_path(self.source_file.path)), 'bwscript.bin')
		# TODO: What if bwscript.bin is not needed?
		if not self.compile_thread.meta.check_requires_update(script_paths + extdef_paths, [aiscript_path, bwscript_path]):
			self.log(f'No changes required for `{self.source_file.display_name()}`.')
			return None
		# TODO: Base files to build on top of?
		self.log(f'Compiling `{self.source_file.display_name()}`...')
		from ...FileFormats.AIBIN import AIBIN, CodeHandlers
		data_context = CodeHandlers.DataContext()
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
					# TODO: Warnings?
				except Exception as e:
					raise CompileError(f"Couldn't load extdef '{extdef_path}'", internal_exception=e)
			self.log('  Extdef loaded!')

		aibin = AIBIN.AIBIN()
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
			# TODO: Check for duplicate scripts?
			new_ai_size, new_bw_size = aibin.can_add_scripts(scripts)
			if new_ai_size is not None:
				ai_size, _ = aibin.calculate_sizes()
				raise CompileError(f"There is not enough room in your aiscript.bin to compile these changes. The current file is {ai_size}B out of the max 65535B, these changes would make the file {new_ai_size}B.")
			if new_bw_size is not None:
				_, bw_size = aibin.calculate_sizes()
				raise CompileError(f"There is not enough room in your bwscript.bin to compile these changes. The current file is {bw_size}B out of the max 65535B, these changes would make the file {new_bw_size}B.")
			# TODO: Warnings
			# if parse_context.warnings:
			# 	WarningDialog(parent, parse_context.warnings, True)
			aibin.add_scripts(scripts)
			self.log('  Script parsed!')

		self.log('Compiling aiscript.bin and bwscript.bin...')
		try:
			aibin.save(aiscript_path, bwscript_path)
		except Exception as e:
			raise CompileError("Couldn't compile aiscript.bin and bwscript.bin", internal_exception=e)
		
		self.log('  aiscript.bin and bwscript.bin compiled!')
		self.compile_thread.meta.update_input_metas(script_paths)
		self.compile_thread.meta.update_output_metas([aiscript_path, bwscript_path])
		return None
