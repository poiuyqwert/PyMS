
from .CodeTooltip import CodeTooltip

from ..FileFormats.TRG import Conditions, Actions

from ..Utilities.utils import fit2

class ConditionsTooltip(CodeTooltip):
	tag = 'Conditions'

	def gettext(self, condition_name):
		definition = Conditions.get_definition_named(condition_name)
		if not definition:
			return 'Unknown'
		return fit2(definition.help(), indent=4)

class ActionsTooltip(CodeTooltip):
	tag = 'Actions'

	def gettext(self, action_name):
		definition = Actions.get_definition_named(action_name)
		if not definition:
			return 'Unknown'
		return fit2(definition.help(), indent=4)
