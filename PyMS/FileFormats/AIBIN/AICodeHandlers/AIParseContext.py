
from . import CodeDirectives
from ..DataContext import DataContext

from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers.Lexer import Lexer
from ....Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler
from ....Utilities.CodeHandlers.CodeDirective import CodeDirective

class AIParseContext(ParseContext):
	def __init__(self, lexer: Lexer, definitions: DefinitionsHandler, data_context: DataContext) -> None:
		ParseContext.__init__(self, lexer, definitions)
		self.data_context = data_context

	def handle_directive(self, directive: CodeDirective) -> None:
		if directive.definition == CodeDirectives.SupressAll:
			self.add_supressed_warning_id(directive.params[0])
		elif directive.definition == CodeDirectives.SupressNextLine:
			self.add_supressed_warning_id(directive.params[0], True)
