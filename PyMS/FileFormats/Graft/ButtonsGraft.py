from __future__ import annotations

from .Definitions import DEFAULT_BUTTON_CARD_COUNT, DEFAULT_STAT_COUNT, NO_CONNECTED_UNIT
from .CodeHandlers import CodeTypes
from .CodeHandlers import ButtonCodeCommands
from .CodeHandlers import StatInfoCodeCommands
from .CodeHandlers.GraftLanguage import ButtonsLanguage
from .CodeHandlers.GraftParseContext import GraftParseContext
from .CodeHandlers.GraftSerializeContext import GraftSerializeContext
from .CodeHandlers.GraftCommandDefinitions import FunctionCommandDefinition, ButtonFunctionCommandDefinition

from ...Utilities.CodeHandlers.CodeCommand import CodeCommand
from ...Utilities.CodeHandlers.CodeStruct import StructBlock, StructField, parse_struct_blocks
from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities import Struct
from ...Utilities import Assets
from ...Utilities import IO

from dataclasses import dataclass
import os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .FGP import FGP

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

class _ButtonCardEntry(Struct.Struct):
	button_count: int
	first_button: int
	connected_unit: int
	padding: int

	_fields = (
		('button_count', Struct.t_u32),
		('first_button', Struct.t_u32), # Index into the buttons list
		('connected_unit', Struct.t_u16),
		('padding', Struct.t_u16),
	)

	def __init__(self, button_count: int = 0, first_button: int = 0, connected_unit: int = NO_CONNECTED_UNIT, padding: int = 0) -> None:
		self.button_count = button_count
		self.first_button = first_button
		self.connected_unit = connected_unit
		self.padding = padding

class StatInfo(Struct.Struct):
	debug_unit_id: int
	status_function: int
	display_function: int

	_fields = (
		('debug_unit_id', Struct.t_u32), # Unused by the game
		('status_function', Struct.t_u32), # Index into `StatInfoCodeCommands.status_function_commands`
		('display_function', Struct.t_u32), # Index into `StatInfoCodeCommands.display_function_commands`
	)

	def __init__(self, debug_unit_id: int = 0, status_function: int = 0, display_function: int = 0) -> None:
		self.debug_unit_id = debug_unit_id
		self.status_function = status_function
		self.display_function = display_function

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, StatInfo):
			return False
		return self.pack() == other.pack()

	def __hash__(self) -> int:
		return hash(self.pack())

@dataclass
class ButtonCard:
	button_set: int | None = None # Index into `ButtonsGraft.button_sets`
	connected_unit: int | None = None

_HEADER = Struct.l_au32(3)

