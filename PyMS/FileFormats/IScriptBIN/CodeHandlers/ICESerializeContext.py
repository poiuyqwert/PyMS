
from .DataContext import DataContext

from ....Utilities.CodeHandlers.SerializeContext import SerializeContext
from ....Utilities.CodeHandlers import Formatters

from typing import IO

class TrailingBlockFormatter(Formatters.BlockFormatter):
	def serialize(self, block_name: str) -> str:
		return f'{block_name}:'

class SpacedCommandFormatter(Formatters.CommandFormatter):
	def __init__(self) -> None:
		super().__init__()
		from . import CodeCommands
		self.max_width = max(len(cmd.name) for cmd in CodeCommands.all_basic_commands + CodeCommands.all_header_commands)

	def serialize(self, command_name: str, parameters: list[str]) -> str:
		result = command_name + ' ' * (self.max_width - len(command_name)) + '\t'
		for n, parameter in enumerate(parameters):
			# TODO: Check for space in parameter
			if n > 0:
				result += ' '
			result += f'{parameter}'
		return result

class ICESerializeContext(SerializeContext):
	def __init__(self, output: IO[str], data_context: DataContext) -> None:
		formatters = Formatters.Formatters(
			block=TrailingBlockFormatter(),
			command=SpacedCommandFormatter(),
			indent_bodies=True
		)
		super().__init__(output, formatters=formatters)
		self.data_context = data_context
