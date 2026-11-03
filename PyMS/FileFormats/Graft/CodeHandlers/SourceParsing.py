from __future__ import annotations

from .GraftLexer import GraftLexer

from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers import Tokens

# Helpers for the line based Graft source code: `Header ID:` lines followed by indented body lines

def next_line_token(parse_context: ParseContext) -> Tokens.Token:
	# The first token of the next non-blank line
	parse_context.next_line()
	return parse_context.lexer.skip(Tokens.NewlineToken)

def parse_int(parse_context: ParseContext, what: str) -> int:
	token = parse_context.lexer.next_token()
	try:
		if isinstance(token, Tokens.HexToken):
			return int(token.raw_value, 16)
		if isinstance(token, Tokens.IntegerToken):
			return int(token.raw_value)
	except ValueError:
		pass
	raise parse_context.error('Parse', f'Expected {what} but got `{token.raw_value}`')

def parse_symbol(parse_context: ParseContext, symbol: str) -> None:
	token = parse_context.lexer.next_token()
	if not isinstance(token, GraftLexer.SymbolToken) or token.raw_value != symbol:
		raise parse_context.error('Parse', f'Expected `{symbol}` but got `{token.raw_value}`')

def parse_end_of_line(parse_context: ParseContext) -> None:
	token = parse_context.lexer.next_token()
	if not isinstance(token, (Tokens.NewlineToken, Tokens.EOFToken)):
		raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected end of line)')

def parse_header_id(parse_context: ParseContext, keyword: str, max_id: int) -> int:
	# Parses the `ID:` (and end of line) after a header keyword
	entry_id = parse_int(parse_context, f'a {keyword} ID')
	if entry_id < 0 or entry_id > max_id:
		raise parse_context.error('Parse', f'{keyword} ID `{entry_id}` is out of range (must be 0 to {max_id})')
	parse_symbol(parse_context, ':')
	parse_end_of_line(parse_context)
	return entry_id
