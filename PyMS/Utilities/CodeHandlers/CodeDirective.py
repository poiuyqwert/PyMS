
from __future__ import annotations

from . import Tokens
from .ParseContext import ParseContext

from ..PyMSError import PyMSError

from typing import TYPE_CHECKING, Sequence, Any, Generic, TypeVar
if TYPE_CHECKING:
	from .Lexer import Lexer

O = TypeVar('O')
class DirectiveType(Generic[O]):
	def __init__(self, name: str, help_text: str) -> None:
		self.name = name
		self.help_text = help_text

	def lex(self, parse_context: ParseContext) -> O:
		raise NotImplementedError(self.__class__.__name__ + '.lex()')

	def parse(self, token: str, parse_context: ParseContext | None) -> O:
		raise NotImplementedError(self.__class__.__name__ + '.parse()')

	def validate(self, value: O, parse_context: ParseContext | None, token: str | None = None) -> None:
		raise NotImplementedError(self.__class__.__name__ + '.validate()')

class CodeDirectiveDefinition(object):
	def __init__(self, name: str, help_text: str, param_types: Sequence[DirectiveType] = ()) -> None:
		self.name = name
		self.help_text = help_text
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

	def full_help_text(self) -> str:
		command = f'{self.name}('
		description = self.help_text
		params_help = ''
		type_counts: dict[str, int] = {}
		for param_type in self.param_types:
			type_counts[param_type.name] = type_counts.get(param_type.name, 0) + 1
		param_counts: dict[str, int] = {}
		for n, param_type in enumerate(self.param_types):
			param_name = param_type.name
			param_counts[param_type.name] = param_counts.get(param_type.name, 0) + 1
			if param_counts[param_name] == 1:
				params_help += f'\n{param_type.name}: {param_type.help_text}'
			if type_counts[param_type.name] > 1:
				param_name += f'({param_counts[param_name]})'
			description = description.replace(f'{{{n}}}', f'`{param_name}`')
			if n:
				command += ', '
			command += param_name
		command += ')'
		help_text = f'{command}\n    {description}'
		if params_help:
			help_text += '\n'
			help_text += params_help
		return help_text

class CodeDirective(object):
	def __init__(self, definition: CodeDirectiveDefinition, params: list[Any]) -> None:
		self.definition = definition
		self.params = params
