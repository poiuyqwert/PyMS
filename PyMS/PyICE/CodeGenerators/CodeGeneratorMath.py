
from . import CodeGenerator

from ...Utilities.UIKit import *
from ...Utilities import JSON
from ...Utilities.PyMSError import PyMSError

import re
from dataclasses import dataclass

from typing import Self, Callable

@dataclass
class CodeGeneratorTypeMath(CodeGenerator.CodeGeneratorType):
	math: str

	@classmethod
	def type_name(cls) -> str:
		return 'math'

	@classmethod
	def from_json(cls, json: JSON.Object) -> Self:
		return cls(JSON.get(json, 'math', str))

	def to_json(self) -> JSON.Object:
		json = CodeGenerator.CodeGeneratorType.to_json(self)
		json['math'] = self.math
		return json

	def count(self) -> int | None:
		return None

	VARIABLE_RE = re.compile(r'\$([a-zA-Z0-9_]+)')
	MATH_RE = re.compile(r'^[0-9.+-/*() \t]+$')
	def value(self, lookup_value: Callable[[str], int]) -> str:
		math = CodeGeneratorTypeMath.VARIABLE_RE.sub(lambda m: str(lookup_value(m.group(1))), self.math)
		if not CodeGeneratorTypeMath.MATH_RE.match(math):
			raise PyMSError('Generate', "Invalid math expression '%s' (only numbers, +, -, /, *, (, ), and whitespace allowed)" % math)
		try:
			return eval(math)
		except:
			raise PyMSError('Generate', "Error evaluating math expression '%s'" % math, capture_exception=True)

	def description(self) -> str:
		return self.math

	def editor_type(self) -> Type[CodeGenerator.CodeGeneratorEditor]:
		return CodeGeneratorEditorMath

class CodeGeneratorEditorMath(CodeGenerator.CodeGeneratorEditor[CodeGeneratorTypeMath]):
	RESIZABLE = (True,False)

	def __init__(self, parent: Misc, generator: CodeGeneratorTypeMath):
		CodeGenerator.CodeGeneratorEditor.__init__(self, parent, generator)

		self.math = StringVar()
		self.math.set(self.generator.math)

		Label(self, text='Math:', anchor=W).pack(side=TOP, fill=X)
		Entry(self, textvariable=self.math).pack(side=TOP, fill=X)

	def save(self):
		self.generator.math = self.math.get()

CodeGenerator.register_type(CodeGeneratorTypeMath)
