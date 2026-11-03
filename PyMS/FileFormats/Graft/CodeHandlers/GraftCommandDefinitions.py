from __future__ import annotations

from . import CodeTypes
from ..Definitions import ParamKind, stat_preset

from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition, CodeCommand
from ....Utilities.CodeHandlers.CodeType import CodeType
from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers.SerializeContext import SerializeContext
from ....Utilities.CodeHandlers.Formatters import ParensCommandFormatter
from ....Utilities.CodeHandlers import Tokens
from ....Utilities.PyMSError import PyMSError

from typing import Any, Generator, Sequence, TypeVar

class GraftCommandDefinition(CodeCommandDefinition):
	# A command whose parameter types can depend on its earlier parameters, whose last parameters can be optional,
	# and which can be written with parentheses
	def __init__(self, name: str, help_text: str, param_types: Sequence[CodeType], *, required_params: int | None = None, parens: bool = False) -> None:
		super().__init__(name, help_text, None, param_types)
		self.required_params = len(param_types) if required_params is None else required_params
		self.parens = parens

	def param_type(self, index: int, _params: list[Any]) -> CodeType:
		# The type of parameter `index`, given the parameters before it
		return self.param_types[index]

	def comments(self, _params: list[Any], _context: SerializeContext) -> list[str]:
		# Comments for the command as a whole (after the comments of its parameters)
		return []

	def create(self, params: list[Any]) -> GraftCodeCommand:
		return GraftCodeCommand(self, params)

	def parse(self, parse_context: ParseContext) -> GraftCodeCommand:
		lexer = parse_context.lexer
		token = lexer.next_token(peek=True)
		in_parens = isinstance(token, Tokens.SymbolToken) and token.raw_value == '('
		if in_parens:
			_ = lexer.next_token()
		parse_context.command_in_parens = in_parens
		params: list[Any] = []
		for index in range(len(self.param_types)):
			if index >= self.required_params:
				token = lexer.next_token(peek=True)
				if (in_parens and token.raw_value == ')') or (not in_parens and isinstance(token, (Tokens.NewlineToken, Tokens.EOFToken))):
					break
			if in_parens and index > 0:
				token = lexer.next_token()
				if token.raw_value != ',':
					raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected `,` separating parameters)")
			try:
				params.append(self.param_type(index, params).parse(parse_context))
			except PyMSError as e:
				parse_context.attribute_error(e)
				raise
		if in_parens:
			token = lexer.next_token()
			if token.raw_value != ')':
				raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected `)` to end parameters)")
		parse_context.command_in_parens = False
		token = lexer.next_token()
		if not isinstance(token, (Tokens.NewlineToken, Tokens.EOFToken)):
			raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected end of line or file)")
		return self.create(params)

class GraftCodeCommand(CodeCommand):
	definition: GraftCommandDefinition

	def __init__(self, definition: GraftCommandDefinition, params: list[Any]) -> None:
		super().__init__(definition, params)
		self.definition = definition

	def iter_params(self) -> Generator[tuple[Any, CodeType], None, None]:
		for index, param in enumerate(self.params):
			yield (param, self.definition.param_type(index, self.params))

	def serialize(self, context: SerializeContext) -> None:
		parameters: list[str] = []
		comments: list[str] = []
		for param, param_type in self.iter_params():
			parameters.append(param_type.serialize(param, context))
			if (comment := param_type.comment(param, context)) is not None:
				comments.append(comment)
		comments.extend(self.definition.comments(self.params, context))
		formatter = ParensCommandFormatter() if self.definition.parens else context.formatters.command
		context.write(formatter.serialize(self.definition.name, parameters))
		if comments:
			context.write(context.formatters.comment.serialize(comments))
		context.write('\n')

class ButtonFunctionCommandDefinition(GraftCommandDefinition):
	# A button condition or action function, with the function's parameter.
	# Functions without a parameter still store a value, which can be given as an optional raw value.
	KIND: str

	def __init__(self, address: int, name: str, display_name: str, param_kind: ParamKind) -> None:
		kind = self.KIND
		param_type = CodeTypes.id_type(param_kind, f'{kind}_param')
		if param_kind == ParamKind.none:
			help_text = f'{kind.capitalize()} `{display_name}` (with the optional unused value {{1}})'
			required_params = 0
		else:
			help_text = f'{kind.capitalize()} `{display_name}` for {param_kind.value} {{1}}'
			required_params = 1
		super().__init__(name, help_text, (param_type,), required_params=required_params)
		self.address = address # Vanilla StarCraft 1.16.1 function address
		self.display_name = display_name # Name used by FireGraft
		self.param_kind = param_kind
		self.function_index = -1 # Index stored in Buttons.graft, set by `number_functions`

	def create_with_param(self, param: int) -> GraftCodeCommand:
		# The unused value of a function without a parameter is only written when it is set
		if self.required_params == 0 and param == 0:
			return self.create([])
		return self.create([param])

	def param_value(self, command: CodeCommand) -> int:
		return command.params[0] if command.params else 0

class ButtonConditionCommandDefinition(ButtonFunctionCommandDefinition):
	KIND = 'condition'

class ButtonActionCommandDefinition(ButtonFunctionCommandDefinition):
	KIND = 'action'

F = TypeVar('F', bound=ButtonFunctionCommandDefinition)
def number_functions(functions: list[F]) -> list[F]:
	# Sets each function's index to its position in its list
	for index, function in enumerate(functions):
		function.function_index = index
	return functions

class StatInfoCommandDefinition(GraftCommandDefinition):
	def comments(self, params: list[Any], _context: SerializeContext) -> list[str]:
		if preset := stat_preset(params[0], params[1]):
			return [f'Stat preset: {preset.name}']
		return []
