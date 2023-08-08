
from __future__ import annotations

from . import Tokens

from ..PyMSError import PyMSError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .CodeBlock import CodeBlock
	from .CodeCommand import CodeCommand, CodeCommandDefinition
	from .ParseContext import ParseContext
	from .Lexer import Lexer

class SourceCodeHandler(object):
	def __init__(self, lexer: Lexer) -> None:
		self.lexer = lexer
		self.cmd_defs: dict[str, CodeCommandDefinition] = {}
		self.active_block: CodeBlock | None = None

	def register_command(self, cmd_def: CodeCommandDefinition) -> None:
		if cmd_def.name in self.cmd_defs:
			raise PyMSError('Internal', "Command with name '%s' already exists" % cmd_def.name)
		self.cmd_defs[cmd_def.name] = cmd_def

	def parse_custom(self, token: Tokens.Token, parse_context: ParseContext) -> bool:
		return False

	def parse(self, parse_context: ParseContext) -> None:
		from .CodeBlock import CodeBlock
		while True:
			token = self.lexer.next_token()
			if isinstance(token, Tokens.EOFToken):
				break
			if self.parse_custom(token, parse_context):
				continue
			if isinstance(token, Tokens.LiteralsToken) and (token.raw_value == ':' or token.raw_value == '--'):
				hyphens = (token.raw_value == '--')
				token = self.lexer.next_token()
				if not isinstance(token, Tokens.IdentifierToken):
					raise PyMSError('Parse', "Expected block name, got '%s' instead" % token.raw_value, line=self.lexer.line)
				name = token.raw_value
				line = self.lexer.line
				existing_line = parse_context.lookup_block_source_line(name)
				if existing_line is not None:
					raise PyMSError('Parse', "A block named '%s' is already defined on line %d" % (name, existing_line), line=self.lexer.line)
				token = self.lexer.next_token()
				if hyphens:
					if not isinstance(token, Tokens.LiteralsToken) or token.raw_value != '--':
						raise PyMSError('Parse', f"Unexpected token '{token.raw_value}' (expected `--` to end the block name)", line=self.lexer.line)
					token = self.lexer.next_token()
				if not isinstance(token, Tokens.NewlineToken):
					raise PyMSError('Parse', "Unexpected token '%s' (expected end of line)" % token.raw_value, line=self.lexer.line)
				block = CodeBlock()
				if self.active_block:
					self.active_block.next_block = block
					block.prev_block = self.active_block
				self.active_block = block
				parse_context.define_block(name, block, line)
				continue
			if isinstance(token, Tokens.IdentifierToken):
				command = self.parse_command(token, parse_context)
				if not self.active_block:
					raise PyMSError('Parse', "'%s' command defined outside of any block" % command.definition.name, line=self.lexer.line)
				self.active_block.commands.append(command)
				if command.definition.ends_flow:
					self.active_block = None
				continue
			if isinstance(token, Tokens.NewlineToken):
				continue
			raise PyMSError('Parse', "Unexpected token '%s' (expected a block or command definition)" % token.raw_value, line=self.lexer.line)
		if self.active_block:
			block_name = parse_context.lookup_block_name(self.active_block)
			assert block_name is not None
			raise PyMSError('Parse', "The last block (named '%s') does not end" % block_name, line=parse_context.lookup_block_source_line(block_name))

	def parse_command(self, identifier: Tokens.IdentifierToken, parse_context: ParseContext) -> CodeCommand:
		if not identifier.raw_value in self.cmd_defs:
			raise PyMSError('Parse', "Unknown command '%s'" % identifier.raw_value, line=self.lexer.line)
		cmd_def = self.cmd_defs[identifier.raw_value]
		return cmd_def.parse(self.lexer, parse_context)
