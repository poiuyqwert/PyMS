
import re

from typing import Self, Sequence

class Token(object):
	def __init__(self, raw_value: str) -> None:
		self.raw_value = raw_value

	@classmethod
	def match(cls, code: str, offset: int) -> (Self | None):
		raise NotImplementedError(cls.__name__ + '.match()')

	def __repr__(self):
		return '<%s %s>' % (self.__class__.__name__, repr(self.raw_value))

class EOFToken(Token):
	def __init__(self):
		Token.__init__(self, None)

	def __repr__(self):
		return '<%s>' % self.__class__.__name__

class RegexToken(Token):
	_regexp: re.Pattern[str]

	@classmethod
	def match(cls, code: str, offset: int) -> (Self | None):
		match = cls._regexp.match(code, offset)
		if not match:
			return None
		return cls(match.group(0))

class IdentifierToken(RegexToken):
	_regexp = re.compile(r'[a-zA-Z_][a-zA-Z_0-9]+')

class IntegerToken(RegexToken):
	_regexp = re.compile(r'-?[0-9]+')

class FloatToken(RegexToken):
	_regexp = re.compile(r'-?[0-9]+\.[0-9]+')

class StringToken(RegexToken):
	_regexp = re.compile(r'"([^\\"]|\\.)*"|\'([^\\\']|\\.)*\'')

class LiteralsToken(Token):
	_literals: Sequence[str]
	__regexp: re.Pattern[str] | None = None

	@classmethod
	def match(cls, code: str, offset: int) -> (Self | None):
		if cls.__regexp is None:
			cls.__regexp = re.compile('|'.join(re.escape(literal) for literal in cls._literals))
		match = cls.__regexp.match(code, offset)
		if not match:
			return None
		return cls(match.group(0))

class WhitespaceToken(RegexToken):
	_regexp = re.compile(r'[ \t]+')

class NewlineToken(RegexToken):
	_regexp = re.compile(r'[\r\n]+')

	def newline_count(self) -> int:
		newlines = self.raw_value.replace('\r\n', '\n')
		return len(newlines)

class CommentToken(RegexToken):
	_regexp = re.compile(r'(?:#|;)[^\r\n]*')

class UnknownToken(RegexToken):
	_regexp = re.compile(r'\s+|\S+')

class BooleanToken(RegexToken):
	_regexp = re.compile(r'true|false|1|0')
