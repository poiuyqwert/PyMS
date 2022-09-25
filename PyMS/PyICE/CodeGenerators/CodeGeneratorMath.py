
from .CodeGenerator import CodeGeneratorType, CodeGeneratorEditor

from ...Utilities.utils import isstr
from ...Utilities.UIKit import *
from ...Utilities.PyMSError import PyMSError

import re

class CodeGeneratorEditorMath(CodeGeneratorEditor):
	RESIZABLE = (True,False)

	def __init__(self, parent, generator):
		CodeGeneratorEditor.__init__(self, parent, generator)

		self.math = StringVar()
		self.math.set(self.generator.math)

		Label(self, text='Math:', anchor=W).pack(side=TOP, fill=X)
		Entry(self, textvariable=self.math).pack(side=TOP, fill=X)

	def save(self):
		self.generator.math = self.math.get()

class CodeGeneratorTypeMath(CodeGeneratorType):
	TYPE = 'math'
	EDITOR = CodeGeneratorEditorMath

	@classmethod
	def validate(cls, save):
		return 'math' in save and isstr(save['math'])

	def __init__(self, save={}):
		self.math = save.get('math', '')

	def count(self):
		return None

	VARIABLE_RE = re.compile(r'\$([a-zA-Z0-9_]+)')
	MATH_RE = re.compile(r'^[0-9.+-/*() \t]+$')
	def value(self, lookup_value):
		math = CodeGeneratorTypeMath.VARIABLE_RE.sub(lambda m: str(lookup_value(m.group(1))), self.math)
		if not CodeGeneratorTypeMath.MATH_RE.match(math):
			raise PyMSError('Generate', "Invalid math expression '%s' (only numbers, +, -, /, *, (, ), and whitespace allowed)" % math)
		try:
			return eval(math)
		except:
			raise PyMSError('Generate', "Error evaluating math expression '%s'" % math, capture_exception=True)

	def description(self):
		return self.math

	def save(self):
		save = CodeGeneratorType.save(self)
		save['math'] = self.math
		return save

CodeGeneratorType.TYPES[CodeGeneratorTypeMath.TYPE] = CodeGeneratorTypeMath
