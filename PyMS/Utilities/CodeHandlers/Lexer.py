
from __future__ import annotations

from .Tokens import Token, EOFToken, UnknownToken, NewlineToken, StringToken

from ..PyMSError import PyMSError

import re, dataclasses
from typing import Type, TypeVar, Callable
from enum import Enum

class Stop(Enum):
	proceed = 0
	exclude = 1
	include = 2

@dataclasses.dataclass
class State:
	offset: int = 0
	line: int = 0

T = TypeVar('T', bound=Token)
class Lexer(object):
	def __init__(self, code: str) -> None:
		self.code = code
		self._lines_of_code_cache: list[str] | None = None
		self.state = State()
		self.token_types: list[Type[Token]] = []
		self.skip_tokens: list[Type[Token]] = []
		self.rollbacks: list[State] = []

	_newline_regexp = re.compile(r'\r?\n|\r(?!=\n)')
	def get_line_of_code(self, line: int) -> str | None:
		if self._lines_of_code_cache is None:
			self._lines_of_code_cache = Lexer._newline_regexp.split(self.code)
		if line >= 0 and line < len(self._lines_of_code_cache):
			return self._lines_of_code_cache[line]
		return None

	def register_token_type(self, token_type: Type[Token], skip: bool = False) -> None:
		self.token_types.append(token_type)
		if skip:
			self.skip_tokens.append(token_type)

	def _check_token(self, token: Token) -> None:
		if isinstance(token, NewlineToken):
			self.state.line += token.newline_count()

	def _skip(self, dont_skip: Type[Token] | None = None) -> None:
		while True:
			if self.is_at_end():
				return
			for skip_token_type in self.skip_tokens:
				if skip_token_type == dont_skip:
					continue
				skip_token = skip_token_type.match(self.code, self.state.offset)
				if skip_token:
					self._check_token(skip_token)
					self.state.offset += len(skip_token.raw_value)
					break
			else:
				break

	def next_token(self, peek: bool = False) -> Token:
		self._skip()
		token: Token | None = None
		while not token:
			if self.is_at_end():
				return EOFToken()
			for token_type in self.token_types:
				token = token_type.match(self.code, self.state.offset)
				if token:
					break
			if not token:
				token = UnknownToken.match(self.code, self.state.offset)
				if not token:
					raise PyMSError('Parse', 'Could not match token')
			if token:
				if not peek:
					self.state.offset += len(token.raw_value)
					self._check_token(token)
				if type(token) in self.skip_tokens:
					token = None
		return token

	def get_token(self, token_type: Type[T]) -> T | None:
		self._skip(dont_skip=token_type)
		if self.is_at_end():
			return None
		token = token_type.match(self.code, self.state.offset)
		if not token:
			return None
		self._check_token(token)
		self.state.offset += len(token.raw_value)
		return token

	def check_token(self, token_type: Type[T]) -> Token:
		self._skip(dont_skip=token_type)
		if self.is_at_end():
			return EOFToken()
		token: Token | None = token_type.match(self.code, self.state.offset)
		if token:
			self._check_token(token)
			self.state.offset += len(token.raw_value)
		else:
			token = self.next_token()
		return token

	# Read all tokens as a string until EOF or the `stop` callback returns `True`
	def read_open_string(self, stop: Callable[[Token], Stop]) -> StringToken:
		raw_string = ''
		while True:
			token = self.next_token(peek=True)
			if isinstance(token, EOFToken):
				break
			should_stop = stop(token)
			if should_stop != Stop.exclude:
				self.next_token()
			if should_stop != Stop.proceed:
				if should_stop == Stop.include:
					raw_string += token.raw_value
				break
			raw_string += token.raw_value
		return StringToken(raw_string)

	def skip(self, skip_token_types: Type[Token] | tuple[Type[Token], ...]) -> Token:
		if not isinstance(skip_token_types, tuple):
			skip_token_types = (skip_token_types,)
		token = self.next_token()
		while isinstance(token, skip_token_types):
			token = self.next_token()
		return token

	def drop_token(self) -> None:
		_ = self.next_token()

	def is_at_end(self) -> bool:
		return self.state.offset == len(self.code)

	def get_rollback(self) -> State:
		return dataclasses.replace(self.state)

	def rollback(self, state: State) -> None:
		self.state = dataclasses.replace(state)
