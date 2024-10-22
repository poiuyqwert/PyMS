
from __future__ import annotations

from . import CodeGenerator

from ...Utilities.UIKit import *
from ...Utilities import JSON
from ...Utilities.PyMSError import PyMSError

from dataclasses import dataclass

from typing import Self, Callable

@dataclass
class CodeGeneratorTypeRange(CodeGenerator.CodeGeneratorType):
	start: int = 0
	stop: int = 0
	step: int = 1

	@classmethod
	def type_name(cls) -> str:
		return 'range'

	@classmethod
	def from_json(cls, json: JSON.Object) -> Self:
		start = JSON.get(json, 'start', int)
		stop = JSON.get(json, 'stop', int)
		step = JSON.get(json, 'step', int)
		if step == 0:
			raise PyMSError('JSON', 'Invalid JSON (`step` has invalid value 0)')
		return cls(start, stop, step)

	def to_json(self) -> JSON.Object:
		json = CodeGenerator.CodeGeneratorType.to_json(self)
		json['start'] = self.start
		json['stop'] = self.stop,
		json['step'] = self.step
		return json

	def count(self) -> int:
		return len(list(range(self.start,self.stop+1,self.step)))

	def value(self, lookup_value: Callable[[str], int]) -> str:
		n = lookup_value('n')
		r = list(range(self.start,self.stop+1,self.step))
		if n >= len(r):
			return ''
		return str(r[n])

	def description(self):
		return '%d to %d, by adding %d' % (self.start,self.stop,self.step)

	def editor_type(self) -> Type[CodeGenerator.CodeGeneratorEditor]:
		return CodeGeneratorEditorRange

class CodeGeneratorEditorRange(CodeGenerator.CodeGeneratorEditor[CodeGeneratorTypeRange]):
	RESIZABLE = (False,False)

	def __init__(self, parent: Misc, generator: CodeGeneratorTypeRange):
		CodeGenerator.CodeGeneratorEditor.__init__(self, parent, generator)

		self.start = IntegerVar(0,[0,None])
		self.start.set(self.generator.start)
		self.stop = IntegerVar(0,[0,None])
		self.stop.set(self.generator.stop)
		self.step = IntegerVar(1,[1,None])
		self.step.set(self.generator.step)

		Label(self, text='From ').pack(side=LEFT)
		Entry(self, textvariable=self.start, width=5).pack(side=LEFT)
		Label(self, text=' to ').pack(side=LEFT)
		Entry(self, textvariable=self.stop, width=5).pack(side=LEFT)
		Label(self, text=', by adding ').pack(side=LEFT)
		Entry(self, textvariable=self.step, width=5).pack(side=LEFT)

	def save(self):
		self.generator.start = self.start.get()
		self.generator.stop = self.stop.get()
		self.generator.step = self.step.get()

CodeGenerator.register_type(CodeGeneratorTypeRange)
