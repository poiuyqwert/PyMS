
from ..FileFormats.TRG import Conditions, Actions

from ..Utilities import UIKit as UI
from ..Utilities.utils import fit2

class ConditionsTooltip(UI.CodeTooltip):
	tag = 'Condition'

	def gettext(self, condition_name: str) -> str | None:
		definition = Conditions.get_definition_named(condition_name)
		if not definition:
			return 'Unknown'
		return fit2(definition.help(), indent=4)

class ActionsTooltip(UI.CodeTooltip):
	tag = 'Action'

	def gettext(self, action_name: str) -> str | None:
		definition = Actions.get_definition_named(action_name)
		if not definition:
			return 'Unknown'
		return fit2(definition.help(), indent=4)
