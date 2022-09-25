
from .UIKit import StringVar

class IntegerVar(StringVar):
	class UpdateCase:
		internal = 0
		programmatic = 1
		user = 2
		both = (programmatic | user)

	def __init__(self, val=0, range=[None,None], exclude=[], callback=None, allow_hex=False, maxout=None, callback_when=UpdateCase.both, limit_when=UpdateCase.user):#, _tag=None):
		self.defaultval = val
		self.lastvalid = val
		self.range = range
		self.exclude = exclude
		self.callback = callback
		self.allow_hex = allow_hex
		self.maxout = maxout
		self.callback_when = callback_when
		self.limit_when = limit_when
		# self._tag = _tag
		StringVar.__init__(self, value=val)
		# self.set(val)
		self.is_hex = False
		self.trace('w', self.editvalue)
		self.update_case = IntegerVar.UpdateCase.user

	def editvalue(self, *_):
# 		if self._tag:
# 			print("""
# Tag: %s
#    Limit When: %s
# Callback When: %s
# Update Case: %s
#    Limit: %s
# Callback: %s
# """ % (self._tag, self.limit_when, self.callback_when, self.update_case, self.limit_when & self.update_case & IntegerVar.UpdateCase.user, self.callback_when & self.update_case))
		if self.limit_when & self.update_case & IntegerVar.UpdateCase.user:
			if self.get(True):
				refresh = True
				try:
					s = self.get()
					# if self._tag:
					# 	print(s, self.range)
					if self.range[0] != None and self.range[0] >= 0 and self.get(True).startswith('-'):
						# if self._tag:
						# 	print('at 1')
						raise Exception()
					if s in self.exclude:
						# if self._tag:
						#	 print('at 2')
						raise Exception()
					refresh = False
				except:
					#raise
					s = self.lastvalid
				else:
					if self.range[0] != None and s < self.range[0]:
						# if self._tag:
						# 	print('at 3')
						s = self.range[0]
						refresh = True
					elif self.range[1] != None and s > self.range[1]:
						# if self._tag:
						# 	print('at 4')
						if self.maxout != None:
							s = self.maxout
						else:
							s = self.range[1]
						refresh = True
				# if self._tag:
				# 	print(s, refresh)
				if refresh:
					if self.is_hex:
						if s == 0:
							self.set('0x', update_case=IntegerVar.UpdateCase.internal)
						else:
							self.set(hex(s), update_case=IntegerVar.UpdateCase.internal)
					else:
						self.set(s, update_case=IntegerVar.UpdateCase.internal)
				if self.callback and self.callback_when & self.update_case:
					self.callback(s)
			elif self.range[0] != None:
				s = self.range[0]
			else:
				s = self.defaultval
			self.lastvalid = s
		else:
			self.lastvalid = self.get(True)
			if self.callback and self.callback_when & self.update_case:
				self.callback(self.get())

	def set(self, value, update_case=UpdateCase.programmatic):
		# if self._tag:
		# 	print('Set %s %s' % (value, update_case))
		self.update_case = update_case
		if self.limit_when & update_case & IntegerVar.UpdateCase.programmatic:
			value = self.apply_limits(value)[1]
			# if self._tag:
			# 	print('Setting %s %s' % (value, update_case))
		StringVar.set(self, value)
		self.update_case = IntegerVar.UpdateCase.user
		# if self._tag:
		# 	print('Set %s done' % value)

	def get(self, s=False):
		try:
			string = StringVar.get(self)
		except:
			string = ''
		if s:
			return string
		if self.allow_hex and string.startswith('0x'):
			self.is_hex = True
			if string == '0x':
				return 0
			try:
				return int(string, 16)
			except:
				return 0
		self.is_hex = False
		try:
			return int(string or 0)
		except:
			return 0

	def setrange(self, range):
		self.range = list(range)
		value = self.get()
		new_value = self.apply_limits(value)
		if new_value != value:
			self.set(new_value)

	# Apply range limits to value
	def apply_limits(self, value):
		# if self._tag:
		# 	print(value, self.range)
		min,max = self.range
		if min != None and min >= 0 and self.get(True).startswith('-'):
			# if self._tag:
			# 	print('Invalid negative')
			value = self.lastvalid
		elif value in self.exclude:
			# if self._tag:
			# 	print('Exclude')
			value = self.lastvalid
		elif min != None and value < min:
			# if self._tag:
			# 	print('Minimum')
			value = min
		elif max != None and value > max:
			# if self._tag:
			# 	print('Maximum')
			if self.maxout != None:
				value = self.maxout
			else:
				value = max
		return value
