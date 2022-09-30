
from .Lexer import Lexer, IdentifierToken, LiteralsToken, EOFToken, NewlineToken
from .CodeDefs import CodeBlock, CodeCommand

from ..PyMSError import PyMSError

class SourceCodeHandler(object):
	def __init__(self, lexer): # type: (Lexer) -> SourceCodeHandler
		self.lexer = lexer
		self.cmd_defs = {} # type: dict[str, Type[CodeCommand]]
		self.active_block = None # type: (CodeBlock | None)
		self.blocks = {} # type: dict[str, tuple[CodeBlock, int]]

	def register_command(self, cmd_def): # type: (Type[CodeCommand]) -> None
		if cmd_def._name in self.cmd_defs:
			raise PyMSError('Internal', "Command with name '%s' already exists" % cmd_def._name)
		self.cmd_defs[cmd_def._name] = cmd_def

	def parse_custom(self, token):
		return False

	def parse(self):
		while True:
			token = self.lexer.next_token()
			if isinstance(token, EOFToken):
				return
			if self.parse_custom(token):
				continue
			if isinstance(token, LiteralsToken) and token.raw_value == ':':
				token = self.lexer.next_token()
				if not isinstance(token, IdentifierToken):
					raise PyMSError('Parse', "Expected block name, got '%s' instead" % token.raw_value, line=self.lexer.line)
				name = token.raw_value
				line = self.lexer.line
				if name in self.blocks:
					_,existing_line = self.blocks[name]
					raise PyMSError('Parse', "A block named '%s' is already defined on line %d" % (name, existing_line), line=self.lexer.line)
				token = self.lexer.next_token()
				if not isinstance(token, NewlineToken):
					raise PyMSError('Parse', "Unexpected token '%s' (expected end of line)" % token.raw_value, line=self.lexer.line)
				block = CodeBlock()
				if self.active_block:
					self.active_block.next_block = block
					block.prev_block = self.active_block
				self.active_block = block
				self.blocks[name] = (block, line)
				continue
			if isinstance(token, IdentifierToken):
				command = self.parse_command(token)
				if not self.active_block:
					raise PyMSError('Parse', "'%s' command defined outside of any block" % command._name, line=self.lexer.line)
				self.active_block.commands.append(command)
				if command._ends_flow:
					self.active_block = None
				continue
			if isinstance(token, NewlineToken):
				continue
			raise PyMSError('Parse', "Unexpected token '%s' (expected a block or command definition)" % token.raw_value, line=self.lexer.line)

	def parse_command(self, identifier): # type: (IdentifierToken) -> CodeCommand
		if not identifier.raw_value in self.cmd_defs:
			raise PyMSError('Parse', "Unknown command '%s'" % identifier.raw_value, line=self.lexer.line)
		cmd_def = self.cmd_defs[identifier.raw_value]
		return cmd_def.parse(self.lexer)
