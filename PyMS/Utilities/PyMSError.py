
import sys

class PyMSError(Exception):
	def __init__(self, type, error, line=None, code=None, warnings=[], capture_exception=False):
		self.type = type
		self.error = error
		self.line = line
		if self.line != None:
			self.line += 1
		self.code = code
		self.warnings = warnings
		self.exception = None
		if capture_exception:
			self.exception = sys.exc_info()

	def repr(self):
		r = '%s Error: %s' % (self.type, self.error)
		if self.line:
			r += '\n    Line %s: %s' % (self.line, self.code)
		return r

	def __repr__(self):
		from utils import fit
		r = fit('%s Error: ' % self.type, self.error)
		if self.line:
			if self.code != None:
				r += fit('    Line %s: ' % self.line, self.code)
			else:
				r += '    Line %s' % self.line
		if self.warnings:
			for w in self.warnings:
				r += repr(w)
		return r

	def __str__(self):
		return repr(self)
