
from ..DataContext import DataContext

from ....Utilities.CodeHandlers.SerializeContext import SerializeContext
from ....Utilities.CodeHandlers.Formatters import Formatters
from ....Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler

class AISerializeContext(SerializeContext):
	def __init__(self, definitions: DefinitionsHandler, formatters: Formatters, data_context: DataContext) -> None:
		SerializeContext.__init__(self, definitions, formatters)
		self.data_context = data_context
