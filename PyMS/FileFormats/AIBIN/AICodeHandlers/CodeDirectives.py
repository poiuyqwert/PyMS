
from . import WarningID

from ....Utilities.CodeHandlers.CodeDirective import DirectiveType, CodeDirectiveDefinition
from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers import Tokens
from ....Utilities.PyMSError import PyMSError

class WarningDirectiveType(DirectiveType[str]):
	def __init__(self) -> None:
		super().__init__('warning_id')

	def lex(self, parse_context: ParseContext) -> str:
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IdentifierToken):
			raise parse_context.error('Parse', f"Expected warning id but got '{token.raw_value}'")
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext | None) -> str:
		if not token in WarningID.all_ids:
			raise PyMSError('Parse', f"Unrecognized warning id '{token}'")
		return token

SupressAll = CodeDirectiveDefinition('suppress_all', (WarningDirectiveType(),))
SupressNextLine = CodeDirectiveDefinition('suppress_next_line', (WarningDirectiveType(),))

all_basic_directives = [
	SupressAll,
	SupressNextLine
]
