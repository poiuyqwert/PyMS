
from ....Utilities.CodeHandlers.LanguageDefinition import LanguageDefinition, LanguagePlugin

class CorePlugin(LanguagePlugin):
	def __init__(self) -> None:
		from . import CodeCommands  # pylint: disable=cyclic-import
		from . import CodeTypes  # pylint: disable=cyclic-import
		super().__init__(LanguagePlugin.CORE_ID, CodeCommands.all_basic_commands, CodeTypes.all_basic_types)

class AISEPlugin(LanguagePlugin):
	ID = 'AISE'

	def __init__(self) -> None:
		from . import AISECodeCommands  # pylint: disable=cyclic-import
		super().__init__(AISEPlugin.ID, AISECodeCommands.all_commands, [])

class AILanguage(LanguageDefinition):
	def __init__(self) -> None:
		super().__init__([
			CorePlugin(),
			AISEPlugin(),
		])
