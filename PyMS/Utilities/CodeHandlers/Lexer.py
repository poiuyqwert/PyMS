
from __future__ import annotations

from .Tokens import Token, EOFToken, UnknownToken, NewlineToken, StringToken

from ..PyMSError import PyMSError

import re, dataclasses
from typing import Type, TypeVar, Callable
from enum import Enum

__all__ = [
	'Stop',
	'State',
	'Lexer',
]

class Stop(Enum):
	proceed = 0
	exclude = 1
	include = 2

@dataclasses.dataclass
class State:
	offset: int = 0
	line: int = 0

T = TypeVar('T', bound=Token)
class Lexer:
	def __init__(self, code: str) -> None:
		self.code = code
		self._lines_of_code_cache: list[str] | None = None
		self.state = State()
		self.token_types: list[Type[Token]] = []
		self.skip_tokens: list[Type[Token]] = []
		self.rollbacks: list[State] = []

	_newline_regexp = re.compile(r'\r?\n|\r(?!\n)')
	def get_line_of_code(self, line: int) -> str | None:
		if self._lines_of_code_cache is None:
			self._lines_of_code_cache = Lexer._newline_regexp.split(self.code)
		if 0 <= line < len(self._lines_of_code_cache):
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
		if peek:
			# Peeking must be side-effect free: capture the full state and restore
			# it so whitespace/comment skipping and line tracking don't leak out.
			saved_state = dataclasses.replace(self.state)
			try:
				return self._read_token()
			finally:
				self.state = saved_state
		return self._read_token()

	def _read_token(self) -> Token:
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

	# Read all tokens as a string until EOF or the `stop` callback says to stop
	def read_open_string(self, stop: Callable[[Token], Stop]) -> StringToken:
		self._skip()
		start = self.state.offset
		end = self.state.offset
		while True:
			before = dataclasses.replace(self.state)
			token = self._read_token()
			if isinstance(token, EOFToken):
				end = self.state.offset
				break
			should_stop = stop(token)
			if should_stop == Stop.exclude:
				# Leave the terminator (and any whitespace before it) unconsumed.
				self.state = before
				break
			end = self.state.offset
			if should_stop == Stop.include:
				break
		return StringToken(self.code[start:end])

	def skip(self, skip_token_types: Type[Token] | tuple[Type[Token], ...], peek: bool = False) -> Token:
		if not isinstance(skip_token_types, tuple):
			skip_token_types = (skip_token_types,)
		token = self.next_token(peek=peek)
		while isinstance(token, skip_token_types):
			if peek:
				self.next_token()
			token = self.next_token(peek=peek)
		return token

	def drop_token(self) -> None:
		_ = self.next_token()

	def is_at_end(self) -> bool:
		return self.state.offset == len(self.code)

	def get_rollback(self) -> State:
		return dataclasses.replace(self.state)

	def rollback(self, state: State) -> None:
		self.state = dataclasses.replace(state)

	def get_raw(self, from_state: State, to_state: State | None = None) -> str:
		if to_state is None:
			to_state = self.state
		return self.code[from_state.offset:to_state.offset]
