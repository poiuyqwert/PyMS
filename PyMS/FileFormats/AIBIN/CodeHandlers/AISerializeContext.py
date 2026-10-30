
from .DataContext import DataContext

from ....Utilities.CodeHandlers.SerializeContext import SerializeContext
from ....Utilities.CodeHandlers.Formatters import Formatters
from ....Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler

from typing import IO

class AISerializeContext(SerializeContext):
	def __init__(self, output: IO[str], definitions: DefinitionsHandler, formatters: Formatters, data_context: DataContext) -> None:
		super().__init__(output, definitions, formatters)
		self.data_context = data_context
