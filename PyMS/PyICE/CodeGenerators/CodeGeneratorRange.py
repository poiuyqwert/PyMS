
from .CodeGenerator import CodeGeneratorEditor, CodeGeneratorType

from ...Utilities.UIKit import *
from ...Utilities.IntegerVar import *

class CodeGeneratorEditorRange(CodeGeneratorEditor):
	RESIZABLE = (False,False)

	def __init__(self, parent, generator):
		CodeGeneratorEditor.__init__(self, parent, generator)

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

class CodeGeneratorTypeRange(CodeGeneratorType):
	TYPE = 'range'
	EDITOR = CodeGeneratorEditorRange

	@classmethod
	def validate(cls, save):
		return 'start' in save and isinstance(save['start'], int) \
			and 'stop' in save and isinstance(save['stop'], int) \
			and 'step' in save and isinstance(save['step'], int) and save['step'] != 0

	def __init__(self, save={}):
		self.start = save.get('start',0)
		self.stop = save.get('stop',0)
		self.step = save.get('step',1)

	def count(self):
		return len(range(self.start,self.stop+1,self.step))

	def value(self, lookup_value):
		n = lookup_value('n')
		r = range(self.start,self.stop+1,self.step)
		if n >= len(r):
			return ''
		return r[n]

	def description(self):
		return '%d to %d, by adding %d' % (self.start,self.stop,self.step)

	def save(self):
		save = CodeGeneratorType.save(self)
		save.update({
			'start': self.start,
			'stop': self.stop,
			'step': self.step
		})
		return save

CodeGeneratorType.TYPES[CodeGeneratorTypeRange.TYPE] = CodeGeneratorTypeRange
