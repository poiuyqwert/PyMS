
from ..Utilities.UIKit import *
from ..Utilities.Tooltip import Tooltip

# TODO: Generalize
class CodeTooltip(Tooltip):
	tag = ''

	def setupbinds(self, press):
		if self.tag:
			self.widget.tag_bind(self.tag, Cursor.Enter, self.enter, '+')
			self.widget.tag_bind(self.tag, Cursor.Leave, self.leave, '+')
			self.widget.tag_bind(self.tag, Mouse.Motion, self.motion, '+')
			self.widget.tag_bind(self.tag, Mouse.Click_Left, self.leave, '+')
			self.widget.tag_bind(self.tag, Mouse.ButtonPress, self.leave)

	def showtip(self):
		if self.tip:
			return
		t = ''
		if self.tag:
			pos = list(self.widget.winfo_pointerxy())
			head,tail = self.widget.tag_prevrange(self.tag,self.widget.index('@%s,%s+1c' % (pos[0] - self.widget.winfo_rootx(),pos[1] - self.widget.winfo_rooty())))
			t = self.widget.get(head,tail)
		try:
			t = self.gettext(t)
			self.tip = Toplevel(self.widget, relief=SOLID, borderwidth=1)
			self.tip.wm_overrideredirect(1)
			frame = Frame(self.tip, background='#FFFFC8', borderwidth=0)
			Label(frame, text=t, justify=LEFT, font=self.font, background='#FFFFC8', relief=FLAT).pack(padx=1, pady=1)
			frame.pack()
			pos = list(self.widget.winfo_pointerxy())
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