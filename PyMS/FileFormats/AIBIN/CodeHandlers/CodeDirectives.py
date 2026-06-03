
from . import WarningID

from ....Utilities.CodeHandlers.CodeDirective import DirectiveType, CodeDirectiveDefinition
from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers import Tokens
from ....Utilities.PyMSError import PyMSError

class VariableNameDirectiveType(DirectiveType[str]):
	def __init__(self) -> None:
		super().__init__('variable_name', 'The name of a variable')

	def lex(self, parse_context: ParseContext) -> str:
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IdentifierToken):
			raise parse_context.error('Parse', f"Expected variable name but got '{token.raw_value}'")
		return token.raw_value

	def validate(self, variable_name: str, parse_context: ParseContext, token: str | None = None) -> None:
		definitions = parse_context.definitions
		if definitions is None:
			raise PyMSError('Parse', f"No definitions handler to lookup variable '{variable_name}'")
		if not definitions.get_variable(variable_name):
			raise PyMSError('Parse', f"Variable named '{variable_name}' is not defined")

class WarningDirectiveType(DirectiveType[str]):
	def __init__(self) -> None:
		super().__init__('warning_id', 'The ID of a warning')

	def lex(self, parse_context: ParseContext) -> str:
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IdentifierToken):
			raise parse_context.error('Parse', f"Expected warning id but got '{token.raw_value}'")
		return token.raw_value

	def validate(self, warning_id: str, parse_context: ParseContext, token: str | None = None) -> None:
		if not warning_id in WarningID.all_ids:
			raise PyMSError('Parse', f"Unrecognized warning id '{warning_id}'")

class IntDirectiveType(DirectiveType[int]):
	def __init__(self) -> None:
		super().__init__('int', 'An integer number')

	def lex(self, parse_context: ParseContext) -> int:
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IntegerToken):
			raise parse_context.error('Parse', f"Expected an integer but got '{token.raw_value}'")
		try:
			return int(token.raw_value)
		except Exception as exc:
			raise parse_context.error('Parse', f"Expected an integer but got '{token.raw_value}'") from exc

ExpandUnits = CodeDirectiveDefinition('expand_units', 'Set the maximum unit id to {1}', (IntDirectiveType(),))
ExpandUpgrades = CodeDirectiveDefinition('expand_upgrades', 'Set the maximum upgrade id to {1}', (IntDirectiveType(),))
ExpandTech = CodeDirectiveDefinition('expand_tech', 'Set the maximum technology id to {1}', (IntDirectiveType(),))

Spellcaster = CodeDirectiveDefinition('spellcaster', 'Mark the variable {1} as a spellcaster so it can be used with defenseuse_xx/defensebuild_xx without warning that the unit doesn\'t have an attack.', (VariableNameDirectiveType(),))

all_defs_directives = [
	Spellcaster,
	ExpandUnits,
	ExpandUpgrades,
	ExpandTech,
]

SupressAll = CodeDirectiveDefinition('suppress_all', 'Suppress all warnings with a specific {1}', (WarningDirectiveType(),))
SupressNextLine = CodeDirectiveDefinition('suppress_next_line', 'Suppress warnings on the next line with a specific {1}', (WarningDirectiveType(),))

all_basic_directives = [
	SupressAll,
	SupressNextLine,
	ExpandUnits,
	ExpandUpgrades,
	ExpandTech,
]
