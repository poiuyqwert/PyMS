
from ..FileFormats.AIBIN.CodeHandlers import CodeCommands, CodeTypes, CodeDirectives

from ..Utilities.utils import fit
from ..Utilities.UIKit import *

class CodeTooltip(Tooltip):
	tag = ''

	def __init__(self, parent: Text):
		self.code_text = parent
		Tooltip.__init__(self, parent)

	def setupbinds(self, press: bool) -> None:
		if self.tag:
			self.code_text.tag_bind(self.tag, Cursor.Enter(), self.enter, '+')
			self.code_text.tag_bind(self.tag, Cursor.Leave(), self.leave, '+')
			self.code_text.tag_bind(self.tag, Mouse.Motion(), self.motion, '+')
			self.code_text.tag_bind(self.tag, Mouse.Click_Left(), self.leave, '+')
			self.code_text.tag_bind(self.tag, Mouse.ButtonRelease(), self.leave)

	def showtip(self) -> None:
		if self.tip:
			return
		if not self.tag:
			return
		pos = list(self.parent.winfo_pointerxy())
		tag_range = self.code_text.tag_prevrange(self.tag, self.code_text.index('@%s,%s+1c' % (pos[0] - self.code_text.winfo_rootx(),pos[1] - self.code_text.winfo_rooty())))
		if not tag_range:
			return
		hover_text = self.code_text.get(*tag_range)
		try:
			tooltip_text = self.gettext(hover_text)
			if not tooltip_text:
				return
			self.tip = TooltipWindow(self.code_text, relief=SOLID, borderwidth=1)
			self.tip.wm_overrideredirect(True)
			frame = Frame(self.tip, background='#FFFFC8', borderwidth=0)
			Label(frame, text=tooltip_text, justify=LEFT, font=self.font, fg='#000', background='#FFFFC8', relief=FLAT).pack(padx=1, pady=1)
			frame.pack()
			pos = list(self.code_text.winfo_pointerxy())
			self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
			self.tip.update_idletasks()
			move = False
			if pos[0] + self.tip.winfo_reqwidth() > self.tip.winfo_screenwidth():
				move = True
				pos[0] = self.tip.winfo_screenwidth() - self.tip.winfo_reqwidth()
			if pos[1] + self.tip.winfo_reqheight() + 22 > self.tip.winfo_screenheight():
				move = True
				pos[1] -= self.tip.winfo_reqheight() + 44
			if move:
				self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
		except:
			if self.tip:
				try:
					self.tip.destroy()
				except:
					pass
				self.tip = None
			return

	def gettext(self, hover_text: str) -> str | None:
		# Overload to specify tooltip text
		return None

class CommandCodeTooltip(CodeTooltip):
	tag = 'Commands'

	def gettext(self, cmd_name: str) -> str | None:
		cmd_defs = CodeCommands.all_basic_commands + CodeCommands.all_header_commands
		for cmd_def in cmd_defs:
			if cmd_def.name == cmd_name:
				return fit('', cmd_def.full_help_text())
		return None

class TypeCodeTooltip(CodeTooltip):
	tag = 'Types'

	def gettext(self, type_name: str) -> str | None:
		types = CodeTypes.all_basic_types
		for type in types:
			if type.name == type_name:
				return f"{type.name}:\n{fit('    ', type.help_text)}"
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

class DirectiveTooltip(CodeTooltip):
	tag = 'Directives'

	def gettext(self, directive_name: str) -> str | None:
		directive_defs = CodeDirectives.all_basic_directives + CodeDirectives.all_defs_directives
		for directive_def in directive_defs:
			if directive_def.name == directive_name:
				return fit('', directive_def.full_help_text())
		return None
