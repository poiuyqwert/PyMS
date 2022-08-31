
from .UIKit import StringVar

class SStringVar(StringVar):
	def __init__(self, val='', length=0, callback=None):
		StringVar.__init__(self)
		self.check = True
		self.length = length
		self.lastvalid = val
		self.set(val)
		self.callback = callback
		self.trace('w', self.editvalue)

	def editvalue(self, *_):
		if self.check:
			s = self.get()
			if self.length and len(s) > self.length:
				self.set(self.lastvalid)
			else:
				self.lastvalid = s
				if self.callback:
					self.callback(s)
		else:
			self.lastvalid = self.get()
			self.check = True
