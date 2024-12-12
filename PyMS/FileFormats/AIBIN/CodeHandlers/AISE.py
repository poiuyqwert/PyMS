
from .AILanguage import AISEPlugin
from .AIDecompileContext import AIDecompileContext
from . import CodeCommands

from ....Utilities.CodeHandlers.LanguageDefinition import LanguageContext, PluginStatus
from ....Utilities.BytesScanner import BytesScanner
from ....Utilities import Struct

expanded_headers_offset = 0x10000

class AISEContext:
	def __init__(self) -> None:
		self.expanded = False
		self.long_jumps: dict[int, int] = {}

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
			self.long_jumps[cmd_address] = cmd.params[0]
