from __future__ import annotations

from . import Tokens
from .CodeCommand import CodeCommandDefinition, CodeCommand
from .CodeType import CodeType
from .ParseContext import ParseContext
from .SourceCodeParser import SourceCodeParser

from ..PyMSError import PyMSError

from typing import TYPE_CHECKING, Any, Callable, Iterator, Sequence
if TYPE_CHECKING:
	from .SerializeContext import SerializeContext

# Struct blocks are a header keyword with parameters, followed by a `{ ... }` body of commands that each set
# a field of the struct (and optionally nested struct blocks), for example:
#
# script TEST {
# 	name_string 0
# 	...
# }

class StructField:
	# A field of a struct block, set by one of `commands` (more than one command makes the field a choice between them)
	def __init__(self, name: str, commands: Sequence[CodeCommandDefinition], *, required: bool = True) -> None:
		self.name = name
		self.commands = commands
		self.required = required

class StructBlockDefinition:
	# `description` names the block in errors (`Unknown {description} command`), and `title_format` is formatted with
	# the header parameters to name a specific block in errors (`{title} is missing '{field}'`)
	def __init__(self, keyword: str, description: str, title_format: str, header_types: Sequence[CodeType], *, fields: Sequence[StructField] = (), children: Sequence[StructBlockDefinition] = ()) -> None:
		self.keyword = keyword
		self.description = description
		self.title_format = title_format
		self.header_types = header_types
		self.fields = fields
		self.children = children
		self._field_lookup: dict[str, tuple[StructField, CodeCommandDefinition]] = {}
		for field in fields:
			for cmd_def in field.commands:
				if cmd_def.name in self._field_lookup:
					raise PyMSError('Internal', f"Command '{cmd_def.name}' is used by more than one field of '{keyword}'")
				self._field_lookup[cmd_def.name] = (field, cmd_def)
		self._child_lookup = {child.keyword: child for child in children}

	def title(self, header_params: Sequence[Any]) -> str:
		return self.title_format.format(*header_params)

	def lookup_field(self, command_name: str) -> tuple[StructField, CodeCommandDefinition] | None:
		return self._field_lookup.get(command_name)

	def lookup_child(self, keyword: str) -> StructBlockDefinition | None:
		return self._child_lookup.get(keyword)

	@staticmethod
	def _parse_header_param(header_type: CodeType, parse_context: ParseContext) -> Any:
		# Header parameters are always literal values (variables are not looked up)
		start = parse_context.lexer.get_rollback()
		try:
			value = header_type.lex(parse_context)
			header_type.validate(value, parse_context, parse_context.lexer.get_raw(from_state=start).strip(' '))
		except PyMSError as e:
			parse_context.attribute_error(e)
			raise
		return value

	# Parses the block after its keyword, up to and including its closing `}` (but not what follows the `}`)
	def parse(self, parse_context: ParseContext) -> StructBlock:
		lexer = parse_context.lexer
		line = lexer.state.token_line
		header_params = [StructBlockDefinition._parse_header_param(header_type, parse_context) for header_type in self.header_types]
		token = lexer.next_token()
		if not isinstance(token, Tokens.SymbolToken) or token.raw_value != '{':
			raise parse_context.error('Parse', f"Expected a '{{' to start the {self.description}, got '{token.raw_value}' instead")
		token = lexer.next_token()
		if not isinstance(token, Tokens.NewlineToken):
			raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected end of line)")
		parse_context.next_line()
		block = StructBlock(self, header_params, line=line)
		while True:
			token = lexer.skip(Tokens.NewlineToken)
			if isinstance(token, Tokens.SymbolToken) and token.raw_value == '}':
				break
			if isinstance(token, Tokens.EOFToken):
				raise parse_context.error('Parse', f"Expected a '}}' to end the {self.description}, got end of file instead")
			if not isinstance(token, Tokens.IdentifierToken):
				raise parse_context.error('Parse', f"Expected a {self.description} command, got '{token.raw_value}' instead")
			if child := self.lookup_child(token.raw_value):
				block.children.append(child.parse(parse_context))
				parse_end_of_line(parse_context)
				continue
			lookup = self.lookup_field(token.raw_value)
			if lookup is None:
				raise parse_context.error('Parse', f"Unknown {self.description} command '{token.raw_value}'")
			field, cmd_def = lookup
			if block.get(field) is not None:
				raise parse_context.error('Parse', f"Duplicate {self.description} command '{token.raw_value}'")
			block.commands.append(cmd_def.parse(parse_context))
			parse_context.next_line()
		for field in self.fields:
			if field.required and block.get(field) is None:
				raise parse_context.error('Parse', f"{self.title(header_params)} is missing '{field.name}'")
		return block

