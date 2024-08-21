
from __future__ import annotations

from . import Tokens
from .ParseContext import ParseContext
from .SourceCodeHandler import SourceCodeParser
from .CodeDirective import CodeDirectiveDefinition

from ..PyMSError import PyMSError

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from .CodeType import CodeType

class Variable(object):
	def __init__(self, name: str, value: Any, type: CodeType) -> None:
		self.name = name
		self.value = value
		self.type = type

class DefinitionsHandler(object):
	class SymbolToken(Tokens.LiteralsToken):
		_literals = ('=', '@', '(', ')')

	def __init__(self) -> None:
		self.types: dict[str, CodeType] = {}
		self.variables: dict[str, Variable] = {}

	def register_type(self, type: CodeType) -> None:
		if type.name in self.types:
			raise PyMSError('Internal', "Type with name '%s' already exists" % type.name)
		self.types[type.name] = type

	def register_types(self, types: list[CodeType]) -> None:
		for type in types:
			self.register_type(type)

	def set_variable(self, name: str, value: Any, type: CodeType) -> None:
		self.variables[name] = Variable(name, value, type)

	def get_variable(self, name: str) -> (Variable | None):
		return self.variables.get(name, None)

	def lookup_variable(self, value: Any, type: CodeType) -> (Variable | None):
		matching_variable: Variable | None = None
		matching_priority: int = 0
		for variable in self.variables.values():
			if variable.value == value and (priority := type.compatible(variable.type)) and priority > matching_priority:
				matching_variable = variable
				matching_priority = priority
		return matching_variable

class DefinitionsSourceCodeParser(SourceCodeParser):
	def __init__(self) -> None:
		self.directive_defs: dict[str, CodeDirectiveDefinition] = {}

	def register_directive(self, directive_def: CodeDirectiveDefinition) -> None:
		if directive_def.name in self.directive_defs:
			raise PyMSError('Internal', f"Directive with name '{directive_def.name}' already exists")
		self.directive_defs[directive_def.name] = directive_def

	def register_directives(self, directive_defs: list[CodeDirectiveDefinition]) -> None:
		for directive_def in directive_defs:
			self.register_directive(directive_def)

	def handles_token(self, token: Tokens.Token, parse_context: ParseContext) -> bool:
		if isinstance(token, Tokens.LiteralsToken) and token.raw_value == '@':
			return True
		if isinstance(token, Tokens.IdentifierToken):
			return True
		return False

	def parse(self, parse_context: ParseContext) -> bool:
		definitions = parse_context.definitions
		assert definitions is not None
		parsed = False
		while True:
			rollback = parse_context.lexer.get_rollback()
			try:
				token = parse_context.lexer.skip(Tokens.NewlineToken)
				if isinstance(token, Tokens.EOFToken):
					break
				if isinstance(token, Tokens.IdentifierToken) and token.raw_value in definitions.types:
					type = definitions.types[token.raw_value]
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
					value = type.parse(token.raw_value, parse_context)
					definitions.set_variable(name, value, type)
					token = parse_context.lexer.next_token()
					if not isinstance(token, (Tokens.NewlineToken, Tokens.EOFToken)):
						raise parse_context.error('Parse', "Unexpected token '%s' (expected end of line or file)" % token.raw_value)
					parsed = True
					continue
				if isinstance(token, Tokens.LiteralsToken) and token.raw_value == '@':
					self.parse_directive(parse_context)
					continue
				parse_context.lexer.rollback(rollback)
				break
				# raise parse_context.error('Parse', "Unexpected token '%s'" % token.raw_value)
			except PyMSError:
				parse_context.lexer.rollback(rollback)
				raise
		return parsed

	def finalize(self, parse_context: ParseContext) -> None:
		pass

	def parse_directive(self, parse_context: ParseContext) -> None:
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IdentifierToken):
			raise parse_context.error('Parse', "Expected directive name, got '%s' instead" % token.raw_value)
		if not token.raw_value in self.directive_defs:
			raise parse_context.error('Parse', "Unknown directive '%s'" % token.raw_value)
		directive_def = self.directive_defs[token.raw_value]
		directive = directive_def.parse(parse_context)
		parse_context.handle_directive(directive)
