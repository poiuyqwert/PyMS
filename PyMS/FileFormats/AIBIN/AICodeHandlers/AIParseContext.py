
from . import CodeDirectives
from ..DataContext import DataContext
from ..AIFlag import AIFlag

from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers.Lexer import Lexer
from ....Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler
from ....Utilities.CodeHandlers.CodeBlock import CodeBlock
from ....Utilities.CodeHandlers.CodeDirective import CodeDirective

from dataclasses import dataclass

@dataclass
class ParsedScriptHeader(object):
	string_id: int
	bwscript: bool
	broodwar_only: bool
	staredit_hidden: bool
	requires_location: bool
	entry_point: CodeBlock | None

	@property
	def flags(self) -> int:
		return (AIFlag.requires_location if self.requires_location else 0) | (AIFlag.staredit_hidden if self.staredit_hidden else 0) | (AIFlag.broodwar_only if self.broodwar_only else 0)

class AIParseContext(ParseContext):
	def __init__(self, lexer: Lexer, definitions: DefinitionsHandler, data_context: DataContext) -> None:
		ParseContext.__init__(self, lexer, definitions)
		self.data_context = data_context
		self.spellcasters: list[int] = []
		self.script_headers: dict[str, tuple[ParsedScriptHeader, int]] = {}

	def handle_directive(self, directive: CodeDirective) -> None:
		if directive.definition == CodeDirectives.Spellcaster:
			assert self.definitions is not None
			variable = self.definitions.get_variable(directive.params[0])
			assert variable is not None
			self.spellcasters.append(variable.value)
		elif directive.definition == CodeDirectives.SupressAll:
			self.add_supressed_warning_id(directive.params[0])
		elif directive.definition == CodeDirectives.SupressNextLine:
			self.add_supressed_warning_id(directive.params[0], True)
