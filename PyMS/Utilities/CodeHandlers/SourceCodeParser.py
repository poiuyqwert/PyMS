
from __future__ import annotations

from . import Tokens
from ..PyMSError import PyMSError
from .CodeBlock import CodeBlock

from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
	from .ParseContext import ParseContext
	from .CodeCommand import CodeCommandDefinition
	from .CodeDirective import CodeDirectiveDefinition

class SourceCodeParser(Protocol):
	def parse(self, parse_context: ParseContext) -> bool:
		...

class BlockSourceCodeParser(SourceCodeParser):
	def parse(self, parse_context: ParseContext) -> bool:
		token = parse_context.lexer.skip(Tokens.NewlineToken)
		if isinstance(token, Tokens.EOFToken):
			return True
		if isinstance(token, Tokens.LiteralsToken) and (token.raw_value == ':' or token.raw_value == '--'):
			hyphens = (token.raw_value == '--')
			token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.IdentifierToken):
				raise parse_context.error('Parse', "Expected block name, got '%s' instead" % token.raw_value)
			name = token.raw_value
			block = parse_context.define_block(name, parse_context.lexer.state.line)
			token = parse_context.lexer.next_token()
			if hyphens:
				if not isinstance(token, Tokens.LiteralsToken) or token.raw_value != '--':
					raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected `--` to end the block name)")
				token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.NewlineToken):
				raise parse_context.error('Parse', "Unexpected token '%s' (expected end of line)" % token.raw_value)
			if parse_context.active_block:
				parse_context.active_block.next_block = block
				block.prev_block = parse_context.active_block
			parse_context.active_block = block
			parse_context.next_line()
			return True
		return False

class CommandSourceCodeParser(SourceCodeParser):
	def parse(self, parse_context: ParseContext) -> bool:
		token = parse_context.lexer.skip(Tokens.NewlineToken)
		if isinstance(token, Tokens.EOFToken):
			return True
		if isinstance(token, Tokens.IdentifierToken) and (cmd_def := parse_context.language.lookup_command(token.raw_value, parse_context.language_context)):
			command = cmd_def.parse(parse_context)
			if not parse_context.active_block:
				raise parse_context.error('Parse', "'%s' command defined outside of any block" % command.definition.name)
			parse_context.active_block.add_command(command)
			for param in command.params:
				if isinstance(param, CodeBlock):
					parse_context.add_block_use_block(param, parse_context.active_block)
			if command.definition.ends_flow:
				parse_context.active_block = None
			parse_context.next_line()
			return True
		return False

class DirectiveSourceCodeParser(SourceCodeParser):
	def __init__(self, directive_defs: list[CodeDirectiveDefinition] = []) -> None:
		self.directive_defs: dict[str, CodeDirectiveDefinition] = {}
		self.register_directives(directive_defs)

	def register_directive(self, directive_def: CodeDirectiveDefinition) -> None:
		if directive_def.name in self.directive_defs:
			raise PyMSError('Internal', f"Directive with name '{directive_def.name}' already exists")
		self.directive_defs[directive_def.name] = directive_def

	def register_directives(self, directive_defs: list[CodeDirectiveDefinition]) -> None:
		for directive_def in directive_defs:
			self.register_directive(directive_def)

	def parse(self, parse_context: ParseContext) -> bool:
		token = parse_context.lexer.skip(Tokens.NewlineToken)
		if isinstance(token, Tokens.EOFToken):
			return True
		if isinstance(token, Tokens.LiteralsToken) and token.raw_value == '@':
			token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.IdentifierToken):
				raise parse_context.error('Parse', "Expected directive name, got '%s' instead" % token.raw_value)
			if not token.raw_value in self.directive_defs:
				raise parse_context.error('Parse', "Unknown directive '%s'" % token.raw_value)
			directive_def = self.directive_defs[token.raw_value]
			directive = directive_def.parse(parse_context)
			parse_context.handle_directive(directive)
			return True
		return False

class DefineSourceCodeParser(SourceCodeParser):
	def parse(self, parse_context: ParseContext) -> bool:
		definitions = parse_context.definitions
		if definitions is None:
			return False
		token = parse_context.lexer.skip(Tokens.NewlineToken)
		if isinstance(token, Tokens.EOFToken):
			return True
		if isinstance(token, Tokens.IdentifierToken) and (code_type := parse_context.language.lookup_type(token.raw_value, parse_context.language_context)):
			token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.IdentifierToken):
				raise parse_context.error('Parse', "Expected variable name but got '%s'" % token.raw_value)
			name = token.raw_value
			if name in definitions.variables:
				raise parse_context.error('Parse', "Variable named '%s' is already defined" % name)
			token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.LiteralsToken) or not token.raw_value == '=':
				raise parse_context.error('Parse', "Expected '=' but got '%s'" % token.raw_value)
			token = parse_context.lexer.next_token()
			# TODO: Use type to parse?
			if not isinstance(token, Tokens.IntegerToken):
				raise parse_context.error('Parse', "Expected integer value but got '%s'" % token.raw_value)
			value = code_type.parse(token.raw_value, parse_context)
			definitions.set_variable(name, value, code_type)
			token = parse_context.lexer.next_token()
			if not isinstance(token, (Tokens.NewlineToken, Tokens.EOFToken)):
				raise parse_context.error('Parse', "Unexpected token '%s' (expected end of line or file)" % token.raw_value)
			return True
		return False
