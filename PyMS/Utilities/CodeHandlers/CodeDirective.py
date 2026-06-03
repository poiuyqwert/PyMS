
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

	def parse(self, parse_context: ParseContext) -> O:
		start = parse_context.lexer.get_rollback()
		value = self.lex(parse_context)
		raw_value = parse_context.lexer.get_raw(from_state=start)
		self.validate(value, parse_context, raw_value)
		return value

	def lex(self, parse_context: ParseContext) -> O:
		raise NotImplementedError(self.__class__.__name__ + '.lex()')

	def validate(self, value: O, parse_context: ParseContext, token: str | None = None) -> None:
		pass

class CodeDirectiveDefinition:
	@staticmethod
	def find_by_name(name: str, directive_defs: list[CodeDirectiveDefinition]) -> CodeDirectiveDefinition | None:
		for directive_def in directive_defs:
			if directive_def.name == name:
				return directive_def
		return None

	def __init__(self, name: str, help_text: str, param_types: Sequence[DirectiveType] = ()) -> None:
		self.name = name
		self.help_text = help_text
		self.param_types = param_types

	def parse(self, parse_context: ParseContext) -> CodeDirective:
		params: list[Any] = []
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.LiteralsToken) or not token.raw_value == '(':
			raise parse_context.error('Parse', f"Expected '(' but got '{token.raw_value}'")
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
			params.append(value)
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.LiteralsToken) or token.raw_value != ')':
			raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected `)` to end parameters)")
		token = parse_context.lexer.next_token()
		if not isinstance(token, (Tokens.NewlineToken, Tokens.EOFToken)):
			raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected end of line or file)")
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
			description = description.replace(f'{{{n + 1}}}', f'`{param_name}`')
			if n:
				command += ', '
			command += param_name
		command += ')'
		help_text = f'{command}\n    {description}'
		if params_help:
			help_text += '\n'
			help_text += params_help
		return help_text

class CodeDirective:
	def __init__(self, definition: CodeDirectiveDefinition, params: list[Any]) -> None:
		self.definition = definition
		self.params = params
