
from Tkinter import StringVar

class IntegerVar(StringVar):
	def __init__(self, val='0', range=[None,None], exclude=[], callback=None, allow_hex=False, maxout=None):
		StringVar.__init__(self)
		self.check = True
		self.defaultval = val
		self.lastvalid = val
		self.set(val)
		self.range = range
		self.maxout = maxout
		self.exclude = exclude
		self.callback = callback
		self.allow_hex = allow_hex
		self.is_hex = False
		self.trace('w', self.editvalue)
		self.silence = False

	def editvalue(self, *_):
		#print self.check
		if self.check:
			#print s,self.range
			if self.get(True):
				refresh = True
				try:
					s = self.get()
					if self.range[0] != None and self.range[0] >= 0 and self.get(True).startswith('-'):
						#print '1'
						raise
					if s in self.exclude:
						#print '2'
						raise
					refresh = False
				except:
					#raise
					s = self.lastvalid
				else:
					if self.range[0] != None and s < self.range[0]:
						#print '3'
						s = self.range[0]
						refresh = True
					elif self.range[1] != None and s > self.range[1]:
						#print '4'
						if self.maxout != None:
							s = self.maxout
						else:
							s = self.range[1]
						refresh = True
				#print s
				if refresh:
					if self.is_hex:
						if s == 0:
							self.set('0x')
						else:
							self.set(hex(s))
					else:
						self.set(s)
				if self.callback and not self.silence:
					self.callback(s)
			elif self.range[0] != None:
				s = self.range[0]
			else:
				s = self.defaultval
			self.lastvalid = s
		else:
			self.lastvalid = self.get(True)
			self.check = True

	def set(self, value, silence=False):
		self.silence = silence
		StringVar.set(self, value)
		self.silence = False

	def get(self, s=False):
		string = StringVar.get(self)
		if s:
			return string
		if self.allow_hex and string.startswith('0x'):
			self.is_hex = True
			if string == '0x':
				return 0
			return int(string, 16)
		self.is_hex = False
		return int(string or 0)

	def setrange(self, range):
		self.range = list(range)
		value = self.get()
		new_value = max(range[0],min(range[1],value))
		if new_value != value:
			self.set(new_value)
