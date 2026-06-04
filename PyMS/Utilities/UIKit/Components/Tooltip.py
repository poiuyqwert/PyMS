
from ..Font import Font
from ..Widgets import Frame, Label, Misc, Toplevel
from ..Constants import FLAT, LEFT, SOLID
from .. import Event
from ..Widgets.Extensions import MiscExtensions
from ..EventPattern import Cursor, Focus, Mouse

from typing import cast

class TooltipWindow(Toplevel):
	pass

class Tooltip:
	# `attach_to_parent`, if True, will assign the Tooltip to the `_tooltip` property on the parent, to prevent the Tooltip from being garbage collected until its parent is
	def __init__(self, parent: Misc, text: str = '', *, font: Font | None = None, delay: int = 750, press: bool = False, mouse: bool = True, attach_to_parent: bool = True):
		self.parent: MiscExtensions = cast(MiscExtensions, parent)
		self.setupbinds(press)
		self.text = text
		self.font = font or Font.fixed()
		self.delay = delay
		self.mouse = mouse
		self.id: str | None = None
		self.tip: TooltipWindow | None = None
		if attach_to_parent:
			setattr(self.parent, '_tooltip_' + self.__class__.__name__, self)

	def setupbinds(self, press: bool) -> None:
		self.parent.winfo_toplevel().bind(Focus.Out(), self.leave, '+')
		self.parent.bind(Cursor.Enter(), self.enter, '+')
		self.parent.bind(Cursor.Leave(), self.leave, '+')
		self.parent.bind(Mouse.Motion(), self.motion, '+')
		self.parent.bind(Mouse.Click_Left(), self.leave, '+')
		if press:
			self.parent.bind(Mouse.ButtonPress(), self.leave, '+')

	def enter(self, _event: Event | None = None) -> None:
		self.unschedule()
		self.id = self.parent.after_managed(self.delay, self.showtip)

	def leave(self, _event: Event | None = None) -> None:
		self.unschedule()
		self.hidetip()

	def motion(self, _event: Event | None = None) -> None:
		if self.id:
			self.parent.after_managed_cancel(self.id)
			self.id = self.parent.after_managed(self.delay, self.showtip)

	def unschedule(self) -> None:
		if self.id:
			self.parent.after_managed_cancel(self.id)
			self.id = None

	def showtip(self) -> None:
		if self.tip:
			return
		self.tip = TooltipWindow(self.parent, relief=SOLID, borderwidth=1)
		self.tip.make_frameless(self.parent.winfo_toplevel())
		frame = Frame(self.tip, background='#FFFFC8', borderwidth=0)
		Label(frame, text=self.text, justify=LEFT, font=self.font, foreground='#000', background='#FFFFC8', relief=FLAT).pack(padx=1, pady=1) # type: ignore[arg-type]
		frame.pack()
		x,y = tuple(self.parent.winfo_pointerxy())
		self.tip.update_idletasks()
		if not self.mouse:
			x = self.parent.winfo_rootx() + self.parent.winfo_width() + 5
			y = self.parent.winfo_rooty() + self.parent.winfo_height() + 5
		else:
			x += 10
			y += 20
		if x + self.tip.winfo_width() > self.tip.winfo_screenwidth():
			x = self.tip.winfo_screenwidth() - self.tip.winfo_width()
		if y + self.tip.winfo_height() > self.tip.winfo_screenheight():
			y = self.tip.winfo_screenheight() - self.tip.winfo_height()
		self.tip.wm_geometry(f'+{x}+{y}')

	def hidetip(self) -> None:
		if self.tip:
			self.tip.destroy()
			self.tip = None
