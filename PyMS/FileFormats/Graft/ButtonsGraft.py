from __future__ import annotations

from .Definitions import STATUS_FUNCTIONS, DISPLAY_FUNCTIONS, DEFAULT_BUTTON_UNIT_COUNT, DEFAULT_STAT_COUNT, NO_CONNECTED_UNIT
from .CodeHandlers import CodeTypes
from .CodeHandlers import CodeCommands
from .CodeHandlers.GraftLanguage import ButtonsLanguage
from .CodeHandlers.GraftParseContext import GraftParseContext
from .CodeHandlers.GraftSerializeContext import GraftSerializeContext
from .CodeHandlers.GraftCommandDefinitions import ButtonFunctionCommandDefinition

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
		self.condition = condition # Index into `CodeCommands.condition_commands`
		self.action = action # Index into `CodeCommands.action_commands`
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

class _UnitButtonsEntry(Struct.Struct):
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
		('status_function', Struct.t_u32), # Index into `STATUS_FUNCTIONS`
		('display_function', Struct.t_u32), # Index into `DISPLAY_FUNCTIONS`
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
class UnitButtons:
	button_set: int | None = None # Index into `ButtonsGraft.button_sets`
	connected_unit: int | None = None
	padding: int = 0

_HEADER = Struct.l_au32(3)

