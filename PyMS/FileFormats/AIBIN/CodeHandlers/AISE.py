
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
long_jump_size = Struct.l_u8.size + Struct.l_u32.size

# Returns where the long jump table ends (the start of the code) if the file is expanded, otherwise None.
# Files with headers past 64KB are always expanded. Smaller files are also expanded if they start with a
# valid long jump table, so files in the expanded layout still load when under the expanded size. A small
# expanded file without long jumps can't be told apart from a standard file, which is why expanded files
# that fit under the expanded size are always saved in the standard layout.
def long_jump_table_end(data: bytes, headers_offset: int, script_addresses: Iterable[int]) -> int | None:
	code_addresses = [address for address in script_addresses if address]
	first_script = min(code_addresses, default=None)
	if headers_offset >= expanded_headers_offset:
		return headers_offset if first_script is None else first_script
	if first_script is None:
		return None
	table_size = first_script - 4
	if table_size <= 0 or table_size % long_jump_size or first_script >= headers_offset:
		return None
	for address in range(4, first_script, long_jump_size):
		if data[address] != CodeCommands.Goto.byte_code_id:
			return None
		target = Struct.l_u32.unpack(data, address + 1)
		if not first_script <= target < headers_offset:
			return None
	return first_script

class AISEContext:
	def __init__(self) -> None:
		self.expanded = False
		self.loaded_long_jumps: dict[int, int] = {}
		self.saving_long_jumps: dict[CodeBlock, int] = {}

	def expand(self, language_context: LanguageContext) -> None:
		self.expanded = True
		language_context.set_status(AISEPlugin.ID, PluginStatus.in_use, 'File has expanded size')

	def load_long_jumps(self, scanner: BytesScanner, context: AIDecompileContext, end: int) -> None:
		while scanner.address < end and not scanner.at_end():
			cmd_address = scanner.address
			cmd_id = scanner.scan(Struct.l_u8)
			cmd_def = context.language.lookup_command(cmd_id, context.language_context)
			if cmd_def != CodeCommands.Goto:
				break
			cmd = cmd_def.decompile(scanner, context)
			self.loaded_long_jumps[cmd_address] = cmd.params[0]

	def determine_long_jumps(self, scripts: Iterable[AIScript], context: AIByteCodeCompiler) -> None:
		self.expanded = True
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
