from __future__ import annotations

from .CodeHandlers import ButtonCodeCommands
from .CodeHandlers.GraftLanguage import ButtonsLanguage
from .CodeHandlers.GraftParseContext import GraftParseContext
from .CodeHandlers.GraftSerializeContext import GraftSerializeContext
from .CodeHandlers.GraftCommandDefinition import GraftCommandDefinition

from ...Utilities.CodeHandlers.CodeCommand import CodeCommand
from ...Utilities.CodeHandlers.CodeStruct import StructBlock, StructField, parse_end_of_line
from ...Utilities.CodeHandlers import Tokens
from ...Utilities.PyMSError import PyMSError
from ...Utilities import Struct

from dataclasses import dataclass, field

class Button(Struct.Struct):
	position: int
	icon: int
	condition: int
	action: int
	condition_param: int
	action_param: int
	enabled_string: int
	disabled_string: int

	_fields = (
		('position', Struct.t_u16),
		('icon', Struct.t_u16),
		('condition', Struct.t_u32),
		('action', Struct.t_u32),
		('condition_param', Struct.t_u16),
		('action_param', Struct.t_u16),
		('enabled_string', Struct.t_u16),
		('disabled_string', Struct.t_u16),
	)

	def __init__(self, *, position: int = 1, icon: int = 0, condition: int = 0, action: int = 0, condition_param: int = 0, action_param: int = 0, enabled_string: int = 0, disabled_string: int = 0) -> None:
		self.position = position
		self.icon = icon
		self.condition = condition # Index into `ButtonCodeCommands.condition_commands`
		self.action = action # Index into `ButtonCodeCommands.action_commands`
		self.condition_param = condition_param
		self.action_param = action_param
		self.enabled_string = enabled_string
		self.disabled_string = disabled_string

	def copy(self) -> Button:
		return Button(position=self.position, icon=self.icon, condition=self.condition, action=self.action, condition_param=self.condition_param, action_param=self.action_param, enabled_string=self.enabled_string, disabled_string=self.disabled_string)

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Button):
			return False
		return self.pack() == other.pack()

	def __hash__(self) -> int:
		return hash(self.pack())

	def find_unknown_function(self) -> str | None:
		# Every button must use a known condition and action, since they're written by name
		if not 0 <= self.condition < len(ButtonCodeCommands.condition_commands):
			return f'unknown button condition {self.condition}'
		if not 0 <= self.action < len(ButtonCodeCommands.action_commands):
			return f'unknown button action {self.action}'
		return None

	def to_block(self) -> StructBlock:
		commands: list[CodeCommand] = [CodeCommand(ButtonCodeCommands.Position, [self.position]), CodeCommand(ButtonCodeCommands.Icon, [self.icon])]
		# The stored value of a function without a parameter is unused, so it isn't written
		condition = ButtonCodeCommands.condition_commands[self.condition]
		commands.append(CodeCommand(condition, [self.condition_param] if condition.param_types else []))
		action = ButtonCodeCommands.action_commands[self.action]
		commands.append(CodeCommand(action, [self.action_param] if action.param_types else []))
		commands.append(CodeCommand(ButtonCodeCommands.EnabledStr, [self.enabled_string]))
		commands.append(CodeCommand(ButtonCodeCommands.DisabledStr, [self.disabled_string]))
		return StructBlock(ButtonCodeCommands.ButtonBlock, [], commands)

	@staticmethod
	def _function_value(block: StructBlock, struct_field: StructField) -> tuple[int, int]:
		# The function index and parameter of a condition or action
		command = block.get(struct_field)
		assert command is not None and isinstance(command.definition, GraftCommandDefinition)
		return (command.definition.function_index, command.params[0] if command.params else 0)

	@classmethod
	def from_block(cls, block: StructBlock) -> Button:
		condition, condition_param = cls._function_value(block, ButtonCodeCommands.ButtonConditionField)
		action, action_param = cls._function_value(block, ButtonCodeCommands.ButtonActionField)
		return cls(
			position=block.param(ButtonCodeCommands.Position),
			icon=block.param(ButtonCodeCommands.Icon),
			condition=condition,
			condition_param=condition_param,
			action=action,
			action_param=action_param,
			enabled_string=block.param(ButtonCodeCommands.EnabledStr),
			disabled_string=block.param(ButtonCodeCommands.DisabledStr),
		)

# The buttons a button card shows. Its ID is its index in `ButtonsGraft.button_sets`, so it isn't stored here.
@dataclass
class ButtonSet:
	buttons: list[Button] = field(default_factory=list)

	def copy(self) -> ButtonSet:
		return ButtonSet([button.copy() for button in self.buttons])

	@staticmethod
	def check_language(parse_context: GraftParseContext) -> None:
		if not isinstance(parse_context.language, ButtonsLanguage):
			raise PyMSError('Internal', f'Buttons.graft code must be compiled with a parse context using `{ButtonsLanguage.__name__}`')

	def find_unknown_function(self) -> str | None:
		# The problem with the first button that uses an unknown function
		for button in self.buttons:
			if problem := button.find_unknown_function():
				return problem
		return None

	def serialize(self, serialize_context: GraftSerializeContext) -> None:
		# Only the buttons (the body of the `button_set` block)
		for button in self.buttons:
			button.to_block().serialize(serialize_context)

	def to_block(self, set_id: int) -> StructBlock:
		return StructBlock(ButtonCodeCommands.ButtonSetBlock, [set_id], children=[button.to_block() for button in self.buttons])

	@classmethod
	def from_block(cls, block: StructBlock) -> ButtonSet:
		return cls([Button.from_block(child) for child in block.children])

	@classmethod
	def compile(cls, parse_context: GraftParseContext, set_id: int) -> ButtonSet:
		# Compiles only the buttons of a button set (no `button_set` header) into the button set for `set_id`
		cls.check_language(parse_context)
		button_block = ButtonCodeCommands.ButtonBlock
		set_keyword = ButtonCodeCommands.ButtonSetBlock.keyword
		buttons: list[Button] = []
		while True:
			token = parse_context.lexer.skip(Tokens.NewlineToken)
			if isinstance(token, Tokens.EOFToken):
				break
			if isinstance(token, Tokens.IdentifierToken) and token.raw_value == set_keyword:
				raise parse_context.error('Parse', f"'{set_keyword}' headers are not allowed, the code is only the buttons of button set {set_id}")
			if not isinstance(token, Tokens.IdentifierToken) or token.raw_value != button_block.keyword:
				raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected '{button_block.keyword}')")
			buttons.append(Button.from_block(button_block.parse(parse_context)))
			parse_end_of_line(parse_context)
		parse_context.finalize()
		return cls(buttons)

@dataclass
class ButtonCard:
	button_set: int | None = None # Index into `ButtonsGraft.button_sets`
	connected_unit: int | None = None

	def to_block(self, card_id: int) -> StructBlock:
		return StructBlock(ButtonCodeCommands.ButtonCardBlock, [card_id], [
			CodeCommand(ButtonCodeCommands.UseButtonSet, [self.button_set]),
			CodeCommand(ButtonCodeCommands.ConnectedUnit, [self.connected_unit]),
		])

	@classmethod
	def from_block(cls, block: StructBlock) -> ButtonCard:
		return cls(block.param(ButtonCodeCommands.UseButtonSet), block.param(ButtonCodeCommands.ConnectedUnit))
