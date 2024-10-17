
from __future__ import annotations

from ....Utilities.CodeHandlers.SourceCodeParser import SourceCodeParser
from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers import Tokens

class ICEBlockSourceCodeParser(SourceCodeParser):
	def parse(self, parse_context: ParseContext) -> bool:
		token = parse_context.lexer.skip(Tokens.NewlineToken)
		if isinstance(token, Tokens.EOFToken):
			return True
		if not isinstance(token, Tokens.IdentifierToken):
			return False
		name = token.raw_value
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.LiteralsToken) or not token.raw_value == ':':
			return False
		block = parse_context.define_block(name, parse_context.lexer.state.line)
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.NewlineToken):
			raise parse_context.error('Parse', "Unexpected token '%s' (expected end of line)" % token.raw_value)
		if parse_context.active_block:
			parse_context.active_block.next_block = block
			block.prev_block = parse_context.active_block
		parse_context.active_block = block
		parse_context.next_line()
		return True
