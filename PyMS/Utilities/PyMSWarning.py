
class PyMSWarning(Exception):
	def __init__(self, type, warning, line=None, code=None, extra=None, level=0, id=None, sub_warnings=None): # type: (str, str, int | None, str | None, str | None, int, int | None, list[PyMSWarning] | None) -> None
		self.type = type
		self.warning = warning
		self.line = line
		if self.line is not None:
			self.line += 1
		self.code = code
		self.extra = extra
		self.level = level
		self.id = id
		self.sub_warnings = [] if not sub_warnings else sub_warnings

	def repr(self): # type: () -> str
		from .utils import fit
		r = fit('%s Warning%s: ' % (self.type, ' (%s)' % self.id if self.id else ''), self.warning, end=True)
		if self.line and self.code:
			r += fit('    Line %s: ' % self.line, self.code, end=True)
		for w in self.sub_warnings:
			r += w.repr()
		return r

	def __repr__(self): # type: () -> str
		from .utils import fit
		r = fit('%s Warning%s: ' % (self.type, ' (%s)' % self.id if self.id else ''), self.warning)
		if self.line and self.code:
			r += fit('    Line %s: ' % self.line, self.code)
		for w in self.sub_warnings:
			r += repr(w)
		return r[:-1]

class PyMSWarnList(Exception):
	def __init__(self, warnings): # type: (list[PyMSWarning]) -> None
		self.warnings = warnings

	def __repr__(self): # type: () -> str
		r = ''
		for w in self.warnings:
			r += repr(w)
		return r[:-1]
