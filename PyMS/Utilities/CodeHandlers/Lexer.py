
from __future__ import annotations

from .Tokens import Token, EOFToken, UnknownToken, NewlineToken, StringToken

from ..PyMSError import PyMSError

from typing import Type, TypeVar, Callable

T = TypeVar('T', bound=Token)
class Lexer(object):
	def __init__(self, code: str) -> None:
		self.code = code
		self.offset = 0
		self.line = 0 # TODO: PyMSError currently expects 0-indexed lines and reports them as 1-indexed
		self.token_types: list[Type[Token]] = []
		self.skip_tokens: list[Type[Token]] = []

	def register_token_type(self, token_type: Type[Token], skip: bool = False) -> None:
		self.token_types.append(token_type)
		if skip:
			self.skip_tokens.append(token_type)

	def next_token(self) -> Token:
		token: Token | None = None
		while not token:
			if self.offset == len(self.code):
				return EOFToken()
			for token_type in self.token_types:
				token = token_type.match(self.code, self.offset)
				if token:
					break
			if not token:
				token = UnknownToken.match(self.code, self.offset)
				if not token:
					raise PyMSError('Parse', 'Could not match token')
			if token:
				self.offset += len(token.raw_value)
				if isinstance(token, NewlineToken):
					self.line += 1
				if type(token) in self.skip_tokens:
					token = None
		return token

	def get_token(self, token_type: Type[T]) -> T:
		if self.offset == len(self.code):
			raise PyMSError('Parse', 'End of file')
		while True:
			for skip_token_type in self.skip_tokens:
				skip_token = skip_token_type.match(self.code, self.offset)
				if skip_token:
					self.offset += len(skip_token.raw_value)
					break
			else:
				break
		token = token_type.match(self.code, self.offset)
		if not token:
			# token = UnknownToken.match(self.code, self.offset)
			# if not token:
			raise PyMSError('Parse', 'Could not match token')
		self.offset += len(token.raw_value)
		return token

	# Read all tokens as a string until EOF or the `stop` callback returns `True`
	def read_open_string(self, stop: Callable[[Token], bool]) -> StringToken:
		raw_string = ''
		while True:
			token = self.next_token()
			if isinstance(token, EOFToken) or stop(token):
				break
			raw_string += token.raw_value
		from .CodeType import StrCodeType
		from .ParseContext import ParseContext
		return StringToken(StrCodeType.parse_string(raw_string))
