
from ..Widgets import *
from ..Font import Font
from ..EventPattern import *

import webbrowser

from typing import Callable

class Hotlink(Label):
	def __init__(self, parent: Misc, text: str, callback: str | Callable[[Event], None] | None = None, font: Font | None = None, hover_font: Font | None = None):
		self.font = font or Font()
		self.hover_font = hover_font or Font(underline=True)
		Label.__init__(self, parent, text=text, foreground='#0000FF', cursor='hand2', font=self.font)
		self.bind(Cursor.Enter(), self.enter)
		self.bind(Cursor.Leave(), self.leave)
		if callback:
			if isinstance(callback, str):
				url = callback
				self.bind(Mouse.Click_Left(), lambda *_: webbrowser.open(url))
			else:
				self.bind(Mouse.Click_Left(), callback)

	def enter(self, e: Event) -> None:
		self['font'] = self.hover_font

	def leave(self, e: Event) -> None:
		self['font'] = self.font
