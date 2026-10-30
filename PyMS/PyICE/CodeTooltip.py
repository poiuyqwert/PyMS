
from ..FileFormats.IScriptBIN.CodeHandlers import CodeCommands

from ..Utilities.utils import fit
from ..Utilities import UIKit as UI
from ..Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition

class AnimationTooltip(UI.CodeTooltip):
	tag = 'HeaderCommand'

	def gettext(self, cmd_name: str) -> str | None:
		if cmd_def := CodeCommandDefinition.find_by_name(cmd_name, CodeCommands.all_header_commands):
			return fit('', cmd_def.full_help_text())
		return None

class CommandTooltip(UI.CodeTooltip):
	tag = 'Command'

	def gettext(self, cmd_name: str) -> str | None:
		if cmd_def := CodeCommandDefinition.find_by_name(cmd_name, CodeCommands.all_basic_commands):
			return fit('', cmd_def.full_help_text())
		return None
