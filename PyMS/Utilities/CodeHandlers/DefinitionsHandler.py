
from __future__ import annotations

from .Lexer import Lexer as _Lexer
from . import Tokens
from .ParseContext import ParseContext

from ..PyMSError import PyMSError
from ..PyMSWarning import PyMSWarning
from .. import IO

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from .CodeType import CodeType

class Variable(object):
	def __init__(self, name: str, value: Any, type: CodeType) -> None:
		self.name = name
		self.value = value
		self.type = type

class DefinitionsHandler(object):
	class SymbolToken(Tokens.LiteralsToken):
		_literals = ('=', '@', '(', ')')

	class Lexer(_Lexer):
		def __init__(self, code: str) -> None:
			_Lexer.__init__(self, code)
			self.register_token_type(Tokens.WhitespaceToken, skip=True)
			self.register_token_type(Tokens.CommentToken, skip=True)
			self.register_token_type(Tokens.IdentifierToken)
			self.register_token_type(DefinitionsHandler.SymbolToken)
			self.register_token_type(Tokens.IntegerToken)
			self.register_token_type(Tokens.NewlineToken)

	def __init__(self) -> None:
		self.types: dict[str, CodeType] = {}
		self.variables: dict[str, Variable] = {}
		self.accepted_annotations: set[str] = set()
		self.annotations: dict[tuple[Any, CodeType], list[str]] = {}

	def register_type(self, type: CodeType) -> None:
		if type._name in self.types:
			raise PyMSError('Internal', "Type with name '%s' already exists" % type._name)
		self.types[type._name] = type

	def register_annotation(self, name: str) -> None:
		self.accepted_annotations.add(name)

	def set_variable(self, name: str, value: Any, type: CodeType) -> None:
		self.variables[name] = Variable(name, value, type)

	def get_variable(self, name: str) -> (Variable | None):
		return self.variables.get(name, None)

	def lookup_variable(self, value: Any, type: CodeType) -> (Variable | None):
		for variable in self.variables.values():
			if variable.type == type and variable.value == value:
				return variable
		return None

	def set_annotation(self, annotation_name: str, value: Any, type: CodeType) -> None:
			annotation_info = (value, type)
			if not annotation_info in self.annotations:
				self.annotations[annotation_info] = []
			self.annotations[annotation_info].append(annotation_name)

	def get_annotations(self, value: Any, type: CodeType) -> list[str]:
		annotation_info = (value, type)
		if not annotation_info in self.annotations:
			return []
		return self.annotations[annotation_info]

	def parse(self, input: IO.AnyInputText) -> list[PyMSWarning]:
		with IO.InputText(input) as f:
			code = f.read()
		warnings: list[PyMSWarning] = []
		lexer = DefinitionsHandler.Lexer(code)
		parse_context = ParseContext()
		while True:
			token = lexer.next_token()
			if isinstance(token, Tokens.EOFToken):
				break
			if isinstance(token, Tokens.IdentifierToken) and token.raw_value in self.types:
				type = self.types[token.raw_value]
				token = lexer.next_token()
				if not isinstance(token, Tokens.IdentifierToken):
					raise PyMSError('Parse', "Expected variable name but got '%s'" % token.raw_value, line=lexer.line)
				name = token.raw_value
				if name in self.variables:
					raise PyMSError('Parse', "Variable named '%s' is already defined" % name, line=lexer.line)
				token = lexer.next_token()
				if not isinstance(token, DefinitionsHandler.SymbolToken) or not token.raw_value == '=':
					raise PyMSError('Parse', "Expected '=' but got '%s'" % token.raw_value, line=lexer.line)
				token = lexer.next_token()
				# TODO: Use type to parse?
				if not isinstance(token, Tokens.IntegerToken):
					raise PyMSError('Parse', "Expected integer value but got '%s'" % token.raw_value, line=lexer.line)
				value = type.parse(token.raw_value, parse_context)
				self.set_variable(name, value, type)
				token = lexer.next_token()
				if not isinstance(token, (Tokens.NewlineToken, Tokens.EOFToken)):
					raise PyMSError('Parse', "Unexpected token '%s' (expected end of line or file)" % token.raw_value, line=lexer.line)
				continue
			if isinstance(token, DefinitionsHandler.SymbolToken) and token.raw_value == '@':
				token = lexer.next_token()
				annotation_name = token.raw_value
				if not annotation_name in self.accepted_annotations:
					warnings.append(PyMSWarning('Parse', "Unknown annotation '@%s'" % token.raw_value, line=lexer.line))
				token = lexer.next_token()
				if not isinstance(token, DefinitionsHandler.SymbolToken) or not token.raw_value == '(':
					raise PyMSError('Parse', "Expected '(' but got '%s'" % token.raw_value, line=lexer.line)
				token = lexer.next_token()
				# TODO: Annotate raw values and not just variables? Use type to parse?
				if not isinstance(token, Tokens.IdentifierToken):
					raise PyMSError('Parse', "Expected variable name but got '%s'" % token.raw_value, line=lexer.line)
				name = token.raw_value
				if not name in self.variables:
					raise PyMSError('Parse', "Variable named '%s' is not defined" % name, line=lexer.line)
				self.set_annotation(annotation_name, self.variables[name].value, self.variables[name].type)
				token = lexer.next_token()
				if not isinstance(token, DefinitionsHandler.SymbolToken) or not token.raw_value == ')':
					raise PyMSError('Parse', "Expected end brace ')' but got '%s'" % token.raw_value, line=lexer.line)
				token = lexer.next_token()
				if not isinstance(token, (Tokens.NewlineToken, Tokens.EOFToken)):
					raise PyMSError('Parse', "Unexpected token '%s' (expected end of line or file)" % token.raw_value, line=lexer.line)
				continue
			if isinstance(token, Tokens.NewlineToken):
				continue
			raise PyMSError('Parse', "Unexpected token '%s' (expected a variable definition or annotation)" % token.raw_value, line=lexer.line)
		return warnings
