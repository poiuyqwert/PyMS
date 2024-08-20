
from . import CodeTypes

from ....Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler

class AIDefinitionsHandler(DefinitionsHandler):
	def __init__(self) -> None:
		super().__init__()
		self.register_types(CodeTypes.all_basic_types)

		self.register_annotation('spellcaster')
