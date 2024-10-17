
from ....Utilities.CodeHandlers.Lexer import Lexer
from ....Utilities.CodeHandlers import Tokens

import re

class ICELexer(Lexer):
	class SymbolToken(Tokens.LiteralsToken):
		_literals = (':', '=', '(', ')', ',')

	class NoneToken(Tokens.LiteralsToken):
		_literals = ('[NONE]',)

	class HeaderToken(Tokens.RegexToken):
		_regexp = re.compile(r'\.header(?:start|end)')

	def __init__(self, code: str) -> None:
		Lexer.__init__(self, code)
		self.register_token_type(Tokens.WhitespaceToken, skip=True)
		self.register_token_type(Tokens.CommentToken, skip=True)
		self.register_token_type(ICELexer.HeaderToken)
		self.register_token_type(ICELexer.NoneToken)
		self.register_token_type(ICELexer.SymbolToken)
		self.register_token_type(Tokens.HexToken)
		self.register_token_type(Tokens.IntegerToken)
		self.register_token_type(Tokens.BooleanToken)
		self.register_token_type(Tokens.IdentifierToken)
		self.register_token_type(Tokens.StringToken)
		self.register_token_type(Tokens.NewlineToken)
