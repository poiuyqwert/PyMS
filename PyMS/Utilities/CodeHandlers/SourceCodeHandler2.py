
from __future__ import annotations

from . import Tokens

from ..PyMSError import PyMSError

from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
	from .CodeCommand import CodeCommand, CodeCommandDefinition
	from .CodeDirective import CodeDirectiveDefinition
	from .ParseContext import ParseContext, BlockMetadata

class SourceCodeParser(Protocol):
	def handles_token(self, token: Tokens.Token, parse_context: ParseContext) -> bool:
		...

	def parse(self, parse_context: ParseContext) -> Tokens.Token | None:
		...

	def finalize(self, parse_context: ParseContext) -> None:
		...

class BasicSourceCodeParser(SourceCodeParser):
	def __init__(self) -> None:
		self.cmd_defs: dict[str, CodeCommandDefinition] = {}
		self.directive_defs: dict[str, CodeDirectiveDefinition] = {}

	def register_command(self, cmd_def: CodeCommandDefinition) -> None:
		if cmd_def.name in self.cmd_defs:
			raise PyMSError('Internal', "Command with name '%s' already exists" % cmd_def.name)
		self.cmd_defs[cmd_def.name] = cmd_def

	def register_commands(self, cmd_defs: list[CodeCommandDefinition]) -> None:
		for cmd_def in cmd_defs:
			self.register_command(cmd_def)

	def register_directive(self, directive_def: CodeDirectiveDefinition) -> None:
		if directive_def.name in self.directive_defs:
			raise PyMSError('Internal', f"Directive with name '{directive_def.name}' already exists")
		self.directive_defs[directive_def.name] = directive_def

	def register_directives(self, directive_defs: list[CodeDirectiveDefinition]) -> None:
		for directive_def in directive_defs:
			self.register_directive(directive_def)

	def handles_token(self, token: Tokens.Token, parse_context: ParseContext) -> bool:
		return True

	def parse(self, parse_context: ParseContext) -> Tokens.Token | None:
		from .CodeBlock import CodeBlock
		while True:
			token = parse_context.lexer.next_token()
			if isinstance(token, Tokens.EOFToken):
				break
			if isinstance(token, Tokens.LiteralsToken) and token.raw_value == '@':
				self.parse_directive(parse_context)
				continue
			if isinstance(token, Tokens.LiteralsToken) and (token.raw_value == ':' or token.raw_value == '--'):
				hyphens = (token.raw_value == '--')
				token = parse_context.lexer.next_token()
				if not isinstance(token, Tokens.IdentifierToken):
					raise parse_context.error('Parse', "Expected block name, got '%s' instead" % token.raw_value)
				name = token.raw_value
				line = parse_context.lexer.line
				metadata = parse_context.lookup_block_metadata_by_name(name)
				if metadata is not None:
					raise parse_context.error('Parse', "A block named '%s' is already defined on line %d" % (name, metadata.source_line))
				token = parse_context.lexer.next_token()
				if hyphens:
					if not isinstance(token, Tokens.LiteralsToken) or token.raw_value != '--':
						raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected `--` to end the block name)")
					token = parse_context.lexer.next_token()
				if not isinstance(token, Tokens.NewlineToken):
					raise parse_context.error('Parse', "Unexpected token '%s' (expected end of line)" % token.raw_value)
				block = CodeBlock()
				if parse_context.active_block:
					parse_context.active_block.next_block = block
					block.prev_block = parse_context.active_block
				parse_context.active_block = block
				parse_context.define_block(block, BlockMetadata(name, line))
				parse_context.next_line()
				continue
			if isinstance(token, Tokens.IdentifierToken):
				command = self.parse_command(token, parse_context)
				if not parse_context.active_block:
					raise parse_context.error('Parse', "'%s' command defined outside of any block" % command.definition.name)
				parse_context.active_block.commands.append(command)
				if command.definition.ends_flow:
					parse_context.active_block = None
				parse_context.next_line()
				continue
			if isinstance(token, Tokens.NewlineToken):
				continue
			return token
		return None

	def finalize(self, parse_context: ParseContext) -> None:
		if parse_context.active_block:
			block_metadata = parse_context.lookup_block_metadata(parse_context.active_block)
			assert block_metadata is not None
			raise parse_context.error('Parse', "The last block (named '%s') does not end" % block_metadata.name, line=block_metadata.source_line)

	def parse_command(self, identifier: Tokens.IdentifierToken, parse_context: ParseContext) -> CodeCommand:
		if not identifier.raw_value in self.cmd_defs:
			raise parse_context.error('Parse', "Unknown command '%s'" % identifier.raw_value)
		cmd_def = self.cmd_defs[identifier.raw_value]
		return cmd_def.parse(parse_context)

	def parse_directive(self, parse_context: ParseContext) -> None:
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IdentifierToken):
			raise parse_context.error('Parse', "Expected directive name, got '%s' instead" % token.raw_value)
		if not token.raw_value in self.directive_defs:
			raise parse_context.error('Parse', "Unknown directive '%s'" % token.raw_value)
		directive_def = self.directive_defs[token.raw_value]
		directive = directive_def.parse(parse_context)
		parse_context.handle_directive(directive)

class SourceCodeHandler2:
	def __init__(self) -> None:
		self.parsers: list[SourceCodeParser] = []

	def register_parser(self, parser: SourceCodeParser) -> None:
		self.parsers.append(parser)

	def parse(self, parse_context: ParseContext) -> None:
		continue_token: Tokens.Token | None = None
		while True:
			if continue_token is not None:
				token = continue_token
			else:
				token = parse_context.lexer.next_token()
			if isinstance(token, Tokens.EOFToken):
				break
			error: PyMSError | None = None
			for parser in self.parsers:
				if parser.handles_token(token, parse_context):
					try:
						continue_token = parser.parse(parse_context)
						error = None
						break
					except PyMSError as e:
						if error is None:
							error = e
			else:
				if error:
					raise error
				raise parse_context.error('Parse', "Unexpected token '%s'" % token.raw_value)
			if parse_context.lexer.is_at_end():
				break
		for parser in self.parsers:
			parser.finalize(parse_context)
