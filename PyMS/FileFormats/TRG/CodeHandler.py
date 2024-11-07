
from ...Utilities.CodeHandlers import Lexer
from ...Utilities.CodeHandlers import Tokens

import re

class TRGLexer(Lexer.Lexer):
	class KeywordsToken(Tokens.LiteralsToken):
		_literals = ('Trigger', 'BriefingTrigger', 'Conditions:', 'Actions:', 'String', 'UnitProperties')

	class SymbolToken(Tokens.LiteralsToken):
		_literals = (':', '(', ')', ',', '-')

	class ParameterToken(Tokens.RegexToken):
		_regexp = re.compile(r'"(\\.|[^"\\\r\n])*"|[^,\\(\\)#\r\n]+')

	def __init__(self, code: str) -> None:
		super().__init__(code)
		self.register_token_type(Tokens.WhitespaceToken, skip=True)
		self.register_token_type(Tokens.CommentToken, skip=True)
		self.register_token_type(Tokens.NewlineToken)
		self.register_token_type(TRGLexer.KeywordsToken)
		self.register_token_type(TRGLexer.SymbolToken)
		self.register_token_type(Tokens.IdentifierToken)
		# self.register_token_type(TRGLexer.IdentifierToken)
