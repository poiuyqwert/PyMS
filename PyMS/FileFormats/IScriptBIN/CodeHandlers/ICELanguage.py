
from ....Utilities.CodeHandlers.LanguageDefinition import LanguageDefinition, LanguagePlugin

class CorePlugin(LanguagePlugin):
	def __init__(self) -> None:
		from . import CodeCommands
		from . import CodeTypes
		super().__init__(LanguagePlugin.CORE_ID, CodeCommands.all_basic_commands, CodeTypes.all_basic_types)

class ICELanguage(LanguageDefinition):
	def __init__(self) -> None:
		super().__init__([
			CorePlugin(),
		])
