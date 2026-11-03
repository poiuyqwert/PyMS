from ....Utilities.CodeHandlers.Lexer import Lexer
from ....Utilities.CodeHandlers import Tokens

class GraftLexer(Lexer):
	class SymbolToken(Tokens.SymbolToken):
		_literals = (':', '(', ')', ',', '{', '}')

	def __init__(self, code: str) -> None:
		Lexer.__init__(self, code)
		self.register_token_type(Tokens.WhitespaceToken, skip=True)
		self.register_token_type(Tokens.CommentToken, skip=True)
		self.register_token_type(GraftLexer.SymbolToken)
		self.register_token_type(Tokens.HexToken)
		self.register_token_type(Tokens.IntegerToken)
		self.register_token_type(Tokens.IdentifierToken)
		self.register_token_type(Tokens.StringToken)
		self.register_token_type(Tokens.NewlineToken)
