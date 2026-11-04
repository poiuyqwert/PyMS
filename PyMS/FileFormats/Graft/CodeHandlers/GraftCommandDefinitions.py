from __future__ import annotations

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

class FunctionCommandDefinition(GraftCommandDefinition):
	# A game function, stored in Buttons.graft as its index in its list of functions
	def __init__(self, name: str, display_name: str, help_text: str, *, param_types: Sequence[CodeType] = ()) -> None:
		super().__init__(name, help_text, param_types)
		self.display_name = display_name # Readable name (the name FireGraft uses, for button conditions and actions)
		self.function_index = -1 # Index stored in Buttons.graft, set by `number_functions`

class ButtonFunctionCommandDefinition(FunctionCommandDefinition):
	# A button condition or action function, with the function's parameter (if it uses one)
	KIND: str

	def __init__(self, name: str, display_name: str, param_type: CodeType | None = None) -> None:
		kind = self.KIND
		if param_type is None:
			help_text = f'{kind.capitalize()} `{display_name}`'
			param_types: tuple[CodeType, ...] = ()
		else:
			help_text = f'{kind.capitalize()} `{display_name}` for {param_type.name} {{1}}'
			param_types = (param_type,)
		super().__init__(name, display_name, help_text, param_types=param_types)

	def create_with_param(self, param: int) -> GraftCodeCommand:
		# The stored value of a function without a parameter is unused, so it isn't written
		if not self.param_types:
			return self.create([])
		return self.create([param])

	def param_value(self, command: CodeCommand) -> int:
		return command.params[0] if command.params else 0

class ButtonConditionCommandDefinition(ButtonFunctionCommandDefinition):
	KIND = 'condition'

class ButtonActionCommandDefinition(ButtonFunctionCommandDefinition):
	KIND = 'action'

F = TypeVar('F', bound=FunctionCommandDefinition)
def number_functions(functions: list[F]) -> list[F]:
	# Sets each function's index to its position in its list
	for index, function in enumerate(functions):
		function.function_index = index
	return functions
