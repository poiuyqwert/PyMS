from . import CodeCommands
from .AIParseContext import AIParseContext

from ....Utilities.CodeHandlers.CodeStruct import StructSourceCodeParser, StructBlock
from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers.CodeBlock import CodeBlock

class AIHeaderSourceCodeParser(StructSourceCodeParser):
	def __init__(self) -> None:
		super().__init__(CodeCommands.ScriptHeader, AIHeaderSourceCodeParser.handle_header)

	@staticmethod
	def handle_header(parse_context: ParseContext, block: StructBlock) -> None:
		from ..AIScript import AIScript
		from ..AIFlag import AIFlag
		assert isinstance(parse_context, AIParseContext)
		script_id: str = block.header_params[0]
		script_line = block.line
		assert script_line is not None
		if script_id in parse_context.scripts:
			_,existing_line = parse_context.scripts[script_id]
			raise parse_context.error('Parse', f"A script with id '{script_id}' is already defined on line {existing_line + 1}", line=script_line)

		string_id: int = block.param(CodeCommands.HeaderNameString)
		in_bwscript = bool(block.param(CodeCommands.HeaderBinFile))
		broodwar_only: bool = block.param(CodeCommands.BroodwarOnly)
		staredit_hidden: bool = block.param(CodeCommands.StarEditHidden)
		requires_location: bool = block.param(CodeCommands.RequiresLocation)
		entry_point: CodeBlock = block.param(CodeCommands.EntryPoint)

		script = AIScript(script_id, AIFlag.flags(requires_location, staredit_hidden, broodwar_only), string_id, entry_point, in_bwscript)
		parse_context.add_block_owner(entry_point, script)
		parse_context.scripts[script_id] = (script, script_line)
