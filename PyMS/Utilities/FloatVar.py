
from .IntegerVar import IntegerVar
from .UIKit import StringVar

class FloatVar(IntegerVar):
	def __init__(self, val='0', range=[None,None], exclude=[], callback=None, precision=None):
		self.precision = precision
		IntegerVar.__init__(self, val, range, exclude, callback)

	def editvalue(self, *_):
		if self.check:
			s = self.get(True)
			if s:
				try:
					if self.range[0] != None and self.range[0] >= 0 and self.get(True).startswith('-'):
						raise Exception()
					isfloat = self.get(True)
					s = self.get()
					if s in self.exclude:
						raise Exception()
					s = str(s)
					if self.precision and not s.endswith('.0') and len(s)-s.index('.')-1 > self.precision:
						raise Exception()
					if not isfloat.endswith('.') and not isfloat.endswith('.0') and s.endswith('.0'):
						s = s[:-2]
						s = int(s)
					else:
						s = float(s)
				except:
					s = self.lastvalid
				else:
					if self.range[0] != None and s < self.range[0]:
						s = self.range[0]
					elif self.range[1] != None and s > self.range[1]:
						s = self.range[1]
				self.set(s)
				if self.callback:
					self.callback(s)
			elif self.range[0] != None:
				s = self.range[0]
			else:
				s = self.defaultval
			self.lastvalid = s
		else:
			self.lastvalid = self.get(True)
			self.check = True

	def get(self, s=False):
		try:
			string = StringVar.get(self)
		except:
			string = ''
		if s:
			return string
		try:
			return float(string)
		except:
			return 0.0
