
from UIKit import Label

class Hotlink(Label):
	def __init__(self, parent, text, callback=None, fonts=[('Courier', 8, 'normal'),('Courier', 8, 'underline')]):
		self.fonts = fonts
		Label.__init__(self, parent, text=text, foreground='#0000FF', cursor='hand2', font=fonts[0])
		self.bind('<Enter>', self.enter)
		self.bind('<Leave>', self.leave)
		if callback:
			self.bind('<Button-1>', callback)

	def enter(self, e):
		self['font'] = self.fonts[1]

	def leave(self, e):
		self['font'] = self.fonts[0]
