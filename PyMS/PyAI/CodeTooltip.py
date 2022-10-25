
from .HelpContent import TYPE_HELP, CMD_HELP, DIRECTIVE_HELP

from ..FileFormats import TBL

from ..Utilities.utils import fit
from ..Utilities.UIKit import *
from ..Utilities.Tooltip import Tooltip

class CodeTooltip(Tooltip):
	tag = ''

	def __init__(self, parent, ai):
		self.ai = ai
		Tooltip.__init__(self, parent)

	def setupbinds(self, press):
		if self.tag:
			self.parent.tag_bind(self.tag, Cursor.Enter, self.enter, '+')
			self.parent.tag_bind(self.tag, Cursor.Leave, self.leave, '+')
			self.parent.tag_bind(self.tag, Mouse.Motion, self.motion, '+')
			self.parent.tag_bind(self.tag, Mouse.Click_Left, self.leave, '+')
			self.parent.tag_bind(self.tag, Mouse.ButtonRelease, self.leave)

	def showtip(self):
		if self.tip:
			return
		t = ''
		if self.tag:
			pos = list(self.parent.winfo_pointerxy())
			head,tail = self.parent.tag_prevrange(self.tag,self.parent.index('@%s,%s+1c' % (pos[0] - self.parent.winfo_rootx()),pos[1] - self.parent.winfo_rooty()))
			t = self.parent.get(head,tail)
		try:
			t = self.gettext(t)
			self.tip = Toplevel(self.parent, relief=SOLID, borderwidth=1)
			self.tip.wm_overrideredirect(1)
			frame = Frame(self.tip, background='#FFFFC8', borderwidth=0)
			Label(frame, text=t, justify=LEFT, font=self.font, fg='#000', background='#FFFFC8', relief=FLAT).pack(padx=1, pady=1)
			frame.pack()
			pos = list(self.parent.winfo_pointerxy())
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

	def gettext(self, t):
		# Overload to specify tooltip text
		return ''

class CommandCodeTooltip(CodeTooltip):
	tag = 'Commands'

	def gettext(self, cmd):
		for help,info in CMD_HELP.iteritems():
			if cmd in info:
				text = '%s Command:\n  %s(' % (help, cmd)
				break
		params = self.ai.parameters[self.ai.short_labels.index(cmd)]
		pinfo = ''
		if params:
			pinfo = '\n\n'
			done = []
			for p in params:
				t = p.__doc__.split(' ',1)[0]
				text += t + ', '
				if not t in done:
					pinfo += fit('  %s: ' % t, TYPE_HELP[t], end=True, indent=4)
					done.append(t)
			text = text[:-2]
		text += ')'
		return text + '\n' + fit('    ', info[cmd], end=True)[:-1] + pinfo[:-1]

class TypeCodeTooltip(CodeTooltip):
	tag = 'Types'

	def gettext(self, type):
		return '%s:\n%s' % (type, fit('    ', TYPE_HELP[type], end=True)[:-1])

class StringCodeTooltip(CodeTooltip):
	tag = 'HeaderString'

	def gettext(self, stringid):
		stringid = int(stringid)
		m = len(self.ai.tbl.strings)
		if stringid > m:
			text = 'Invalid String ID (Range is 0 to %s)' % (m-1)
		else:
			text = 'String %s:\n  %s' % (stringid, TBL.decompile_string(self.ai.tbl.strings[stringid]))
		return text

class FlagCodeTooltip(CodeTooltip):
	tag = 'HeaderFlags'

	def gettext(self, flags):
		text = 'AI Script Flags:\n  %s:\n    ' % flags
		if flags == '000':
			text += 'None'
		else:
			text += '\n    '.join([d for d,f in zip(['BroodWar Only','Invisible in StarEdit','Requires a Location'], flags) if f == '1'])
		return text

class DirectiveTooltip(CodeTooltip):
	tag = 'Directives'

	def gettext(self, directive):
		return DIRECTIVE_HELP.get(directive, '%s:\n  Unknown directive' % directive)
