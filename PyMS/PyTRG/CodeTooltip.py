
from ..Utilities.UIKit import *

# TODO: Generalize
class CodeTooltip(Tooltip):
	tag: str

	def __init__(self, parent: CodeText, text: str = '', font: Font | None = None, delay: int = 750, press: bool = False, mouse: bool = True, attach_to_parent: bool = True):
		self.code_text = parent
		super().__init__(parent, text, font, delay, press, mouse, attach_to_parent)

	def setupbinds(self, press: bool) -> None:
		if self.tag:
			self.code_text.tag_bind(self.tag, Cursor.Enter(), self.enter, '+')
			self.code_text.tag_bind(self.tag, Cursor.Leave(), self.leave, '+')
			self.code_text.tag_bind(self.tag, Mouse.Motion(), self.motion, '+')
			self.code_text.tag_bind(self.tag, Mouse.Click_Left(), self.leave, '+')
			self.code_text.tag_bind(self.tag, Mouse.ButtonPress(), self.leave)

	def showtip(self) -> None:
		if self.tip:
			return
		t = ''
		if self.tag:
			pos = list(self.code_text.winfo_pointerxy())
			tag_range = self.code_text.tag_prevrange(self.tag,self.code_text.index('@%s,%s+1c' % (pos[0] - self.code_text.winfo_rootx(),pos[1] - self.code_text.winfo_rooty())))
			if tag_range:
				head,tail = tag_range
				t = self.code_text.get(head,tail)
		try:
			t = self.gettext(t)
			self.tip = TooltipWindow(self.code_text, relief=SOLID, borderwidth=1)
			self.tip.wm_overrideredirect(True)
			frame = Frame(self.tip, background='#FFFFC8', borderwidth=0)
			Label(frame, text=t, justify=LEFT, font=self.font, fg='#000', background='#FFFFC8', relief=FLAT).pack(padx=1, pady=1) # type: ignore[arg-type]
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

	def gettext(self, t):
		# Overload to specify tooltip text
		return ''