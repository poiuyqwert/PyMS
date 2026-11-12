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
	def commands(cls) -> list[CodeCommandDefinition]:
		return cls.CORE_PLUGIN.commands()

	@classmethod
	def has_command(cls, cmd_def: CodeCommandDefinition) -> bool:
		return cls.CORE_PLUGIN.lookup_command(cmd_def.name) is cmd_def

# Base class for the languages of the requirement .graft files (one per file, since each file's errors name what its requirements are for)
class ReqGraftLanguage(GraftLanguage):
	# What the file's scripts are the requirements for
	DESCRIPTION: str
	# Keyword for the header of each script in the source code
	HEADER_KEYWORD: str
	# The opcodes the file can be loaded with, by their value (including ones the language doesn't have available, that the game still handles for the file)
	LOADABLE_OPCODES: dict[int, CodeCommandDefinition]

# The language of units.dat requirements, which are parsed by a different function than the other requirements
class UnitRequirementsLanguage(ReqGraftLanguage):
	DESCRIPTION = 'Unit Requirements'
	HEADER_KEYWORD = 'Unit'
	LOADABLE_OPCODES = RequirementCodeCommands.unit_loadable_opcodes
	CORE_PLUGIN = LanguagePlugin(LanguagePlugin.CORE_ID, RequirementCodeCommands.unit_req_commands, [])

# The language of upgrades.dat requirements
class UpgradeRequirementsLanguage(ReqGraftLanguage):
	DESCRIPTION = 'Upgrade Requirements'
	HEADER_KEYWORD = 'Upgrade'
	LOADABLE_OPCODES = RequirementCodeCommands.check_allowed_loadable_opcodes
	CORE_PLUGIN = LanguagePlugin(LanguagePlugin.CORE_ID, RequirementCodeCommands.upgrade_req_commands, [])

# The language of techdata.dat research requirements
class ResearchRequirementsLanguage(ReqGraftLanguage):
	DESCRIPTION = 'Tech Research Requirements'
	HEADER_KEYWORD = 'Research'
	LOADABLE_OPCODES = RequirementCodeCommands.check_allowed_loadable_opcodes
	CORE_PLUGIN = LanguagePlugin(LanguagePlugin.CORE_ID, RequirementCodeCommands.research_req_commands, [])

# The language of techdata.dat use requirements
class TechRequirementsLanguage(ReqGraftLanguage):
	DESCRIPTION = 'Tech Use Requirements'
	HEADER_KEYWORD = 'Tech'
	LOADABLE_OPCODES = RequirementCodeCommands.check_allowed_loadable_opcodes
	CORE_PLUGIN = LanguagePlugin(LanguagePlugin.CORE_ID, RequirementCodeCommands.tech_use_req_commands, [])

# The language of orders.dat requirements
class OrderRequirementsLanguage(ReqGraftLanguage):
	DESCRIPTION = 'Order Requirements'
	HEADER_KEYWORD = 'Order'
	LOADABLE_OPCODES = RequirementCodeCommands.check_allowed_loadable_opcodes
	CORE_PLUGIN = LanguagePlugin(LanguagePlugin.CORE_ID, RequirementCodeCommands.order_req_commands, [])

# The language of Buttons.graft (its button sets, button cards, and unit stat info)
class ButtonsLanguage(GraftLanguage):
	CORE_PLUGIN = LanguagePlugin(LanguagePlugin.CORE_ID, ButtonCodeCommands.button_commands + ButtonCodeCommands.button_card_commands + StatInfoCodeCommands.unit_stat_info_commands, [])