class StructBlock:
	def __init__(self, definition: StructBlockDefinition, header_params: list[Any], commands: list[CodeCommand] | None = None, children: list[StructBlock] | None = None, *, line: int | None = None) -> None:
		self.definition = definition
		self.header_params = header_params
		self.commands = commands if commands is not None else []
		self.children = children if children is not None else []
		self.line = line # Source line of the header, when parsed

	def get(self, field: StructField) -> CodeCommand | None:
		for command in self.commands:
			if command.definition in field.commands:
				return command
		return None

	def find(self, cmd_def: CodeCommandDefinition) -> CodeCommand | None:
		for command in self.commands:
			if command.definition is cmd_def:
				return command
		return None

	def param(self, cmd_def: CodeCommandDefinition, default: Any = None) -> Any:
		# The first parameter of the `cmd_def` command, or `default` if the block doesn't have the command
		command = self.find(cmd_def)
		return command.params[0] if command is not None else default

	def serialize(self, context: SerializeContext) -> None:
		parameters: list[str] = []
		comments: list[str] = []
		for param, header_type in zip(self.header_params, self.definition.header_types):
			parameters.append(header_type.serialize(param, context))
			if (comment := header_type.comment(param, context)) is not None:
				comments.append(comment)
		context.write(context.formatters.command.serialize(self.definition.keyword, parameters) + ' {')
		if comments:
			context.write(context.formatters.comment.serialize(comments))
		context.write('\n')
		context.indent()
		for command in self.commands:
			command.serialize(context)
		for child in self.children:
			child.serialize(context)
		context.dedent()
		context.write('}\n')

def parse_end_of_line(parse_context: ParseContext) -> None:
	token = parse_context.lexer.next_token()
	if not isinstance(token, (Tokens.NewlineToken, Tokens.EOFToken)):
		raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected end of line or file)")
	parse_context.next_line()

def parse_struct_blocks(parse_context: ParseContext, definitions: Sequence[StructBlockDefinition]) -> Iterator[StructBlock]:
	# Parses source code made of only top level struct blocks
	lookup = {definition.keyword: definition for definition in definitions}
	while True:
		token = parse_context.lexer.skip(Tokens.NewlineToken)
		if isinstance(token, Tokens.EOFToken):
			return
		definition = lookup.get(token.raw_value) if isinstance(token, Tokens.IdentifierToken) else None
		if definition is None:
			expected = ' or '.join(f"'{keyword}'" for keyword in lookup)
			raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected {expected})")
		block = definition.parse(parse_context)
		parse_end_of_line(parse_context)
		yield block

class StructSourceCodeParser(SourceCodeParser):
	# Parses a struct block as part of a larger source code, passing it to `handle`
	def __init__(self, definition: StructBlockDefinition, handle: Callable[[ParseContext, StructBlock], None]) -> None:
		self.definition = definition
		self.handle = handle

	def parse(self, parse_context: ParseContext) -> bool:
		token = parse_context.lexer.skip(Tokens.NewlineToken)
		if not isinstance(token, Tokens.IdentifierToken) or token.raw_value != self.definition.keyword:
			return False
		block = self.definition.parse(parse_context)
		parse_end_of_line(parse_context)
		self.handle(parse_context, block)
		return True
