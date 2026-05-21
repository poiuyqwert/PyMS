
from ..Widgets import *
from ..EventPattern import *
from .Tooltip import Tooltip, TooltipWindow

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
		tag_range = self.code_text.tag_prevrange(self.tag, self.code_text.index(f'@{pos[0] - self.code_text.winfo_rootx()},{pos[1] - self.code_text.winfo_rooty()}+1c'))
		if not tag_range:
			return
		hover_text = self.code_text.get(*tag_range)
		try:
			tooltip_text = self.gettext(hover_text) # pylint: disable=assignment-from-none
			if not tooltip_text:
				return
			self.tip = TooltipWindow(self.code_text, relief=SOLID, borderwidth=1)
			self.tip.make_frameless(self.code_text.winfo_toplevel())
			frame = Frame(self.tip, background='#FFFFC8', borderwidth=0)
			Label(frame, text=tooltip_text, justify=LEFT, font=self.font, fg='#000', background='#FFFFC8', relief=FLAT).pack(padx=1, pady=1)
			frame.pack()
			pos = list(self.code_text.winfo_pointerxy())
			self.tip.wm_geometry(f'+{pos[0]}+{pos[1]+22}')
			self.tip.update_idletasks()
			move = False
			if pos[0] + self.tip.winfo_reqwidth() > self.tip.winfo_screenwidth():
				move = True
				pos[0] = self.tip.winfo_screenwidth() - self.tip.winfo_reqwidth()
			if pos[1] + self.tip.winfo_reqheight() + 22 > self.tip.winfo_screenheight():
				move = True
				pos[1] -= self.tip.winfo_reqheight() + 44
			if move:
				self.tip.wm_geometry(f'+{pos[0]}+{pos[1]+22}')
		except:
			if self.tip:
				try:
					self.tip.destroy()
				except:
					pass
				self.tip = None
			return

	def gettext(self, _hover_text: str) -> str | None:
		# Overload to specify tooltip text
		return None
