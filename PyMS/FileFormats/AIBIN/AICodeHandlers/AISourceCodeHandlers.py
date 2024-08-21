
from . import CodeCommands
from . import CodeDirectives
from .AILexer import AILexer
from .AIParseContext import AIParseContext, ParsedScriptHeader
from .AIDefinitionsHandler import AIDefinitionsSourceCodeParser

from ....Utilities.CodeHandlers.SourceCodeHandler import SourceCodeHandler, BasicSourceCodeParser
from ....Utilities.CodeHandlers.ParseContext import ParseContext, BlockReferenceResolver
from ....Utilities.CodeHandlers import Tokens
from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ....Utilities.CodeHandlers.DefinitionsHandler import DefinitionsSourceCodeParser

class AISourceCodeParser(BasicSourceCodeParser):
	def __init__(self) -> None:
		BasicSourceCodeParser.__init__(self)
		self.register_commands(CodeCommands.all_basic_commands)
		self.register_directives(CodeDirectives.all_basic_directives)

class AIHeaderEntryPointBlockReferenceResolver(BlockReferenceResolver):
	def __init__(self, header: ParsedScriptHeader, source_line: int | None) -> None:
		BlockReferenceResolver.__init__(self, source_line)
		self.header = header

	def block_defined(self, block):
		self.header.entry_point = block

class AIHeaderSourceCodeParser(BasicSourceCodeParser):
	def __init__(self) -> None:
		BasicSourceCodeParser.__init__(self)
		self.register_commands(CodeCommands.all_header_commands)

	def handles_token(self, token: Tokens.Token, parse_context: ParseContext) -> bool:
		return isinstance(token, Tokens.IdentifierToken) and token.raw_value == 'script'

	def parse(self, parse_context: ParseContext) -> bool:
		rollback = parse_context.lexer.get_rollback()
		token = parse_context.lexer.skip(Tokens.NewlineToken)
		if not isinstance(token, Tokens.IdentifierToken) or not token.raw_value == 'script':
			parse_context.lexer.rollback(rollback)
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
		script_header = ParsedScriptHeader()
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
			command = self.parse_command(token, parse_context)
			if command.definition in commands_parsed:
				raise parse_context.error('Parse', f"Duplicate script header command '{command.definition.name}'")
			commands_parsed.append(command.definition)
			if command.definition == CodeCommands.HeaderNameString:
				script_header.string_id = command.params[0]
			elif command.definition == CodeCommands.HeaderBinFile:
				script_header.bwscript = bool(command.params[0])
			elif command.definition == CodeCommands.BroodwarOnly:
				script_header.broodwar_only = command.params[0]
			elif command.definition == CodeCommands.StarEditHidden:
				script_header.staredit_hidden = command.params[0]
			elif command.definition == CodeCommands.RequiresLocation:
				script_header.requires_location = command.params[0]
			elif command.definition == CodeCommands.EntryPoint:
				entry_point_name: str = command.params[0]
				script_header.entry_point_name = entry_point_name
				if entry_point := parse_context.lookup_block(entry_point_name):
					script_header.entry_point = entry_point
				else:
					parse_context.missing_block(entry_point_name, AIHeaderEntryPointBlockReferenceResolver(script_header, line))
		if not script_header.entry_point_name:
			raise parse_context.error('Parse', "Script with ID '%s' is missing an 'entry_point'" % script_id, line=line)
		parse_context.script_headers[script_id] = (script_header, line)
		return True

class AISourceCodeHandler(SourceCodeHandler):
	def __init__(self) -> None:
		super().__init__()
		self.register_parser(AISourceCodeParser())
		self.register_parser(AIHeaderSourceCodeParser())
		self.register_parser(AIDefinitionsSourceCodeParser())
