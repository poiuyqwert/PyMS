
from . import CodeTypes
from . import CodeDirectives

from ....Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler, DefinitionsSourceCodeParser

class AIDefinitionsHandler(DefinitionsHandler):
	def __init__(self) -> None:
		super().__init__()
		self.register_types(CodeTypes.all_basic_types)

class AIDefinitionsSourceCodeParser(DefinitionsSourceCodeParser):
	def __init__(self) -> None:
		super().__init__()
		self.register_directives(CodeDirectives.all_defs_directives)
