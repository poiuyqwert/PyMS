
from . import CodeCommands
from .AILexer import AILexer
from .AIParseContext import AIParseContext, ParsedScriptHeader

from ....Utilities.CodeHandlers.SourceCodeParser import CommandSourceCodeParser
from ....Utilities.CodeHandlers.ParseContext import ParseContext, BlockReferenceResolver
from ....Utilities.CodeHandlers import Tokens
from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ....Utilities.CodeHandlers.CodeBlock import CodeBlock

class AIHeaderEntryPointBlockReferenceResolver(BlockReferenceResolver):
	def __init__(self, header: ParsedScriptHeader, source_line: int | None) -> None:
		BlockReferenceResolver.__init__(self, source_line)
		self.header = header

	def block_defined(self, block):
		self.header.entry_point = block

class AIHeaderSourceCodeParser(CommandSourceCodeParser):
	def __init__(self) -> None:
		super().__init__()
		self.register_commands(CodeCommands.all_header_commands)

	def handles_token(self, token: Tokens.Token, parse_context: ParseContext) -> bool:
		return isinstance(token, Tokens.IdentifierToken) and token.raw_value == 'script'

	def parse(self, parse_context: ParseContext) -> bool:
		token = parse_context.lexer.skip(Tokens.NewlineToken)
		if not isinstance(token, Tokens.IdentifierToken) or not token.raw_value == 'script':
			return False
		assert isinstance(parse_context, AIParseContext)
		token = parse_context.lexer.check_token(AILexer.ScriptIDToken)
		if not isinstance(token, AILexer.ScriptIDToken):
			raise parse_context.error('Parse', "Expected script ID, got '%s' instead" % token.raw_value)
		line = parse_context.lexer.state.line
		script_id = token.raw_value
		if script_id in parse_context.script_headers:
			_,existing_line = parse_context.script_headers[script_id]
			raise parse_context.error('Parse', "A script with id '%s' is already defined on line %d" % (script_id, existing_line))

		string_id: int | None = None
		bwscript: bool | None = None
		broodwar_only: bool | None = None
		staredit_hidden: bool | None = None
		requires_location: bool | None = None
		entry_point: str | CodeBlock | None = None

		commands_parsed: list[CodeCommandDefinition] = []
		token = parse_context.lexer.next_token()
		if not isinstance(token, AILexer.SymbolToken) or token.raw_value != '{':
			raise parse_context.error('Parse', "Expected a '{' to start the script header, got '%s' instead" % token.raw_value)
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.NewlineToken):
			raise parse_context.error('Parse', "Unexpected token '%s' (expected end of line)" % token.raw_value)
		while True:
			token = parse_context.lexer.next_token()
			line = parse_context.lexer.state.line
			if isinstance(token, AILexer.SymbolToken) and token.raw_value == '}':
				break
			if not isinstance(token, Tokens.IdentifierToken):
				raise parse_context.error('Parse', "Expected a script header command, got '%s' instead" % token.raw_value)
			cmd_def = self.cmd_defs[token.raw_value]
			command = cmd_def.parse(parse_context)
			if command.definition in commands_parsed:
				raise parse_context.error('Parse', f"Duplicate script header command '{command.definition.name}'")
			commands_parsed.append(command.definition)
			if command.definition == CodeCommands.HeaderNameString:
				string_id = command.params[0]
			elif command.definition == CodeCommands.HeaderBinFile:
				bwscript = bool(command.params[0])
			elif command.definition == CodeCommands.BroodwarOnly:
				broodwar_only = command.params[0]
			elif command.definition == CodeCommands.StarEditHidden:
				staredit_hidden = command.params[0]
			elif command.definition == CodeCommands.RequiresLocation:
				requires_location = command.params[0]
			elif command.definition == CodeCommands.EntryPoint:
				entry_point = command.params[0]
		if string_id is None:
			raise parse_context.error('Parse', f"Script with ID '{script_id}' is missing '{CodeCommands.HeaderNameString.name}'", line=line)
		if bwscript is None:
			raise parse_context.error('Parse', f"Script with ID '{script_id}' is missing '{CodeCommands.HeaderBinFile.name}'", line=line)
		if broodwar_only is None:
			raise parse_context.error('Parse', f"Script with ID '{script_id}' is missing '{CodeCommands.BroodwarOnly.name}'", line=line)
		if staredit_hidden is None:
			raise parse_context.error('Parse', f"Script with ID '{script_id}' is missing '{CodeCommands.StarEditHidden.name}'", line=line)
		if requires_location is None:
			raise parse_context.error('Parse', f"Script with ID '{script_id}' is missing '{CodeCommands.RequiresLocation.name}'", line=line)
		if entry_point is None:
			raise parse_context.error('Parse', f"Script with ID '{script_id}' is missing '{CodeCommands.EntryPoint.name}'", line=line)
		
		script_header = ParsedScriptHeader(string_id, bwscript, broodwar_only, staredit_hidden, requires_location, entry_point if isinstance(entry_point, CodeBlock) else None)
		if isinstance(entry_point, str):
			parse_context.missing_block(entry_point, AIHeaderEntryPointBlockReferenceResolver(script_header, line))
		parse_context.script_headers[script_id] = (script_header, line)
		return True
