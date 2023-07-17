
from __future__ import annotations

from .Tokens import Token, EOFToken, UnknownToken, NewlineToken, StringToken

from ..PyMSError import PyMSError

from typing import Type, TypeVar, Callable
from enum import Enum

class Stop(Enum):
	proceed = 0
	exclude = 1
	include = 2

T = TypeVar('T', bound=Token)
class Lexer(object):
	def __init__(self, code: str) -> None:
		self.code = code
		# self.prev_offsets: list[int] = []
		self.offset = 0
		self.line = 0 # TODO: PyMSError currently expects 0-indexed lines and reports them as 1-indexed
		self.token_types: list[Type[Token]] = []
		self.skip_tokens: list[Type[Token]] = []

	def register_token_type(self, token_type: Type[Token], skip: bool = False) -> None:
		self.token_types.append(token_type)
		if skip:
			self.skip_tokens.append(token_type)

	def _check_token(self, token: Token) -> None:
		if isinstance(token, NewlineToken):
			self.line += 1

	def _skip(self, dont_skip: Type[Token] | None = None) -> None:
		while True:
			if self.offset == len(self.code):
				return
			for skip_token_type in self.skip_tokens:
				if skip_token_type == dont_skip:
					continue
				skip_token = skip_token_type.match(self.code, self.offset)
				if skip_token:
					self._check_token(skip_token)
					self.offset += len(skip_token.raw_value)
					break
			else:
				break

	def next_token(self, peek: bool = False) -> Token:
		# start_offset = self.offset
		self._skip()
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
				if not peek:
					self.offset += len(token.raw_value)
				self._check_token(token)
				if type(token) in self.skip_tokens:
					token = None
		# self.prev_offsets.append(start_offset)
		return token

	def get_token(self, token_type: Type[T]) -> T | None:
		# start_offset = self.offset
		self._skip(dont_skip=token_type)
		if self.offset == len(self.code):
			return None
		token = token_type.match(self.code, self.offset)
		if not token:
			# token = UnknownToken.match(self.code, self.offset)
			# if not token:
			return None
		self._check_token(token)
		self.offset += len(token.raw_value)
		# self.prev_offsets.append(start_offset)
		return token

	def check_token(self, token_type: Type[T]) -> Token:
		# start_offset = self.offset
		self._skip(dont_skip=token_type)
		if self.offset == len(self.code):
			return EOFToken()
		token: Token | None = token_type.match(self.code, self.offset)
		if token:
			self._check_token(token)
			self.offset += len(token.raw_value)
		else:
			token = self.next_token()
		# self.prev_offsets.append(start_offset)
		return token

	# Read all tokens as a string until EOF or the `stop` callback returns `True`
	def read_open_string(self, stop: Callable[[Token], Stop]) -> StringToken:
		# start_offset = self.offset
		raw_string = ''
		while True:
			token = self.next_token()
			if isinstance(token, EOFToken):
				break
			should_stop = stop(token)
			if should_stop != Stop.proceed:
				if should_stop == Stop.include:
					raw_string += token.raw_value
				break
			raw_string += token.raw_value
		# self.prev_offsets.append(start_offset)
		return StringToken(raw_string)

	def skip(self, skip_token_types: Type[Token] | tuple[Type[Token], ...]) -> Token:
		# start_offset = self.offset
		if not isinstance(skip_token_types, tuple):
			skip_token_types = (skip_token_types,)
		token = self.next_token()
		while isinstance(token, skip_token_types):
			token = self.next_token()
		# self.prev_offsets.append(start_offset)
		return token

	# def rewind(self) -> None:
	# 	if not self.prev_offsets:
	# 		return
	# 	self.offset = self.prev_offsets.pop()
