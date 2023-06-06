
import sys

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from .PyMSWarning import PyMSWarning

class PyMSError(Exception):
	def __init__(self, type, error, line=None, code=None, warnings=[], capture_exception=False): # type: (str, str, int | None, str | None, list[PyMSWarning], bool) -> None
		self.type = type
		self.error = error
		self.line = line
		if self.line is not None:
			self.line += 1
		self.code = code
		self.warnings = warnings
		self.exception = None
		if capture_exception:
			self.exception = sys.exc_info()

	def repr(self): # type: () -> str
		r = '%s Error: %s' % (self.type, self.error)
		if self.line:
			r += '\n    Line %s: %s' % (self.line, self.code)
		return r

	def __repr__(self): # type: () -> str
		from .utils import fit
		r = fit('%s Error: ' % self.type, self.error)
		if self.line:
			if self.code is not None:
				r += fit('    Line %s: ' % self.line, self.code)
			else:
				r += '    Line %s' % self.line
		if self.warnings:
			for w in self.warnings:
				r += repr(w)
		return r

	def __str__(self): # type: () -> str
		return repr(self)
