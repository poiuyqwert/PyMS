
from . import WarningID

from ....Utilities.CodeHandlers.CodeDirective import DirectiveType, CodeDirectiveDefinition
from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers import Tokens
from ....Utilities.PyMSError import PyMSError

class VariableNameDirectiveType(DirectiveType[str]):
	def __init__(self) -> None:
		super().__init__('variable_name')

	def lex(self, parse_context: ParseContext) -> str:
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IdentifierToken):
			raise parse_context.error('Parse', f"Expected variable name but got '{token.raw_value}'")
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext | None) -> str:
		self.validate(token, parse_context, token)
		return token

	def validate(self, variable_name: str, parse_context: ParseContext | None, token: str | None = None) -> None:
		if parse_context is None:
			raise PyMSError('Parse', "No parse context to lookup variable '%s'" % variable_name)
		definitions = parse_context.definitions
		if definitions is None:
			raise PyMSError('Parse', "No definitions handler to lookup variable '%s'" % variable_name)
		if not definitions.get_variable(variable_name):
			raise PyMSError('Parse', "Variable named '%s' is not defined" % variable_name)

class WarningDirectiveType(DirectiveType[str]):
	def __init__(self) -> None:
		super().__init__('warning_id')

	def lex(self, parse_context: ParseContext) -> str:
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IdentifierToken):
			raise parse_context.error('Parse', f"Expected warning id but got '{token.raw_value}'")
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext | None) -> str:
		self.validate(token, parse_context, token)
		return token

	def validate(self, warning_id: str, parse_context: ParseContext | None, token: str | None = None) -> None:
		if not warning_id in WarningID.all_ids:
			raise PyMSError('Parse', f"Unrecognized warning id '{token}'")

Spellcaster = CodeDirectiveDefinition('spellcaster', (VariableNameDirectiveType(),))

all_defs_directives = [
	Spellcaster,
]

SupressAll = CodeDirectiveDefinition('suppress_all', (WarningDirectiveType(),))
SupressNextLine = CodeDirectiveDefinition('suppress_next_line', (WarningDirectiveType(),))

all_basic_directives = [
	SupressAll,
	SupressNextLine,
]
