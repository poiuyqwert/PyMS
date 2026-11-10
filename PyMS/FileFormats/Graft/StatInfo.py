from __future__ import annotations

from .CodeHandlers import StatInfoCodeCommands
from .CodeHandlers.GraftCommandDefinition import GraftCommandDefinition

from ...Utilities.CodeHandlers.CodeCommand import CodeCommand
from ...Utilities.CodeHandlers.CodeStruct import StructBlock, StructField
from ...Utilities import Struct

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

	def find_unknown_function(self) -> str | None:
		# Every unit must use a known status and display function, since they're written by name
		if not 0 <= self.status_function < len(StatInfoCodeCommands.status_function_commands):
			return f'unknown status function {self.status_function}'
		if not 0 <= self.display_function < len(StatInfoCodeCommands.display_function_commands):
			return f'unknown display function {self.display_function}'
		return None

	def to_block(self, unit_id: int) -> StructBlock:
		return StructBlock(StatInfoCodeCommands.UnitStatInfoBlock, [unit_id], [
			CodeCommand(StatInfoCodeCommands.DebugID, [self.debug_unit_id]),
			CodeCommand(StatInfoCodeCommands.status_function_commands[self.status_function], []),
			CodeCommand(StatInfoCodeCommands.display_function_commands[self.display_function], []),
		])

	@staticmethod
	def _function_index(block: StructBlock, struct_field: StructField) -> int:
		# The function index of a status or display function
		command = block.get(struct_field)
		assert command is not None and isinstance(command.definition, GraftCommandDefinition)
		return command.definition.function_index

	@classmethod
	def from_block(cls, block: StructBlock, unit_id: int) -> StatInfo:
		# The debug ID defaults to the unit itself
		status_function = cls._function_index(block, StatInfoCodeCommands.UnitStatusFunctionField)
		display_function = cls._function_index(block, StatInfoCodeCommands.UnitDisplayFunctionField)
		return cls(block.param(StatInfoCodeCommands.DebugID, unit_id), status_function, display_function)
