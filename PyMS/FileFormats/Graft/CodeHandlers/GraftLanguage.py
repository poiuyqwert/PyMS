from __future__ import annotations

from . import RequirementCodeCommands
from . import ButtonCodeCommands
from . import StatInfoCodeCommands

from ....Utilities.CodeHandlers.LanguageDefinition import LanguageDefinition, LanguagePlugin
from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition

# Base class for the Graft languages
class GraftLanguage(LanguageDefinition):
	# The language's commands (plugins only index their commands, so one is shared by every instance)
	CORE_PLUGIN: LanguagePlugin

	def __init__(self) -> None:
		super().__init__([self.CORE_PLUGIN])

	@classmethod
	def lookup_opcode(cls, word: int) -> CodeCommandDefinition | None:
		return cls.CORE_PLUGIN.lookup_command(word)

	@classmethod
	def commands(cls) -> list[CodeCommandDefinition]:
		return cls.CORE_PLUGIN.commands()

	@classmethod
	def has_command(cls, cmd_def: CodeCommandDefinition) -> bool:
		return cls.CORE_PLUGIN.lookup_command(cmd_def.name) is cmd_def

# The language of units.dat requirements, which are parsed by a different function than the other requirements
class UnitRequirementsLanguage(GraftLanguage):
	CORE_PLUGIN = LanguagePlugin(LanguagePlugin.CORE_ID, RequirementCodeCommands.unit_req_commands, [])

# The language of upgrades.dat, techdata.dat (research and use), and orders.dat requirements
class OtherRequirementsLanguage(GraftLanguage):
	CORE_PLUGIN = LanguagePlugin(LanguagePlugin.CORE_ID, RequirementCodeCommands.other_req_commands, [])

# The language of Buttons.graft (its button sets, button cards, and unit stat info)
class ButtonsLanguage(GraftLanguage):
	CORE_PLUGIN = LanguagePlugin(LanguagePlugin.CORE_ID, ButtonCodeCommands.button_commands + ButtonCodeCommands.button_card_commands + StatInfoCodeCommands.unit_stat_info_commands, [])
