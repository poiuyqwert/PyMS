
from .AILanguage import AISEPlugin
from .AIDecompileContext import AIDecompileContext
from . import CodeCommands
from ..AIScript import AIScript
from .AIByteCodeCompiler import AIByteCodeCompiler
from . import AISECodeTypes

from ....Utilities.CodeHandlers.LanguageDefinition import LanguageContext, PluginStatus
from ....Utilities.CodeHandlers.CodeBlock import CodeBlock
from ....Utilities.BytesScanner import BytesScanner
from ....Utilities import Struct

from typing import Iterable

expanded_headers_offset = 0x10000

class AISEContext:
	def __init__(self) -> None:
		self.expanded = False
		self.loaded_long_jumps: dict[int, int] = {}
		self.saving_long_jumps: dict[CodeBlock, int] = {}

	def expand(self, language_context: LanguageContext) -> None:
		self.expanded = True
		language_context.set_status(AISEPlugin.ID, PluginStatus.in_use, 'File has expanded size')

	def load_long_jumps(self, scanner: BytesScanner, context: AIDecompileContext) -> None:
		while not scanner.at_end():
			cmd_address = scanner.address
			cmd_id = scanner.scan(Struct.l_u8)
			cmd_def = context.language.lookup_command(cmd_id, context.language_context)
			if cmd_def != CodeCommands.Goto:
				break
			cmd = cmd_def.decompile(scanner, context)
			self.loaded_long_jumps[cmd_address] = cmd.params[0]

	def determine_long_jumps(self, scripts: Iterable[AIScript], context: AIByteCodeCompiler) -> None:
		checked_blocks: set[CodeBlock] = set()
		def check_block(block: CodeBlock) -> None:
			if block in checked_blocks:
				return
			assert CodeCommands.Goto.byte_code_id is not None
			checked_blocks.add(block)
			for cmd in block.commands:
				for param, param_type in cmd.iter_params():
					if isinstance(param, CodeBlock):
						if not isinstance(param_type, AISECodeTypes.LongBlockCodeType) and not param in self.saving_long_jumps:
							self.saving_long_jumps[param] = context.current_offset
							# TODO: Is there a better way to add the goto command other than manually?
							context.add_data(Struct.l_u8.pack(CodeCommands.Goto.byte_code_id))
							context.add_block_ref(param, Struct.l_u32)
						check_block(param)
			if block.prev_block is not None:
				check_block(block.prev_block)
			if block.next_block is not None:
				check_block(block.next_block)

		for script in scripts:
			check_block(script.entry_point)
