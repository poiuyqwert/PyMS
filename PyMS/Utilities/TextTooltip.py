
from Tooltip import Tooltip

class TextTooltip(Tooltip):
	def __init__(self, parent, tag, **kwargs):
		self.tag = tag
		kwargs['mouse'] = True
		Tooltip.__init__(self, parent, **kwargs)

	def setupbinds(self, press):
		self.parent.tag_bind(self.tag, '<Enter>', self.enter, '+')
		self.parent.tag_bind(self.tag, '<Leave>', self.leave, '+')
		self.parent.tag_bind(self.tag, '<Motion>', self.motion, '+')
		self.parent.tag_bind(self.tag, '<Button-1>', self.leave, '+')
		if press:
			self.parent.tag_bind(self.tag, '<ButtonPress>', self.leave)
