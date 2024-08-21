
from __future__ import annotations

from PyMS.Utilities.CodeHandlers.Lexer import Lexer

from . import Tokens
from .ParseContext import ParseContext

from ..PyMSError import PyMSError

from typing import TYPE_CHECKING, Sequence, Any, Generic, TypeVar
if TYPE_CHECKING:
	from .Lexer import Lexer

O = TypeVar('O')
class DirectiveType(Generic[O]):
	def __init__(self, name: str) -> None:
		self.name = name

	def lex(self, parse_context: ParseContext) -> O:
		raise NotImplementedError(self.__class__.__name__ + '.lex()')

	def parse(self, token: str, parse_context: ParseContext | None) -> O:
		raise NotImplementedError(self.__class__.__name__ + '.parse()')

	def validate(self, value: O, parse_context: ParseContext | None, token: str | None = None) -> None:
		raise NotImplementedError(self.__class__.__name__ + '.validate()')

class CodeDirectiveDefinition(object):
	def __init__(self, name: str, param_types: Sequence[DirectiveType] = ()) -> None:
		self.name = name
		self.param_types = param_types

	def parse(self, parse_context: ParseContext) -> CodeDirective:
		params: list[Any] = []
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.LiteralsToken) or not token.raw_value == '(':
			raise parse_context.error('Parse', "Expected '(' but got '%s'" % token.raw_value)
		for param_index,param_type in enumerate(self.param_types):
			if param_index > 0:
				token = parse_context.lexer.next_token()
				if not isinstance(token, Tokens.LiteralsToken) or token.raw_value != ',':
					raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected `,` separating parameters)")
			try:
				value = param_type.lex(parse_context)
			except PyMSError as e:
				parse_context.attribute_error(e)
				raise e
			except:
				raise
			params.append(value)
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.LiteralsToken) or token.raw_value != ')':
			raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected `)` to end parameters)")
		token = parse_context.lexer.next_token()
		if not isinstance(token, (Tokens.NewlineToken, Tokens.EOFToken)):
			raise parse_context.error('Parse', "Unexpected token '%s' (expected end of line or file)" % token.raw_value)
		return CodeDirective(self, params)

class CodeDirective(object):
	def __init__(self, definition: CodeDirectiveDefinition, params: list[Any]) -> None:
		self.definition = definition
		self.params = params
