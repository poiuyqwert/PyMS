
from . import CodeDirectives
from ..DataContext import DataContext
from ..AIFlag import AIFlag

from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers.Lexer import Lexer
from ....Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler
from ....Utilities.CodeHandlers.CodeBlock import CodeBlock
from ....Utilities.CodeHandlers.CodeDirective import CodeDirective

class ParsedScriptHeader(object):
	def __init__(self) -> None:
		self.string_id: int | None = None
		self.bwscript: bool | None = None
		self.broodwar_only: bool | None = None
		self.staredit_hidden: bool | None = None
		self.requires_location: bool | None = None
		self.entry_point_name: str | None = None
		self.entry_point: CodeBlock | None = None
	
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
