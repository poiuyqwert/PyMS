
from .Constants import RE_COORDINATES

from ..Utilities import UIKit as UI

class SelectionTooltip(UI.Tooltip):
	tag = 'Selection'

	def __init__(self, parent: UI.Text) -> None:
		self.text_widget = parent
		UI.Tooltip.__init__(self, parent)

	def setupbinds(self, press: bool) -> None:
		if self.tag:
			self.text_widget.tag_bind(self.tag, UI.Cursor.Enter(), self.enter, '+')
			self.text_widget.tag_bind(self.tag, UI.Cursor.Leave(), self.leave, '+')
			self.text_widget.tag_bind(self.tag, UI.Mouse.Motion(), self.motion, '+')
			self.text_widget.tag_bind(self.tag, UI.Mouse.Click_Left(), self.leave, '+')
			self.text_widget.tag_bind(self.tag, UI.Mouse.ButtonPress(), self.leave)

	def showtip(self) -> None:
		if self.tip:
			return
		pos = list(self.text_widget.winfo_pointerxy())
		tag_range = self.text_widget.tag_prevrange(self.tag,self.text_widget.index(f'@{pos[0] - self.text_widget.winfo_rootx()},{pos[1] - self.text_widget.winfo_rooty()}+1c'))
		if not tag_range:
			return
		head,tail = tag_range
		m = RE_COORDINATES.match(self.text_widget.get(head,tail))
		if not m:
			return
		try:
			self.tip = UI.TooltipWindow(self.text_widget, relief=UI.SOLID, borderwidth=1)
			self.tip.make_frameless(self.text_widget.winfo_toplevel())
			c = UI.Canvas(self.tip, borderwidth=0, width=255, height=255, background='#FFFFC8', highlightthickness=0, takefocus=False)
			c.pack()
			c.create_line((123,128),(134,128),fill='#00FF00')
			c.create_line((128,123),(128,134),fill='#00FF00')
			x,y = int(m.group(1)),int(m.group(2))
			c.create_line((-x+123,y+128),(-x+134,y+128),fill='#0000FF')
			c.create_line((-x+128,y+123),(-x+128,y+134),fill='#0000FF')
			pos = list(self.text_widget.winfo_pointerxy())
			self.tip.wm_geometry(f'+{pos[0]}+{pos[1]+22}')
			self.tip.update_idletasks()
			move = False
			if pos[0] + self.tip.winfo_reqwidth() > self.tip.winfo_screenwidth():
				move = True
				pos[0] = self.tip.winfo_screenwidth() - self.tip.winfo_reqwidth()
			if pos[1] + self.tip.winfo_reqheight() > self.tip.winfo_screenheight():
				move = True
				pos[1] -= self.tip.winfo_reqheight() + 44
			if move:
				self.tip.wm_geometry(f'+{pos[0]}+{pos[1]+22}')
			self.tip['background'] = '#FF0000'
		except Exception:
			if self.tip:
				try:
					self.tip.destroy()
				except Exception:
					pass
				self.tip = None
			return
