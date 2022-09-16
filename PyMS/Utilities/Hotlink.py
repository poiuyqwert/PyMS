
from .UIKit import Label, Font
from .EventPattern import *

import webbrowser

class Hotlink(Label):
	def __init__(self, parent, text, callback=None, font=None, hover_font=None):
		self.font = font or Font()
		self.hover_font = hover_font or Font(underline=True)
		Label.__init__(self, parent, text=text, foreground='#0000FF', cursor='hand2', font=self.font)
		self.bind(Cursor.Enter, self.enter)
		self.bind(Cursor.Leave, self.leave)
		if callback:
			if isinstance(callback, str):
				self.bind(Mouse.Click_Left, lambda *_: webbrowser.open(callback))
			else:
				self.bind(Mouse.Click_Left, callback)

	def enter(self, e):
		self['font'] = self.hover_font

	def leave(self, e):
		self['font'] = self.font
