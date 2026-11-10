from __future__ import annotations

from .Buttons import Button, ButtonSet, ButtonCard
from .StatInfo import StatInfo
from .CodeHandlers import CodeTypes
from .CodeHandlers import ButtonCodeCommands
from .CodeHandlers import StatInfoCodeCommands
from .CodeHandlers.GraftParseContext import GraftParseContext
from .CodeHandlers.GraftSerializeContext import GraftSerializeContext

from ...Utilities.CodeHandlers.CodeStruct import parse_struct_blocks
from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities import Struct
from ...Utilities import Assets
from ...Utilities import IO

import os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .FGP import FGP

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

	def __init__(self, button_count: int = 0, first_button: int = 0, connected_unit: int = CodeTypes.ConnectedUnitCodeType.NONE_VALUE, padding: int = 0) -> None:
		self.button_count = button_count
		self.first_button = first_button
		self.connected_unit = connected_unit
		self.padding = padding

_HEADER = Struct.l_au32(3)

class ButtonsGraft:
	# Default filename for the file
	FILE_NAME = 'Buttons.graft'
	# Path the Graft Hook loads the file from in an MPQ
	MPQ_PATH = 'datreq\\Buttons.graft'

	# Default table sizes of the vanilla game
	DEFAULT_BUTTON_CARD_COUNT = 250 # The units, plus the special button cards for groups, builder pages, replays, etc.
	DEFAULT_STAT_COUNT = 228
	# The first button card after the units (their names are in `Assets.DataReference.ButtonCards`), which aren't units but have `unit` buttons entries
	SPECIAL_BUTTON_CARDS_START = 228

	def __init__(self) -> None:
		self.button_sets: list[ButtonSet] = []
		self.button_cards: list[ButtonCard] = [ButtonCard() for _ in range(ButtonsGraft.DEFAULT_BUTTON_CARD_COUNT)]
		self.stat_info: list[StatInfo] = [StatInfo(unit_id) for unit_id in range(ButtonsGraft.DEFAULT_STAT_COUNT)]

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
		button_sets: list[ButtonSet] = []
		set_lookup: dict[tuple[int, int], int] = {}
		cursor = 0
		for first, count in sorted(set((entry.first_button, entry.button_count) for entry in entries if entry.button_count)):
			if first < cursor:
				warnings.append(PyMSWarning(warn_type='Load', warning=f'Buttons {first} to {first + count - 1} overlap another button set, they will be saved as a separate button set'))
			else:
				if first > cursor:
					button_sets.append(ButtonSet(buttons[cursor:first]))
				cursor = first + count
			set_lookup[(first, count)] = len(button_sets)
			button_sets.append(ButtonSet(buttons[first:first + count]).copy())
		if cursor < button_count:
			button_sets.append(ButtonSet(buttons[cursor:]))

		button_cards: list[ButtonCard] = []
		for entry in entries:
			button_set = set_lookup[(entry.first_button, entry.button_count)] if entry.button_count else None
			button_cards.append(ButtonCard(button_set, CodeTypes.ConnectedUnitCodeType.from_value(entry.connected_unit)))
		if padded_cards := [card_id for card_id, entry in enumerate(entries) if entry.padding]:
			warnings.append(PyMSWarning(warn_type='Load', warning=f"Button card(s) {', '.join(str(card_id) for card_id in padded_cards)} have unused data after their connected unit, it will be discarded"))

		for set_id, loaded_set in enumerate(button_sets):
			ButtonsGraft._check_button_set(set_id, loaded_set, 'Load')
		for unit_id, info in enumerate(stat_info):
			ButtonsGraft._check_stat_info(unit_id, info, 'Load')

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
			for button in button_set.buttons:
				buttons += button.pack()
			button_count += len(button_set.buttons)
		entries = bytearray()
		for card_id, card in enumerate(self.button_cards):
			entry = _ButtonCardEntry(connected_unit=CodeTypes.ConnectedUnitCodeType.to_value(card.connected_unit))
			if card.button_set is not None:
				if not 0 <= card.button_set < len(self.button_sets):
					raise PyMSError('Save', f'Button card {card_id} uses button set {card.button_set}, which does not exist')
				# An empty button set is saved the same as no button set
				entry.button_count = len(self.button_sets[card.button_set].buttons)
				if entry.button_count:
					entry.first_button = set_offsets[card.button_set]
			entries += entry.pack()
		data = _HEADER.pack([button_count, len(self.button_cards), len(self.stat_info)]) + buttons + entries
		for info in self.stat_info:
			data += info.pack()
		with IO.OutputBytes(output) as f:
			f.write(bytes(data))

	def add_button_set(self, button_set: ButtonSet | None = None) -> int:
		self.button_sets.append(button_set if button_set is not None else ButtonSet())
		return len(self.button_sets) - 1

	def set_button_set(self, set_id: int, button_set: ButtonSet) -> None:
		if not 0 <= set_id < len(self.button_sets):
			raise PyMSError('Internal', f'Button set {set_id} does not exist')
		self.button_sets[set_id] = button_set

	def button_cards_using_button_set(self, set_id: int) -> list[int]:
		return [card_id for card_id, card in enumerate(self.button_cards) if card.button_set == set_id]

	def remove_button_set(self, set_id: int) -> ButtonSet:
		if not 0 <= set_id < len(self.button_sets):
			raise PyMSError('Internal', f'Button set {set_id} does not exist')
		if users := self.button_cards_using_button_set(set_id):
			raise PyMSError('Internal', f"Button set {set_id} can't be removed because it is used by button card(s) {', '.join(str(card_id) for card_id in users)}")
		button_set = self.button_sets.pop(set_id)
		for card in self.button_cards:
			if card.button_set is not None and card.button_set > set_id:
				card.button_set -= 1
		return button_set

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
	def _check_button_set(set_id: int, button_set: ButtonSet, error_type: str) -> None:
		if problem := button_set.find_unknown_function():
			raise PyMSError(error_type, f'Button set {set_id} uses {problem}')

	@staticmethod
	def _check_stat_info(unit_id: int, info: StatInfo, error_type: str) -> None:
		if problem := info.find_unknown_function():
			raise PyMSError(error_type, f'Unit {unit_id} uses {problem}')

	def decompile(self, serialize_context: GraftSerializeContext) -> None:
		for set_id, button_set in enumerate(self.button_sets):
			button_set.to_block(set_id).serialize(serialize_context)
			serialize_context.write('\n')
		for card_id, card in enumerate(self.button_cards):
			card.to_block(card_id).serialize(serialize_context)
			serialize_context.write('\n')
		for unit_id, info in enumerate(self.stat_info):
			info.to_block(unit_id).serialize(serialize_context)
			serialize_context.write('\n')

	def decompile_button_set(self, serialize_context: GraftSerializeContext, set_id: int) -> None:
		# Only the buttons of the button set (the body of its `button_set` block)
		if not 0 <= set_id < len(self.button_sets):
			raise PyMSError('Decompile', f'Button set {set_id} does not exist')
		self.button_sets[set_id].serialize(serialize_context)

	@staticmethod
	def compile(parse_context: GraftParseContext) -> ButtonsGraft:
		ButtonSet.check_language(parse_context)
		button_sets: dict[int, ButtonSet] = {}
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
				button_sets[entry_id] = ButtonSet.from_block(block)
			elif definition is ButtonCodeCommands.ButtonCardBlock:
				button_cards[entry_id] = ButtonCard.from_block(block)
			else:
				stat_info[entry_id] = StatInfo.from_block(block, entry_id)

		buttons_graft = ButtonsGraft()
		set_count = max(button_sets.keys()) + 1 if button_sets else 0
		buttons_graft.button_sets = [button_sets.get(set_id, ButtonSet()) for set_id in range(set_count)]
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
		for set_id, fg_button_set in fgp.button_sets.items():
			ButtonsGraft._check_button_set(set_id, fg_button_set, 'Import')
		for fg_unit in fgp.units:
			if fg_unit.stat_info is not None:
				ButtonsGraft._check_stat_info(fg_unit.unit_id, fg_unit.stat_info, 'Import')
		for set_id, fg_button_set in fgp.button_sets.items():
			while set_id >= len(self.button_sets):
				self.button_sets.append(ButtonSet())
			self.button_sets[set_id] = fg_button_set.copy()
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
