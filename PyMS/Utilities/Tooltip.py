
from .utils import is_mac
from .UIKit import *
from .EventPattern import *

class Tooltip(object):
	# `attach_to_parent`, if True, will assign the Tooltip to the `_tooltip` property on the parent, to prevent the Tooltip from being garbage collected until its parent is
	def __init__(self, parent, text='', font=None, delay=750, press=False, mouse=False, attach_to_parent=True): # type: (Widget, str, (Font | tuple[str, int, str]), int, bool, bool, bool) -> Tooltip
		self.parent = parent
		self.setupbinds(press)
		self.text = text
		self.font = font
		self.delay = delay
		self.mouse = mouse
		self.id = None
		self.tip = None
		self.pos = None
		if attach_to_parent:
			self.parent._tooltip = self

	def setupbinds(self, press):
		self.parent.winfo_toplevel().bind(Focus.Out, self.leave, '+')
		self.parent.bind(Cursor.Enter, self.enter, '+')
		self.parent.bind(Cursor.Leave, self.leave, '+')
		self.parent.bind(Mouse.Motion, self.motion, '+')
		self.parent.bind(Mouse.Click_Left, self.leave, '+')
		if press:
			self.parent.bind(Mouse.ButtonPress, self.leave)

	def enter(self, e=None):
		self.unschedule()
		self.id = self.parent.after(self.delay, self.showtip)

	def leave(self, e=None):
		self.unschedule()
		self.hidetip()

	def motion(self, e=None):
		if self.id:
			self.parent.after_cancel(self.id)
			self.id = self.parent.after(self.delay, self.showtip)

	def unschedule(self):
		if self.id:
			self.parent.after_cancel(self.id)
			self.id = None

	def showtip(self):
		if self.tip:
			return
		self.tip = Toplevel(self.parent, relief=SOLID, borderwidth=1)
		self.tip.wm_overrideredirect(1)
		if is_mac():
			self.tip.wm_transient(self.parent.winfo_toplevel())
		frame = Frame(self.tip, background='#FFFFC8', borderwidth=0)
		Label(frame, text=self.text, justify=LEFT, font=self.font, background='#FFFFC8', relief=FLAT).pack(padx=1, pady=1)
		frame.pack()
		pos = list(self.parent.winfo_pointerxy())
		self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
		self.tip.update_idletasks()
		move = False
		if not self.mouse:
			move = True
			pos = [self.parent.winfo_rootx() + self.parent.winfo_reqwidth(), self.parent.winfo_rooty() + self.parent.winfo_reqheight()]
		if pos[0] + self.tip.winfo_reqwidth() > self.tip.winfo_screenwidth():
			move = True
			pos[0] = self.tip.winfo_screenwidth() - self.tip.winfo_reqwidth()
		if pos[1] + self.tip.winfo_reqheight() + 22 > self.tip.winfo_screenheight():
			move = True
			pos[1] -= self.tip.winfo_reqheight() + 44
		if move:
			self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))

	def hidetip(self):
		if self.tip:
			self.tip.destroy()
			self.tip = None
