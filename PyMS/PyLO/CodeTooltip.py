
from .Constants import RE_COORDINATES

from ..Utilities.Tooltip import Tooltip
from ..Utilities.UIKit import *

class CodeTooltip(Tooltip):
	tag = 'Selection'

	def __init__(self, parent):
		Tooltip.__init__(self, parent)

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
		pos = list(self.parent.winfo_pointerxy())
		head,tail = self.parent.tag_prevrange(self.tag,self.parent.index('@%s,%s+1c' % (pos[0] - self.parent.winfo_rootx(),pos[1] - self.parent.winfo_rooty())))
		m = RE_COORDINATES.match(self.parent.get(head,tail))
		if not m:
			return
		try:
			self.tip = Toplevel(self.parent, relief=SOLID, borderwidth=1)
			self.tip.wm_overrideredirect(1)
			c = Canvas(self.tip, borderwidth=0, width=255, height=255, background='#FFFFC8', highlightthickness=0, takefocus=False)
			c.pack()
			c.create_line(123,128,134,128,fill='#00FF00')
			c.create_line(128,123,128,134,fill='#00FF00')
			x,y = int(m.group(1)),int(m.group(2))
			c.create_line(-x+123,y+128,-x+134,y+128,fill='#0000FF')
			c.create_line(-x+128,y+123,-x+128,y+134,fill='#0000FF')
			pos = list(self.parent.winfo_pointerxy())
			self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
			self.tip.update_idletasks()
			move = False
			if pos[0] + self.tip.winfo_reqwidth() > self.tip.winfo_screenwidth():
				move = True
				pos[0] = self.tip.winfo_screenwidth() - self.tip.winfo_reqwidth()
			if pos[1] + self.tip.winfo_reqheight() > self.tip.winfo_screenheight():
				move = True
				pos[1] -= self.tip.winfo_reqheight() + 44
			if move:
				self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
			self.tip['background'] = '#FF0000'
		except:
			if self.tip:
				try:
					self.tip.destroy()
				except:
					pass
				self.tip = None
			return