class ButtonsGraft:
	# Default filename for the file
	FILE_NAME = 'Buttons.graft'
	# Path the Graft Hook loads the file from in an MPQ
	MPQ_PATH = 'datreq\\Buttons.graft'

	def __init__(self) -> None:
		self.button_sets: list[list[Button]] = []
		self.button_cards: list[ButtonCard] = [ButtonCard() for _ in range(DEFAULT_BUTTON_CARD_COUNT)]
		self.stat_info: list[StatInfo] = [StatInfo(unit_id) for unit_id in range(DEFAULT_STAT_COUNT)]

	@classmethod
	def default_path(cls) -> str:
		return Assets.data_file_path(os.path.join('Graft', cls.FILE_NAME))

	def new(self) -> None:
		# The vanilla StarCraft buttons
		self.load(self.default_path())

	def load(self, any_input: IO.AnyInputBytes) -> list[PyMSWarning]:
		with IO.InputBytes(any_input) as f:
			data = f.read()
		warnings: list[PyMSWarning] = []
		try:
			if len(data) < _HEADER.size:
				raise PyMSError('Load', f'Unsupported {ButtonsGraft.FILE_NAME} file, the file is too small for its header')
			button_count, card_count, stat_count = _HEADER.unpack(data)
			size = _HEADER.size + button_count * Button.calcsize() + card_count * _ButtonCardEntry.calcsize() + stat_count * StatInfo.calcsize()
			if len(data) < size:
				raise PyMSError('Load', f'Unsupported {ButtonsGraft.FILE_NAME} file, the file is too small for its {button_count} buttons, {card_count} button cards, and {stat_count} stat infos')
			if len(data) > size:
				warnings.append(PyMSWarning(warn_type='Load', warning=f'{len(data) - size} bytes of unused data after the end of the file will be discarded'))
			offset = _HEADER.size
			buttons = Button.unpack_array(data, button_count, offset)
			offset += button_count * Button.calcsize()
			entries = _ButtonCardEntry.unpack_array(data, card_count, offset)
			offset += card_count * _ButtonCardEntry.calcsize()
			stat_info = StatInfo.unpack_array(data, stat_count, offset)
		except PyMSError:
			raise
		except Exception as exc:
			raise PyMSError('Load', f'Unsupported {ButtonsGraft.FILE_NAME} file, could possibly be invalid or corrupt') from exc

		for card_id, entry in enumerate(entries):
			if entry.button_count and entry.first_button + entry.button_count > button_count:
				raise PyMSError('Load', f'Unsupported {ButtonsGraft.FILE_NAME} file, button card {card_id} uses buttons {entry.first_button} to {entry.first_button + entry.button_count - 1} but there are only {button_count} buttons')

		# Rebuild the button sets from the ranges of buttons the button cards reference.
		# Any buttons no button card references are kept as their own sets so they aren't lost.
		button_sets: list[list[Button]] = []
		set_lookup: dict[tuple[int, int], int] = {}
		cursor = 0
		for first, count in sorted(set((entry.first_button, entry.button_count) for entry in entries if entry.button_count)):
			if first < cursor:
				warnings.append(PyMSWarning(warn_type='Load', warning=f'Buttons {first} to {first + count - 1} overlap another button set, they will be saved as a separate button set'))
			else:
				if first > cursor:
					button_sets.append(buttons[cursor:first])
				cursor = first + count
			set_lookup[(first, count)] = len(button_sets)
			button_sets.append([button.copy() for button in buttons[first:first + count]])
		if cursor < button_count:
			button_sets.append(buttons[cursor:])

		button_cards: list[ButtonCard] = []
		for entry in entries:
			button_set = set_lookup[(entry.first_button, entry.button_count)] if entry.button_count else None
			button_cards.append(ButtonCard(button_set, CodeTypes.ConnectedUnitCodeType.from_value(entry.connected_unit)))
		if padded_cards := [card_id for card_id, entry in enumerate(entries) if entry.padding]:
			warnings.append(PyMSWarning(warn_type='Load', warning=f"Button card(s) {', '.join(str(card_id) for card_id in padded_cards)} have unused data after their connected unit, it will be discarded"))

		for set_id, button_set_buttons in enumerate(button_sets):
			ButtonsGraft._check_functions(set_id, button_set_buttons, 'Load')
		for unit_id, info in enumerate(stat_info):
			ButtonsGraft._check_stat_functions(unit_id, info, 'Load')

		self.button_sets = button_sets
		self.button_cards = button_cards
		self.stat_info = stat_info
		return warnings

	def save(self, output: IO.AnyOutputBytes) -> None:
		set_offsets: list[int] = []
		buttons = bytearray()
		button_count = 0
		for button_set in self.button_sets:
			set_offsets.append(button_count)
			for button in button_set:
				buttons += button.pack()
			button_count += len(button_set)
		entries = bytearray()
		for card_id, card in enumerate(self.button_cards):
			entry = _ButtonCardEntry(connected_unit=CodeTypes.ConnectedUnitCodeType.to_value(card.connected_unit))
			if card.button_set is not None:
				if not 0 <= card.button_set < len(self.button_sets):
					raise PyMSError('Save', f'Button card {card_id} uses button set {card.button_set}, which does not exist')
				# An empty button set is saved the same as no button set
				entry.button_count = len(self.button_sets[card.button_set])
				if entry.button_count:
					entry.first_button = set_offsets[card.button_set]
			entries += entry.pack()
		data = _HEADER.pack([button_count, len(self.button_cards), len(self.stat_info)]) + buttons + entries
		for info in self.stat_info:
			data += info.pack()
		with IO.OutputBytes(output) as f:
			f.write(bytes(data))

	def add_button_set(self, buttons: list[Button] | None = None) -> int:
		self.button_sets.append(buttons if buttons is not None else [])
		return len(self.button_sets) - 1

	def button_cards_using_button_set(self, set_id: int) -> list[int]:
		return [card_id for card_id, card in enumerate(self.button_cards) if card.button_set == set_id]

	def remove_button_set(self, set_id: int) -> list[Button]:
		if not 0 <= set_id < len(self.button_sets):
			raise PyMSError('Internal', f'Button set {set_id} does not exist')
		if users := self.button_cards_using_button_set(set_id):
			raise PyMSError('Internal', f"Button set {set_id} can't be removed because it is used by button card(s) {', '.join(str(card_id) for card_id in users)}")
		buttons = self.button_sets.pop(set_id)
		for card in self.button_cards:
			if card.button_set is not None and card.button_set > set_id:
				card.button_set -= 1
		return buttons

	def set_button_card_count(self, count: int) -> None:
		if count < len(self.button_cards):
			del self.button_cards[count:]
		else:
			self.button_cards.extend(ButtonCard() for _ in range(count - len(self.button_cards)))

	def set_stat_count(self, count: int) -> None:
		if count < len(self.stat_info):
			del self.stat_info[count:]
		else:
			self.stat_info.extend(StatInfo(unit_id) for unit_id in range(len(self.stat_info), count))

	@staticmethod
	def _check_functions(set_id: int, buttons: list[Button], error_type: str) -> None:
		# Every button must use a known condition and action, since they're written by name
		for button in buttons:
			if not 0 <= button.condition < len(ButtonCodeCommands.condition_commands):
				raise PyMSError(error_type, f'Button set {set_id} uses unknown button condition {button.condition}')
			if not 0 <= button.action < len(ButtonCodeCommands.action_commands):
				raise PyMSError(error_type, f'Button set {set_id} uses unknown button action {button.action}')

	@staticmethod
	def _check_stat_functions(unit_id: int, info: StatInfo, error_type: str) -> None:
		# Every unit must use a known status and display function, since they're written by name
		if not 0 <= info.status_function < len(StatInfoCodeCommands.status_function_commands):
			raise PyMSError(error_type, f'Unit {unit_id} uses unknown status function {info.status_function}')
		if not 0 <= info.display_function < len(StatInfoCodeCommands.display_function_commands):
			raise PyMSError(error_type, f'Unit {unit_id} uses unknown display function {info.display_function}')

	@staticmethod
	def _button_block(button: Button) -> StructBlock:
		commands: list[CodeCommand] = [ButtonCodeCommands.Icon.create([button.icon])]
		commands.append(ButtonCodeCommands.condition_commands[button.condition].create_with_param(button.condition_param))
		commands.append(ButtonCodeCommands.action_commands[button.action].create_with_param(button.action_param))
		commands.append(ButtonCodeCommands.EnabledStr.create([button.enabled_string]))
		commands.append(ButtonCodeCommands.DisabledStr.create([button.disabled_string]))
		return StructBlock(ButtonCodeCommands.ButtonBlock, [button.position], commands)

	@staticmethod
	def _function_value(block: StructBlock, field: StructField) -> tuple[int, int]:
		# The function index and parameter of a condition or action
		command = block.get(field)
		assert command is not None and isinstance(command.definition, ButtonFunctionCommandDefinition)
		return (command.definition.function_index, command.definition.param_value(command))

	@staticmethod
	def _function_index(block: StructBlock, field: StructField) -> int:
		# The function index of a status or display function
		command = block.get(field)
		assert command is not None and isinstance(command.definition, FunctionCommandDefinition)
		return command.definition.function_index

	@staticmethod
	def _button(block: StructBlock) -> Button:
		condition, condition_param = ButtonsGraft._function_value(block, ButtonCodeCommands.ButtonConditionField)
		action, action_param = ButtonsGraft._function_value(block, ButtonCodeCommands.ButtonActionField)
		return Button(
			position=block.header_params[0],
			icon=block.param(ButtonCodeCommands.Icon),
			condition=condition,
			condition_param=condition_param,
			action=action,
			action_param=action_param,
			enabled_string=block.param(ButtonCodeCommands.EnabledStr),
			disabled_string=block.param(ButtonCodeCommands.DisabledStr),
		)

	def decompile(self, serialize_context: GraftSerializeContext) -> None:
		for set_id, buttons in enumerate(self.button_sets):
			StructBlock(ButtonCodeCommands.ButtonSetBlock, [set_id], children=[ButtonsGraft._button_block(button) for button in buttons]).serialize(serialize_context)
			serialize_context.write('\n')
		for card_id, card in enumerate(self.button_cards):
			StructBlock(ButtonCodeCommands.ButtonCardBlock, [card_id], [
				ButtonCodeCommands.UseButtonSet.create([card.button_set]),
				ButtonCodeCommands.ConnectedUnit.create([card.connected_unit]),
			]).serialize(serialize_context)
			serialize_context.write('\n')
		for unit_id, info in enumerate(self.stat_info):
			StructBlock(StatInfoCodeCommands.UnitStatInfoBlock, [unit_id], [
				StatInfoCodeCommands.UnitUnused.create([info.debug_unit_id]),
				StatInfoCodeCommands.status_function_commands[info.status_function].create([]),
				StatInfoCodeCommands.display_function_commands[info.display_function].create([]),
			]).serialize(serialize_context)
			serialize_context.write('\n')

	@staticmethod
	def compile(parse_context: GraftParseContext) -> ButtonsGraft:
		if not isinstance(parse_context.language, ButtonsLanguage):
			raise PyMSError('Internal', f'ButtonsGraft must be compiled with a parse context using `{ButtonsLanguage.__name__}`')
		button_sets: dict[int, list[Button]] = {}
		button_cards: dict[int, ButtonCard] = {}
		stat_info: dict[int, StatInfo] = {}
		header_lines: dict[tuple[str, int], int] = {}
		for block in parse_struct_blocks(parse_context, (ButtonCodeCommands.ButtonSetBlock, ButtonCodeCommands.ButtonCardBlock, StatInfoCodeCommands.UnitStatInfoBlock)):
			definition = block.definition
			entry_id: int = block.header_params[0]
			assert block.line is not None
			if (definition.keyword, entry_id) in header_lines:
				raise parse_context.error('Parse', f'{definition.title(block.header_params)} is already defined on line {header_lines[(definition.keyword, entry_id)] + 1}', line=block.line)
			header_lines[(definition.keyword, entry_id)] = block.line
			if definition is ButtonCodeCommands.ButtonSetBlock:
				button_sets[entry_id] = [ButtonsGraft._button(child) for child in block.children]
			elif definition is ButtonCodeCommands.ButtonCardBlock:
				button_cards[entry_id] = ButtonCard(block.param(ButtonCodeCommands.UseButtonSet), block.param(ButtonCodeCommands.ConnectedUnit))
			else:
				status_function = ButtonsGraft._function_index(block, StatInfoCodeCommands.UnitStatusFunctionField)
				display_function = ButtonsGraft._function_index(block, StatInfoCodeCommands.UnitDisplayFunctionField)
				stat_info[entry_id] = StatInfo(block.param(StatInfoCodeCommands.UnitUnused, entry_id), status_function, display_function)

		buttons_graft = ButtonsGraft()
		set_count = max(button_sets.keys()) + 1 if button_sets else 0
		buttons_graft.button_sets = [button_sets.get(set_id, []) for set_id in range(set_count)]
		card_count = max(button_cards.keys()) + 1 if button_cards else 0
		buttons_graft.button_cards = [button_cards.get(card_id, ButtonCard()) for card_id in range(card_count)]
		card_title = ButtonCodeCommands.ButtonCardBlock.title
		for card_id, card in enumerate(buttons_graft.button_cards):
			if card.button_set is not None and card.button_set >= set_count:
				line = header_lines[(ButtonCodeCommands.ButtonCardBlock.keyword, card_id)]
				raise PyMSError('Parse', f'{card_title([card_id])} uses button set {card.button_set}, which is not defined', line=line, code=parse_context.lexer.get_line_of_code(line))
		# Stat info is a table for units 0 up to the last `unit_stat_info`, so it can't have gaps
		stat_count = max(stat_info.keys()) + 1 if stat_info else 0
		stat_info_title = StatInfoCodeCommands.UnitStatInfoBlock.title
		for unit_id in range(stat_count):
			if unit_id not in stat_info:
				raise PyMSError('Parse', f'{stat_info_title([unit_id])} is not defined (every unit up to the last `{StatInfoCodeCommands.UnitStatInfoBlock.keyword}` needs one)')
		buttons_graft.stat_info = [stat_info[unit_id] for unit_id in range(stat_count)]
		parse_context.finalize()
		return buttons_graft

	def import_fgp(self, fgp: FGP) -> list[PyMSWarning]:
		# Lays the FireGraft project's buttons over the current buttons
		warnings: list[PyMSWarning] = []
		for set_id, buttons in fgp.button_sets.items():
			ButtonsGraft._check_functions(set_id, buttons, 'Import')
		for fg_unit in fgp.units:
			if fg_unit.stat_info is not None:
				ButtonsGraft._check_stat_functions(fg_unit.unit_id, fg_unit.stat_info, 'Import')
		for set_id, buttons in fgp.button_sets.items():
			while set_id >= len(self.button_sets):
				self.button_sets.append([])
			self.button_sets[set_id] = [button.copy() for button in buttons]
		for fg_unit in fgp.units:
			if fg_unit.unit_id >= len(self.button_cards):
				warnings.append(PyMSWarning(warn_type='Import', warning=f'FireGraft unit {fg_unit.unit_id} is past the last button card ({len(self.button_cards) - 1}) and was skipped'))
				continue
			if fg_unit.button_set is not None and fg_unit.button_set >= len(self.button_sets):
				warnings.append(PyMSWarning(warn_type='Import', warning=f'FireGraft unit {fg_unit.unit_id} uses button set {fg_unit.button_set}, which does not exist, so it was set to no button set'))
				button_set = None
			else:
				button_set = fg_unit.button_set
			self.button_cards[fg_unit.unit_id] = ButtonCard(button_set, CodeTypes.ConnectedUnitCodeType.from_value(fg_unit.connected_unit))
			if fg_unit.stat_info is not None:
				if fg_unit.unit_id >= len(self.stat_info):
					warnings.append(PyMSWarning(warn_type='Import', warning=f'FireGraft unit {fg_unit.unit_id} is past the last unit with stat info ({len(self.stat_info) - 1}), so its stat info was skipped'))
				else:
					self.stat_info[fg_unit.unit_id] = fg_unit.stat_info
		return warnings
