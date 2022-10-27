
from ..FileFormats import IScriptBIN

from ..Utilities.utils import fit
from ..Utilities.UIKit import *
from ..Utilities.Tooltip import Tooltip

class CodeTooltip(Tooltip):
	tag = ''

	def setupbinds(self, press):
		if self.tag:
			self.parent.tag_bind(self.tag, Cursor.Enter, self.enter, '+')
			self.parent.tag_bind(self.tag, Cursor.Leave, self.leave, '+')
			self.parent.tag_bind(self.tag, Mouse.Motion, self.motion, '+')
			self.parent.tag_bind(self.tag, Mouse.Click_Left, self.leave, '+')
			self.parent.tag_bind(self.tag, Mouse.ButtonPress, self.leave)

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

class AnimationTooltip(CodeTooltip):
	tag = 'Animations'

	def gettext(self, anim):
		return 'Animation:\n  %s\n%s' % (anim,fit('    ', IScriptBIN.HEADER_HELP[IScriptBIN.REV_HEADER[anim]], end=True)[:-1])

class CommandTooltip(CodeTooltip):
	tag = 'Commands'

	def gettext(self, cmd):
		text = 'Command:\n  %s(' % cmd
		c = IScriptBIN.REV_OPCODES[cmd]
		params = IScriptBIN.OPCODES[c][1]
		pinfo = ''
		if params:
			pinfo = '\n\n'
			done = []
			for p in params:
				t = p.__doc__
				text += t + ', '
				if not t in done:
					pinfo += fit('  %s: ' % t, IScriptBIN.TYPE_HELP[t], end=True, indent=4)
					done.append(t)
			text = text[:-2]
		text += ')'
		return text + '\n' + fit('    ', IScriptBIN.CMD_HELP[c], end=True)[:-1] + pinfo[:-1]
