
# from .CodeDefs import CodeType
from .Lexer import *

from ..PyMSError import PyMSError
from ..fileutils import load_file
from ..PyMSWarning import PyMSWarning

class DefinitionsHandler(object):
	class SymbolToken(LiteralsToken):
		_literals = ('=', '@', '(', ')')

	class Lexer(Lexer):
		def __init__(self, code): # type: (str) -> DefinitionsHandler.Lexer
			Lexer.__init__(self, code)
			self.register_token_type(WhitespaceToken, skip=True)
			self.register_token_type(CommentToken, skip=True)
			self.register_token_type(IdentifierToken)
			self.register_token_type(DefinitionsHandler.SymbolToken)
			self.register_token_type(IntegerToken)
			self.register_token_type(NewlineToken)

	class Variable(object):
		def __init__(self, name, value, type): # type: (str, Any, CodeType) -> DefinitionsHandler.Variable
			self.name = name
			self.value = value
			self.type = type

	def __init__(self):
		self.types = {} # type: dict[str, CodeType]
		self.variables = {} # type: dict[str, DefinitionsHandler.Variable]
		self.accepted_annotations = set() # type: set[str]
		self.annotations = {} # type: dict[tuple(Any, CodeType), list[str]]

	def register_type(self, type): # type: (CodeType) -> None
		if type._name in self.types:
			raise PyMSError('Internal', "Type with name '%s' already exists" % type._name)
		self.types[type._name] = type

	def register_annotation(self, name): # type: (str) -> None
		self.accepted_annotations.add(name)

	def set_variable(self, name, value, type): # type: (str, Any, CodeType) -> None
		self.variables[name] = DefinitionsHandler.Variable(name, value, type)

	def get_variable(self, name): # type: (str) -> (DefinitionsHandler.Variable | None)
		return self.variables.get(name, None)

	def lookup_variable(self, value, type): # type: (Any, CodeType) -> (DefinitionsHandler.Variable | None)
		for variable in self.variables.values():
			if variable.type == type and variable.value == value:
				return variable
		return None

	def set_annotation(self, annotation_name, value, type): # type: (str, Any, CodeType) -> None
			annotation_info = (value, type)
			if not annotation_info in self.annotations:
				self.annotations[annotation_info] = []
			self.annotations[annotation_info].append(annotation_name)

	def get_annotations(self, value, type): # type: (Any, CodeType) -> list[str]
		annotation_info = (value, type)
		if not annotation_info in self.annotations:
			return []
		return self.annotations[annotation_info]

	def parse_file(self, file_path): # type: (str) -> None
		code = load_file(file_path)
		self.parse_code(code)

	def parse_code(self, code): # type: (str) -> list[PyMSWarning]
		warnings = []
		lexer = DefinitionsHandler.Lexer(code)
		while True:
			token = lexer.next_token()
			if isinstance(token, EOFToken):
				break
			if isinstance(token, IdentifierToken) and token.raw_value in self.types:
				type = self.types[token.raw_value]
				token = lexer.next_token()
				if not isinstance(token, IdentifierToken):
					raise PyMSError('Parse', "Expected variable name but got '%s'" % token.raw_value, line=lexer.line)
				name = token.raw_value
				if name in self.variables:
					raise PyMSError('Parse', "Variable named '%s' is already defined" % name, line=lexer.line)
				token = lexer.next_token()
				if not isinstance(token, DefinitionsHandler.SymbolToken) or not token.raw_value == '=':
					raise PyMSError('Parse', "Expected '=' but got '%s'" % token.raw_value, line=lexer.line)
				token = lexer.next_token()
				# TODO: Use type to parse?
				if not isinstance(token, IntegerToken):
					raise PyMSError('Parse', "Expected integer value but got '%s'" % token.raw_value, line=lexer.line)
				value = type.parse(token.raw_value)
				self.set_variable(name, value, type)
				token = lexer.next_token()
				if not isinstance(token, (NewlineToken, EOFToken)):
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
				if not isinstance(token, IdentifierToken):
					raise PyMSError('Parse', "Expected variable name but got '%s'" % token.raw_value, line=lexer.line)
				name = token.raw_value
				if not name in self.variables:
					raise PyMSError('Parse', "Variable named '%s' is not defined" % name, line=lexer.line)
				self.set_annotation(annotation_name, self.variables[name].value, self.variables[name].type)
				token = lexer.next_token()
				if not isinstance(token, DefinitionsHandler.SymbolToken) or not token.raw_value == ')':
					raise PyMSError('Parse', "Expected end brace ')' but got '%s'" % token.raw_value, line=lexer.line)
				token = lexer.next_token()
				if not isinstance(token, (NewlineToken, EOFToken)):
					raise PyMSError('Parse', "Unexpected token '%s' (expected end of line or file)" % token.raw_value, line=lexer.line)
				continue
			if isinstance(token, NewlineToken):
				continue
			raise PyMSError('Parse', "Unexpected token '%s' (expected a variable definition or annotation)" % token.raw_value, line=lexer.line)
		return warnings
