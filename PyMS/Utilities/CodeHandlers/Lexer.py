
from ..PyMSError import PyMSError

import re

class Lexer(object):
	def __init__(self, code): # type: (str) -> Lexer
		self.code = code
		self.offset = 0
		self.line = None # type: (int | None)
		self.token_types = [] # type: list[Type[Token]]
		self.skip_tokens = [] # type: list[Type[Token]]

	def register_token_type(self, token_type, skip=False): # type: (Type[Token], bool) -> None
		self.token_types.append(token_type)
		if skip:
			self.skip_tokens.append(token_type)
		if token_type == NewlineToken:
			self.line = 0 # TODO: PyMSError currently expects 0-indexed lines and reports them as 1-indexed

	def next_token(self): # type: () -> Token
		token = None
		while not token:
			if self.offset == len(self.code):
				return EOFToken()
			for token_type in self.token_types:
				token = token_type.match(self.code, self.offset) # type: Token
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

	def get_token(self, token_type): # type: (Type[Token]) -> Token
		if self.offset == len(self.code):
			return EOFToken()
		token = token_type.match(self.code, self.offset)
		if not token:
			token = UnknownToken.match(self.code, self.offset)
			if not token:
					raise PyMSError('Parse', 'Could not match token')
		if token:
			self.offset += len(token.raw_value)
		return token

	# Read all tokens as a string until EOF or the `stop` callback returns `True`
	def read_open_string(self, stop): # type: (Callable[Token, bool]) -> StringToken
		raw_string = ''
		while True:
			token = self.next_token()
			if isinstance(token, EOFToken) or stop(token):
				break
			raw_string += token.raw_value
		from .CodeDefs import StrCodeType
		return StringToken(StrCodeType.serialize(raw_string))

class Token(object):
	def __init__(self, raw_value): # type: (str) -> Token
		self.raw_value = raw_value

	@classmethod
	def match(cls, code, offset): # type: (str, int) -> (Self | None)
		raise NotImplementedError(cls.__name__ + '.match()')

	def __repr__(self):
		return '<%s %s>' % (self.__class__.__name__, repr(self.raw_value))

class EOFToken(Token):
	def __init__(self):
		Token.__init__(self, None)

	def __repr__(self):
		return '<%s>' % self.__class__.__name__

class RegexToken(Token):
	_regexp = None # type: re.Pattern[str]

	@classmethod
	def match(cls, code, offset): # type: (str, int) -> (Self | None)
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
	_literals = [] # type: list[str]
	__regexp = None # type: re.Pattern[str]

	@classmethod
	def match(cls, code, offset): # type: (str, int) -> (Self | None)
		if cls.__regexp == None:
			cls.__regexp = re.compile('|'.join(re.escape(literal) for literal in cls._literals))
		match = cls.__regexp.match(code, offset)
		if not match:
			return None
		return cls(match.group(0))

class WhitespaceToken(RegexToken):
	_regexp = re.compile(r'[ \t]+')

class NewlineToken(RegexToken):
	_regexp = re.compile(r'[\r\n]+')

class CommentToken(RegexToken):
	_regexp = re.compile(r'#[^\r\n]*')

class UnknownToken(RegexToken):
	_regexp = re.compile(r'\s+|\S+')

class BooleanToken(RegexToken):
	_regexp = re.compile(r'true|false|1|0')
