
from ....Utilities.CodeHandlers.Lexer import Lexer
from ....Utilities.CodeHandlers import Tokens

import re

class AILexer(Lexer):
	class SymbolToken(Tokens.LiteralsToken):
		_literals = (':', '=', '@', '(', ')', ',', '{', '}', '--')

	class AISESymbolToken(Tokens.LiteralsToken):
		_literals = ('.', '|', '~')

	class ScriptIDToken(Tokens.RegexToken):
		_regexp = re.compile(r'\S{4}')

	def __init__(self, code: str) -> None:
		Lexer.__init__(self, code)
		self.register_token_type(Tokens.WhitespaceToken, skip=True)
		self.register_token_type(Tokens.CommentToken, skip=True)
		self.register_token_type(AILexer.SymbolToken)
		self.register_token_type(AILexer.AISESymbolToken)
		self.register_token_type(Tokens.HexToken) # Required for AISE
		self.register_token_type(Tokens.IntegerToken)
		self.register_token_type(Tokens.BooleanToken)
		self.register_token_type(Tokens.IdentifierToken)
		self.register_token_type(Tokens.StringToken)
		self.register_token_type(Tokens.NewlineToken)
