
from ...Utilities.utils import fit
from ...Utilities import UIKit as UI
from ...Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition

class CommandTooltip(UI.CodeTooltip):
	tag = 'Command'

	def __init__(self, parent: UI.Text, commands: list[CodeCommandDefinition]) -> None:
		self.commands = commands
		super().__init__(parent)

	def gettext(self, cmd_name: str) -> str | None:
		if cmd_def := CodeCommandDefinition.find_by_name(cmd_name, self.commands):
			return fit('', cmd_def.full_help_text())
		return None
