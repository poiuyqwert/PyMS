
from ..FileFormats.AIBIN.CodeHandlers import CodeCommands, CodeTypes, CodeDirectives, AISECodeCommands

from ..Utilities.utils import fit
from ..Utilities import UIKit as UI
from ..Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ..Utilities.CodeHandlers.CodeType import CodeType
from ..Utilities.CodeHandlers.CodeDirective import CodeDirectiveDefinition

class CommandCodeTooltip(UI.CodeTooltip):
	tag = 'Command'

	def gettext(self, cmd_name: str) -> str | None:
		if cmd_def := CodeCommandDefinition.find_by_name(cmd_name, CodeCommands.all_basic_commands + CodeCommands.all_header_commands):
			return fit('', cmd_def.full_help_text())
		return None

class AISECommandCodeTooltip(UI.CodeTooltip):
	tag = 'AISECommand'

	def gettext(self, cmd_name: str) -> str | None:
		if cmd_def := CodeCommandDefinition.find_by_name(cmd_name, AISECodeCommands.all_commands):
			return fit('', cmd_def.full_help_text())
		return None

class TypeCodeTooltip(UI.CodeTooltip):
	tag = 'Type'

	def gettext(self, type_name: str) -> str | None:
		if code_type := CodeType.find_by_name(type_name, CodeTypes.all_basic_types):
			return f"{code_type.name}:\n{fit('    ', code_type.help_text)}"
		return None

# class StringCodeTooltip(CodeTooltip):
# 	tag = 'HeaderString'

# 	def gettext(self, stringid):
# 		stringid = int(stringid)
# 		m = len(self.ai.tbl.strings)
# 		if stringid > m:
# 			text = 'Invalid String ID (Range is 0 to %s)' % (m-1)
# 		else:
# 			text = 'String %s:\n  %s' % (stringid, TBL.decompile_string(self.ai.tbl.strings[stringid]))
# 		return text

# class FlagCodeTooltip(CodeTooltip):
# 	tag = 'HeaderFlags'

# 	def gettext(self, flags):
# 		text = 'AI Script Flags:\n  %s:\n    ' % flags
# 		if flags == '000':
# 			text += 'None'
# 		else:
# 			text += '\n    '.join([d for d,f in zip(['BroodWar Only','Invisible in StarEdit','Requires a Location'], flags) if f == '1'])
# 		return text

class DirectiveTooltip(UI.CodeTooltip):
	tag = 'Directive'

	def gettext(self, directive_name: str) -> str | None:
		if directive_def := CodeDirectiveDefinition.find_by_name(directive_name, CodeDirectives.all_basic_directives + CodeDirectives.all_defs_directives):
			return fit('', directive_def.full_help_text())
		return None
