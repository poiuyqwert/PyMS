
from ..FileFormats.TRG import Conditions, Actions

from ..Utilities.UIKit import CodeTooltip
from ..Utilities.utils import fit2

class ConditionsTooltip(CodeTooltip):
	tag = 'Condition'

	def gettext(self, condition_name: str) -> str | None:
		definition = Conditions.get_definition_named(condition_name)
		if not definition:
			return 'Unknown'
		return fit2(definition.help(), indent=4)

class ActionsTooltip(CodeTooltip):
	tag = 'Action'

	def gettext(self, action_name: str) -> str | None:
		definition = Actions.get_definition_named(action_name)
		if not definition:
			return 'Unknown'
		return fit2(definition.help(), indent=4)
