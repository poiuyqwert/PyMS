
from __future__ import annotations

from .SourceCodeParser import SourceCodeParser
from . import Tokens

from ..PyMSError import PyMSError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .ParseContext import ParseContext

class SourceCodeHandler(SourceCodeParser):
	def __init__(self) -> None:
		self.parsers: list[SourceCodeParser] = []

	def register_parser(self, parser: SourceCodeParser) -> None:
		self.parsers.append(parser)

	def register_parsers(self, parsers: list[SourceCodeParser]) -> None:
		for parser in parsers:
			self.register_parser(parser)

	def parse(self, parse_context: ParseContext) -> bool:
		any_parsed = False
		while True:
			error: PyMSError | None = None
			parse_context.lexer.skip((Tokens.WhitespaceToken, Tokens.NewlineToken, Tokens.CommentToken), peek=True)
			rollback = parse_context.lexer.get_rollback()
			for parser in self.parsers:
				try:
					parsed = parser.parse(parse_context)
					if parsed:
						error = None
						any_parsed = True
						break
				except PyMSError as e:
					if error is None or e.level > error.level:
						error = e
				parse_context.lexer.rollback(rollback)
			else:
				if error is not None:
					raise error
				if not parsed:
					parse_context.lexer.rollback(rollback)
					token = parse_context.lexer.next_token()
					raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}'")
			if parse_context.lexer.is_at_end():
				break
		return any_parsed
