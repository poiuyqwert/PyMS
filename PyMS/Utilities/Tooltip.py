
from utils import is_mac
from UIKit import *
from EventPattern import *

class Tooltip:
	def __init__(self, widget, text='', font=None, delay=750, press=False, mouse=False):
		self.widget = widget
		self.setupbinds(press)
		self.text = text
		self.font = font
		self.delay = delay
		self.mouse = mouse
		self.id = None
		self.tip = None
		self.pos = None

	def setupbinds(self, press):
		self.widget.winfo_toplevel().bind(Focus.Out, self.leave, '+')
		self.widget.bind(Cursor.Enter, self.enter, '+')
		self.widget.bind(Cursor.Leave, self.leave, '+')
		self.widget.bind(Mouse.Motion, self.motion, '+')
		self.widget.bind(Mouse.Click_Left, self.leave, '+')
		if press:
			self.widget.bind(Mouse.ButtonPress, self.leave)

	def enter(self, e=None):
		self.unschedule()
		self.id = self.widget.after(self.delay, self.showtip)

	def leave(self, e=None):
		self.unschedule()
		self.hidetip()

	def motion(self, e=None):
		if self.id:
			self.widget.after_cancel(self.id)
			self.id = self.widget.after(self.delay, self.showtip)

	def unschedule(self):
		if self.id:
			self.widget.after_cancel(self.id)
			self.id = None

	def showtip(self):
		if self.tip:
			return
		self.tip = Toplevel(self.widget, relief=SOLID, borderwidth=1)
		self.tip.wm_overrideredirect(1)
		if is_mac():
			self.tip.wm_transient(self.widget.winfo_toplevel())
		frame = Frame(self.tip, background='#FFFFC8', borderwidth=0)
		Label(frame, text=self.text, justify=LEFT, font=self.font, background='#FFFFC8', relief=FLAT).pack(padx=1, pady=1)
		frame.pack()
		pos = list(self.widget.winfo_pointerxy())
		self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
		self.tip.update_idletasks()
		move = False
		if not self.mouse:
			move = True
			pos = [self.widget.winfo_rootx() + self.widget.winfo_reqwidth(), self.widget.winfo_rooty() + self.widget.winfo_reqheight()]
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
