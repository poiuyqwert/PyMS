
from typing import Protocol
from dataclasses import dataclass

class BlockFormatter(Protocol):
	def serialize(self, block_name: str) -> str:
		...

class ColonBlockFormatter(BlockFormatter):
	def serialize(self, block_name: str) -> str:
		return f':{block_name}'

class HyphenBlockFormatter(BlockFormatter):
	def serialize(self, block_name: str) -> str:
		return f'--{block_name}--'

class CommandFormatter(Protocol):
	def serialize(self, command_name: str, parameters: list[str]) -> str:
		...

class FlatCommandFormatter(CommandFormatter):
	def serialize(self, command_name: str, parameters: list[str]) -> str:
		result = command_name
		for parameter in parameters:
			# TODO: Check for space in parameter
			result += f' {parameter}'
		return result

class ParensCommandFormatter(CommandFormatter):
	def serialize(self, command_name: str, parameters: list[str]) -> str:
		result = f'{command_name}('
		add_comma = False
		for parameter in parameters:
			if add_comma:
				result += ', '
			add_comma = True
			result += parameter
		result += ')'
		return result

class CommentFormatter(Protocol):
	def symbol(self) -> str:
		...

	def serialize(self, comments: list[str]) -> str:
		...

class HashCommentFormatter(CommentFormatter):
	def symbol(self) -> str:
		return '#'

	def serialize(self, comments: list[str]) -> str:
		return f'\t# {", ".join(comments)}'

class SemicolonCommentFormatter(CommentFormatter):
	def symbol(self) -> str:
		return ';'

	def serialize(self, comments: list[str]) -> str:
		return f'\t; {", ".join(comments)}'

@dataclass
class Formatters:
	block: BlockFormatter = ColonBlockFormatter()
	command: CommandFormatter = FlatCommandFormatter()
	comment: CommentFormatter = HashCommentFormatter()
	indent_bodies: bool = False
