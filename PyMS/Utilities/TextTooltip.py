
from Tooltip import Tooltip

class TextTooltip(Tooltip):
	def __init__(self, widget, tag, **kwargs):
		self.tag = tag
		kwargs['mouse'] = True
		Tooltip.__init__(self, widget, **kwargs)

	def setupbinds(self, press):
		self.widget.tag_bind(self.tag, '<Enter>', self.enter, '+')
		self.widget.tag_bind(self.tag, '<Leave>', self.leave, '+')
		self.widget.tag_bind(self.tag, '<Motion>', self.motion, '+')
		self.widget.tag_bind(self.tag, '<Button-1>', self.leave, '+')
		if press:
			self.widget.tag_bind(self.tag, '<ButtonPress>', self.leave)
