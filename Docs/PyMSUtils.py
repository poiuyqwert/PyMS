from textwrap import wrap

def fit(label, text):
	r = '%s: ' % label
	s = len(r)
	indent = False
	for l in wrap(text, 80 - s):
		if indent:
			r += ' ' * s
		else:
			indent = True
		r += l
		if len(l) != 80 - s:
			r += '\n'
	return r

class PyMSError(Exception):
	def __init__(self, type, error, line=None, code=None, warnings=[]):
		self.type = type
		self.error = error
		self.line = line
		if self.line != None:
			self.line += 1
		self.code = code
		self.warnings = warnings

	def __repr__(self):
		r = fit('%s Error' % self.type, self.error)
		if self.line:
			r += fit('    Line %s' % self.line, self.code)
		if self.warnings:
			for w in self.warnings:
				r += repr(w)
		return r[:-1]

class PyMSWarning(Exception):
	def __init__(self, type, warning, line=None, code=None, extra=None):
		self.type = type
		self.warning = warning
		self.line = line
		if self.line != None:
			self.line += 1
		self.code = code
		self.extra = extra

	def __repr__(self):
		r = fit('%s Warning' % self.type,self.warning)
		if self.line:
			r += fit('    Line %s' % self.line, self.code)
		return r[:-1]

class PyMSWarnList(Exception):
	def __init__(self, warnings):
		self.warnings = warnings

	def __repr__(self):
		r = ''
		for w in self.warnings:
			r += repr(w)
		return r[:-1]

class odict:
	def __init__(self, d=None):
		self.keynames = []
		self.dict = {}
		if d:
			self.keynames = list(d.keys)
			self.dict = dict(d.dict)

	def __delitem__(self, key):
		del self.dict[key]
		self.keynames.remove(key)

	def __setitem__(self, key, item):
		self.dict[key] = item
		if key not in self.keynames:
			self.keynames.append(key)

	def __getitem__(self, key):
		return self.dict[key]

	def __contains__(self, key):
		if key in self.keynames:
			return True
		return False

	def __len__(self):
		return len(self.keynames)

	def iteritems(self):
		iter = []
		for k in self.keynames:
			iter.append((k,self.dict[k]))
		return iter

	def iterkeys(self):
		return list(self.keynames)

	def peek(self):
		return (self.keynames[0],self.dict[self.keynames[0]])

	def keys(self):
		return list(self.keynames)

	def index(self, key):
		return self.keynames.index(key)

	def getkey(self, n):
		return self.keynames[n]

	def getitem(self, n):
		return self.dict[self.keynames[n]]

	def remove(self, n):
		self.keynames.remove(n)
		del self.dict[n]

	def __repr__(self):
		return '%s@%s' % (self.keynames,self.dict)