class ButtonsGraft:
	# Default filename for the file
	FILE_NAME = 'Buttons.graft'
	# Path the Graft Hook loads the file from in an MPQ
	MPQ_PATH = 'datreq\\Buttons.graft'

	def __init__(self) -> None:
		self.button_sets: list[list[Button]] = []
		self.units: list[UnitButtons] = [UnitButtons() for _ in range(DEFAULT_BUTTON_UNIT_COUNT)]
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
			button_count, unit_count, stat_count = _HEADER.unpack(data)
			size = _HEADER.size + button_count * Button.calcsize() + unit_count * _UnitButtonsEntry.calcsize() + stat_count * StatInfo.calcsize()
			if len(data) < size:
				raise PyMSError('Load', f'Unsupported {ButtonsGraft.FILE_NAME} file, the file is too small for its {button_count} buttons, {unit_count} units, and {stat_count} stat infos')
			if len(data) > size:
				warnings.append(PyMSWarning(warn_type='Load', warning=f'{len(data) - size} bytes of unused data after the end of the file will be discarded'))
			offset = _HEADER.size
			buttons = Button.unpack_array(data, button_count, offset)
			offset += button_count * Button.calcsize()
			entries = _UnitButtonsEntry.unpack_array(data, unit_count, offset)
			offset += unit_count * _UnitButtonsEntry.calcsize()
			stat_info = StatInfo.unpack_array(data, stat_count, offset)
		except PyMSError:
			raise
		except Exception as exc:
			raise PyMSError('Load', f'Unsupported {ButtonsGraft.FILE_NAME} file, could possibly be invalid or corrupt') from exc

		for unit_id, entry in enumerate(entries):
			if entry.button_count and entry.first_button + entry.button_count > button_count:
				raise PyMSError('Load', f'Unsupported {ButtonsGraft.FILE_NAME} file, unit {unit_id} uses buttons {entry.first_button} to {entry.first_button + entry.button_count - 1} but there are only {button_count} buttons')

		# Rebuild the button sets from the ranges of buttons the units reference.
		# Any buttons no unit references are kept as their own sets so they aren't lost.
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

		units: list[UnitButtons] = []
		for entry in entries:
			button_set = set_lookup[(entry.first_button, entry.button_count)] if entry.button_count else None
			units.append(UnitButtons(button_set, CodeTypes.ConnectedUnitCodeType.from_value(entry.connected_unit), entry.padding))

		for set_id, button_set_buttons in enumerate(button_sets):
			for button in button_set_buttons:
				if not 0 <= button.condition < len(CodeCommands.condition_commands):
					warnings.append(PyMSWarning(warn_type='Load', warning=f'Button set {set_id} uses unknown button condition {button.condition}'))
				if not 0 <= button.action < len(CodeCommands.action_commands):
					warnings.append(PyMSWarning(warn_type='Load', warning=f'Button set {set_id} uses unknown button action {button.action}'))
		for unit_id, info in enumerate(stat_info):
			if not 0 <= info.status_function < len(STATUS_FUNCTIONS):
				warnings.append(PyMSWarning(warn_type='Load', warning=f'Unit {unit_id} uses unknown status function {info.status_function}'))
			if not 0 <= info.display_function < len(DISPLAY_FUNCTIONS):
				warnings.append(PyMSWarning(warn_type='Load', warning=f'Unit {unit_id} uses unknown display function {info.display_function}'))

		self.button_sets = button_sets
		self.units = units
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
		for unit_id, unit in enumerate(self.units):
			entry = _UnitButtonsEntry(connected_unit=CodeTypes.ConnectedUnitCodeType.to_value(unit.connected_unit), padding=unit.padding)
			if unit.button_set is not None:
				if not 0 <= unit.button_set < len(self.button_sets):
					raise PyMSError('Save', f'Unit {unit_id} uses button set {unit.button_set}, which does not exist')
				# An empty button set is saved the same as no button set
				entry.button_count = len(self.button_sets[unit.button_set])
				if entry.button_count:
					entry.first_button = set_offsets[unit.button_set]
			entries += entry.pack()
		data = _HEADER.pack([button_count, len(self.units), len(self.stat_info)]) + buttons + entries
		for info in self.stat_info:
			data += info.pack()
		with IO.OutputBytes(output) as f:
			f.write(bytes(data))

	def add_button_set(self, buttons: list[Button] | None = None) -> int:
		self.button_sets.append(buttons if buttons is not None else [])
		return len(self.button_sets) - 1

	def units_using_button_set(self, set_id: int) -> list[int]:
		return [unit_id for unit_id, unit in enumerate(self.units) if unit.button_set == set_id]

	def remove_button_set(self, set_id: int) -> list[Button]:
		if not 0 <= set_id < len(self.button_sets):
			raise PyMSError('Internal', f'Button set {set_id} does not exist')
		if users := self.units_using_button_set(set_id):
			raise PyMSError('Internal', f"Button set {set_id} can't be removed because it is used by unit(s) {', '.join(str(unit_id) for unit_id in users)}")
		buttons = self.button_sets.pop(set_id)
		for unit in self.units:
			if unit.button_set is not None and unit.button_set > set_id:
				unit.button_set -= 1
		return buttons

	def set_unit_count(self, count: int) -> None:
		if count < len(self.units):
			del self.units[count:]
		else:
			self.units.extend(UnitButtons() for _ in range(count - len(self.units)))

	def set_stat_count(self, count: int) -> None:
		if count < len(self.stat_info):
			del self.stat_info[count:]
		else:
			self.stat_info.extend(StatInfo(unit_id) for unit_id in range(len(self.stat_info), count))

	@staticmethod
	def _button_block(button: Button) -> StructBlock:
		commands: list[CodeCommand] = [CodeCommands.ButtonIcon.create([button.icon])]
		if 0 <= button.condition < len(CodeCommands.condition_commands):
			commands.append(CodeCommands.condition_commands[button.condition].create_with_param(button.condition_param))
		else:
			commands.append(CodeCommands.RawCondition.create([button.condition, button.condition_param]))
		if 0 <= button.action < len(CodeCommands.action_commands):
			commands.append(CodeCommands.action_commands[button.action].create_with_param(button.action_param))
		else:
			commands.append(CodeCommands.RawAction.create([button.action, button.action_param]))
		commands.append(CodeCommands.ButtonEnabledString.create([button.enabled_string]))
		commands.append(CodeCommands.ButtonDisabledString.create([button.disabled_string]))
		return StructBlock(CodeCommands.ButtonBlock, [button.position], commands)

	@staticmethod
	def _function_value(block: StructBlock, field: StructField) -> tuple[int, int]:
		# The function index and parameter of a condition or action
		command = block.get(field)
		assert command is not None
		if isinstance(command.definition, ButtonFunctionCommandDefinition):
			return (command.definition.function_index, command.definition.param_value(command))
		return (command.params[0], command.params[1])

	@staticmethod
	def _button(block: StructBlock) -> Button:
		condition, condition_param = ButtonsGraft._function_value(block, CodeCommands.ButtonConditionField)
		action, action_param = ButtonsGraft._function_value(block, CodeCommands.ButtonActionField)
		return Button(
			position=block.header_params[0],
			icon=block.param(CodeCommands.ButtonIcon),
			condition=condition,
			condition_param=condition_param,
			action=action,
			action_param=action_param,
			enabled_string=block.param(CodeCommands.ButtonEnabledString),
			disabled_string=block.param(CodeCommands.ButtonDisabledString),
		)

	def decompile(self, serialize_context: GraftSerializeContext) -> None:
		for set_id, buttons in enumerate(self.button_sets):
			StructBlock(CodeCommands.ButtonSetBlock, [set_id], children=[ButtonsGraft._button_block(button) for button in buttons]).serialize(serialize_context)
			serialize_context.write('\n')
		for unit_id, unit in enumerate(self.units):
			commands: list[CodeCommand] = [
				CodeCommands.UnitButtonSet.create([unit.button_set]),
				CodeCommands.UnitConnectedUnit.create([unit.connected_unit]),
			]
			if unit_id < len(self.stat_info):
				info = self.stat_info[unit_id]
				params = [info.status_function, info.display_function]
				if info.debug_unit_id != unit_id:
					params.append(info.debug_unit_id)
				commands.append(CodeCommands.UnitStatInfo.create(params))
			if unit.padding:
				commands.append(CodeCommands.UnitPadding.create([unit.padding]))
			StructBlock(CodeCommands.UnitBlock, [unit_id], commands).serialize(serialize_context)
			serialize_context.write('\n')

	@staticmethod
	def compile(parse_context: GraftParseContext) -> ButtonsGraft:
		if not isinstance(parse_context.language, ButtonsLanguage):
			raise PyMSError('Internal', f'ButtonsGraft must be compiled with a parse context using `{ButtonsLanguage.__name__}`')
		button_sets: dict[int, list[Button]] = {}
		units: dict[int, UnitButtons] = {}
		stat_info: dict[int, StatInfo] = {}
		header_lines: dict[tuple[str, int], int] = {}
		for block in parse_struct_blocks(parse_context, (CodeCommands.ButtonSetBlock, CodeCommands.UnitBlock)):
			definition = block.definition
			entry_id: int = block.header_params[0]
			assert block.line is not None
			if (definition.keyword, entry_id) in header_lines:
				raise parse_context.error('Parse', f'{definition.title(block.header_params)} is already defined on line {header_lines[(definition.keyword, entry_id)] + 1}', line=block.line)
			header_lines[(definition.keyword, entry_id)] = block.line
			if definition is CodeCommands.ButtonSetBlock:
				button_sets[entry_id] = [ButtonsGraft._button(child) for child in block.children]
				continue
			units[entry_id] = UnitButtons(block.param(CodeCommands.UnitButtonSet), block.param(CodeCommands.UnitConnectedUnit), block.param(CodeCommands.UnitPadding, 0))
			if command := block.find(CodeCommands.UnitStatInfo):
				params = command.params
				stat_info[entry_id] = StatInfo(params[2] if len(params) > 2 else entry_id, params[0], params[1])

		buttons_graft = ButtonsGraft()
		set_count = max(button_sets.keys()) + 1 if button_sets else 0
		buttons_graft.button_sets = [button_sets.get(set_id, []) for set_id in range(set_count)]
		unit_count = max(units.keys()) + 1 if units else 0
		buttons_graft.units = [units.get(unit_id, UnitButtons()) for unit_id in range(unit_count)]
		unit_title = CodeCommands.UnitBlock.title
		for unit_id, unit in enumerate(buttons_graft.units):
			if unit.button_set is not None and unit.button_set >= set_count:
				line = header_lines[(CodeCommands.UnitBlock.keyword, unit_id)]
				raise PyMSError('Parse', f'{unit_title([unit_id])} uses button set {unit.button_set}, which is not defined', line=line, code=parse_context.lexer.get_line_of_code(line))
		# Stat info is a table for units 0 up to the last unit with `stat_info`, so it can't have gaps
		stat_count = max(stat_info.keys()) + 1 if stat_info else 0
		stat_info_name = CodeCommands.UnitStatInfo.name
		for unit_id in range(stat_count):
			if unit_id not in stat_info:
				raise PyMSError('Parse', f'{unit_title([unit_id])} is missing `{stat_info_name}` (every unit up to the last unit with `{stat_info_name}` needs it)')
		buttons_graft.stat_info = [stat_info[unit_id] for unit_id in range(stat_count)]
		parse_context.finalize()
		return buttons_graft

	def import_fgp(self, fgp: FGP) -> list[PyMSWarning]:
		# Lays the FireGraft project's buttons over the current buttons
		warnings: list[PyMSWarning] = []
		for set_id, buttons in fgp.button_sets.items():
			while set_id >= len(self.button_sets):
				self.button_sets.append([])
			self.button_sets[set_id] = [button.copy() for button in buttons]
		for fg_unit in fgp.units:
			if fg_unit.unit_id >= len(self.units):
				warnings.append(PyMSWarning(warn_type='Import', warning=f'FireGraft unit {fg_unit.unit_id} is past the last unit with buttons ({len(self.units) - 1}) and was skipped'))
				continue
			if fg_unit.button_set is not None and fg_unit.button_set >= len(self.button_sets):
				warnings.append(PyMSWarning(warn_type='Import', warning=f'FireGraft unit {fg_unit.unit_id} uses button set {fg_unit.button_set}, which does not exist, so it was set to no button set'))
				button_set = None
			else:
				button_set = fg_unit.button_set
			self.units[fg_unit.unit_id] = UnitButtons(button_set, CodeTypes.ConnectedUnitCodeType.from_value(fg_unit.connected_unit))
			if fg_unit.stat_info is not None:
				if fg_unit.unit_id >= len(self.stat_info):
					warnings.append(PyMSWarning(warn_type='Import', warning=f'FireGraft unit {fg_unit.unit_id} is past the last unit with stat info ({len(self.stat_info) - 1}), so its stat info was skipped'))
				else:
					self.stat_info[fg_unit.unit_id] = fg_unit.stat_info
		return warnings
