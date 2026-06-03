
# Shared scaffolding for the CodeHandlers test suite.
#
# This is intentionally not named `test_*` so unittest discovery ignores it.
# It provides a realistically-configured Lexer (mirroring the token
# registration order used by the real AI/IScript lexers) plus convenience
# builders for ParseContexts and a small reusable language.

from ...Utilities.CodeHandlers.Lexer import Lexer
from ...Utilities.CodeHandlers import Tokens
from ...Utilities.CodeHandlers import CodeType
from ...Utilities.CodeHandlers import LanguageDefinition
from ...Utilities.CodeHandlers.ParseContext import ParseContext, ParseSettings
from ...Utilities.CodeHandlers.CodeBlock import CodeBlock
from ...Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler

from ...Utilities import Struct


class HelperLexer(Lexer):
	"""A Lexer registering the standard token types in the same priority order
	the production AI lexer uses (symbols, then numbers, boolean, identifier,
	string), so token-shadowing behavior matches real usage."""

	class SymbolToken(Tokens.LiteralsToken):
		_literals = (':', '=', '@', '(', ')', ',', '{', '}', '--', '|')

	def __init__(self, code: str) -> None:
		Lexer.__init__(self, code)
		self.register_token_type(Tokens.WhitespaceToken, skip=True)
		self.register_token_type(Tokens.CommentToken, skip=True)
		self.register_token_type(HelperLexer.SymbolToken)
		self.register_token_type(Tokens.HexToken)
		self.register_token_type(Tokens.FloatToken)
		self.register_token_type(Tokens.IntegerToken)
		self.register_token_type(Tokens.BooleanToken)
		self.register_token_type(Tokens.IdentifierToken)
		self.register_token_type(Tokens.StringToken)
		self.register_token_type(Tokens.NewlineToken)


# Common code types shared across tests.
ByteType = CodeType.IntCodeType('byte', 'a byte', Struct.l_u8)
WordType = CodeType.IntCodeType('word', 'a word', Struct.l_u16)


def make_parse_context(code: str, language: LanguageDefinition.LanguageDefinition | None = None, *, definitions: DefinitionsHandler | None = None, settings: ParseSettings | None = None, with_block: bool = True) -> ParseContext:
	"""Build a ParseContext over `code` using HelperLexer. When `with_block` is
	set an empty active block is attached (mirrors the per-command parse tests)."""
	if language is None:
		language = make_language()
	lexer = HelperLexer(code)
	context = ParseContext(lexer, language, settings if settings is not None else ParseSettings(), definitions=definitions)
	if with_block:
		context.active_block = CodeBlock()
	return context


def make_language(cmd_defs=None, code_types=None) -> LanguageDefinition.LanguageDefinition:
	"""Build a single-(core)-plugin language definition."""
	return LanguageDefinition.LanguageDefinition([
		LanguageDefinition.LanguagePlugin(
			LanguageDefinition.LanguagePlugin.CORE_ID,
			cmd_defs if cmd_defs is not None else [],
			code_types if code_types is not None else [],
		)
	])
