
from . import CodeCommands
from . import CodeDirectives
from .AILexer import AILexer
from ..AIFlag import AIFlag

from ....Utilities.CodeHandlers.SourceCodeHandler import SourceCodeHandler
from ....Utilities.CodeHandlers.ParseContext import ParseContext, BlockReferenceResolver
from ....Utilities.CodeHandlers.CodeBlock import CodeBlock
from ....Utilities.CodeHandlers import Tokens
from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ....Utilities.PyMSError import PyMSError

class AISourceCodeHandler(SourceCodeHandler):
	def __init__(self) -> None:
		SourceCodeHandler.__init__(self)
		self.script_headers: dict[str, tuple[AIHeaderSourceCodeHandler.AIScriptHeader, int]] = {}
		self.register_commands(CodeCommands.all_basic_commands)
		self.register_directives(CodeDirectives.all_basic_directives)

	def parse_custom(self, token: Tokens.Token, parse_context: ParseContext) -> bool:
		if isinstance(token, Tokens.IdentifierToken) and token.raw_value == 'script':
			parse_context.next_line()
			token = parse_context.lexer.check_token(AILexer.ScriptIDToken)
			if not isinstance(token, AILexer.ScriptIDToken):
				raise parse_context.error('Parse', "Expected script ID, got '%s' instead" % token.raw_value)
			line = parse_context.lexer.line
			script_id = token.raw_value
			if script_id in self.script_headers:
				_,existing_line = self.script_headers[script_id]
				raise parse_context.error('Parse', "A script with id '%s' is already defined on line %d" % (script_id, existing_line))
			code_handler = AIHeaderSourceCodeHandler()
			code_handler.parse(parse_context)
			# TODO: Validate header
			if not code_handler.script_header:
				raise PyMSError('Parse', "No script header found")
			if not code_handler.script_header.entry_point_name:
				raise parse_context.error('Parse', "Script with ID '%s' is missing an 'entry_point'" % script_id)
			self.script_headers[script_id] = (code_handler.script_header, line)
			return True
		return False

class AIHeaderSourceCodeHandler(SourceCodeHandler):
	class AIScriptHeader(object):
		def __init__(self) -> None:
			self.string_id: int | None = None
			self.bwscript: bool | None = None
			self.broodwar_only: bool | None = None
			self.staredit_hidden: bool | None = None
			self.requires_location: bool | None = None
			self.entry_point_name: str | None = None
			self.entry_point: CodeBlock | None = None
		
		@property
		def flags(self) -> int:
			return (AIFlag.requires_location if self.requires_location else 0) | (AIFlag.staredit_hidden if self.staredit_hidden else 0) | (AIFlag.broodwar_only if self.broodwar_only else 0)

	def __init__(self) -> None:
		SourceCodeHandler.__init__(self)
		self.register_commands(CodeCommands.all_header_commands)
		self.script_header: AIHeaderSourceCodeHandler.AIScriptHeader | None = None

	def parse(self, parse_context: ParseContext) -> None:
		script_header = AIHeaderSourceCodeHandler.AIScriptHeader()
		commands_parsed: list[CodeCommandDefinition] = []
		token = parse_context.lexer.next_token()
		if not isinstance(token, AILexer.SymbolToken) or token.raw_value != '{':
			raise parse_context.error('Parse', "Expected a '{' to start the script header, got '%s' instead" % token.raw_value)
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.NewlineToken):
			raise parse_context.error('Parse', "Unexpected token '%s' (expected end of line)" % token.raw_value)
		while True:
			token = parse_context.lexer.next_token()
			line = parse_context.lexer.line
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
		self.script_header = script_header

class AIHeaderEntryPointBlockReferenceResolver(BlockReferenceResolver):
	def __init__(self, header: AIHeaderSourceCodeHandler.AIScriptHeader, source_line: int | None) -> None:
		BlockReferenceResolver.__init__(self, source_line)
		self.header = header

	def block_defined(self, block):
		self.header.entry_point = block
