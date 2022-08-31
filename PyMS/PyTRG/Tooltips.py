
from .CodeTooltip import CodeTooltip
from .HelpText import *

from ..FileFormats import TRG

from ..Utilities.utils import fit

class ConditionsTooltip(CodeTooltip):
	tag = 'Conditions'

	def gettext(self, condition):
		text = 'Condition:\n  %s(' % condition
		if condition == 'RawCond':
			text += """Long, Long, Long, Short, Byte, Byte, Byte, Byte)
    Create a condition from raw values

  Long: Any number in the range 0 to 4294967295
  Short: Any number in the range 0 to 65535
  Byte: Any number in the range 0 to 255"""
			return text
		params = self.parent.toplevel.trg.condition_parameters[self.parent.toplevel.trg.conditions.index(condition)]
		pinfo = ''
		if params:
			pinfo = '\n\n'
			done = []
			for p in params:
				t = p.__doc__.split(' ',1)[0]
				text += t + ', '
				if not t in done:
					pinfo += fit('  %s: ' % t, TRG.TYPE_HELP[t], end=True, indent=4)
					done.append(t)
			text = text[:-2]
		text += ')'
		return text + '\n' + fit('    ', CONDITIONS_HELP[condition], end=True)[:-1] + pinfo[:-1]

class ActionsTooltip(CodeTooltip):
	tag = 'Actions'

	def gettext(self, action):
		text = 'Action:\n  %s(' % action
		if action == 'RawAct':
			text += """Long, Long, Long, Long, Long, Long, Short, Byte, Byte)
    Create an action from raw values

  Long: Any number in the range 0 to 4294967295
  Short: Any number in the range 0 to 65535
  Byte: Any number in the range 0 to 255"""
			return text
		params = self.parent.toplevel.trg.action_parameters[self.parent.toplevel.trg.actions.index(action)]
		pinfo = ''
		if params:
			pinfo = '\n\n'
			done = []
			for p in params:
				t = p.__doc__.split(' ',1)[0]
				text += t + ', '
				if not t in done:
					pinfo += fit('  %s: ' % t, TRG.TYPE_HELP[t], end=True, indent=4)
					done.append(t)
			text = text[:-2]
		return text + ')\n' + fit('    ', ACTIONS_HELP[action], end=True)[:-1] + pinfo[:-1]

class TrigPlugActionsTooltip(CodeTooltip):
	tag = 'TrigPlugActions'

	def gettext(self, action):
		text = 'TrigPlug Action:\n  %s(' % action
		params = self.parent.toplevel.trg.new_action_parameters[self.parent.toplevel.trg.new_actions.index(action)]
		pinfo = ''
		if params:
			pinfo = '\n\n'
			done = []
			for p in params:
				t = p.__doc__.split(' ',1)[0]
				text += t + ', '
				if not t in done:
					pinfo += fit('  %s: ' % t, TRG.TYPE_HELP[t], end=True, indent=4)
					done.append(t)
			text = text[:-2]
		text += ')'
		return text + '\n' + fit('    ', NEW_ACTIONS_HELP[action], end=True)[:-1] + pinfo[:-1]
