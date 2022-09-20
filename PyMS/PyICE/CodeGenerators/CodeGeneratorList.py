
from .CodeGenerator import CodeGeneratorType, CodeGeneratorEditor

from ...Utilities.utils import isstr
from ...Utilities.UIKit import *
from ...Utilities.DropDown import DropDown

class CodeGeneratorTypeListRepeater(object):
	def count(self, list_size):
		raise NotImplementedError(self.__class__.__name__ + '.count(list_size)')

	def index(self, list_size, n):
		raise NotImplementedError(self.__class__.__name__ + '.index(list_size, n)')

class CodeGeneratorTypeListRepeaterDont(CodeGeneratorTypeListRepeater):
	TYPE = 'dont'
	NAME = "Don't Repeat"

	def count(self, list_size):
		return list_size

	def index(self, list_count, n):
		if n >= list_count:
			return None
		return n

class CodeGeneratorTypeListRepeaterRepeatOnce(CodeGeneratorTypeListRepeater):
	TYPE = 'once'
	NAME = 'Once'

	def count(self, list_size):
		return list_size * 2

	def index(self, list_size, n):
		if n >= list_size * 2:
			return None
		return n % list_size

class CodeGeneratorTypeListRepeaterRepeatForever(CodeGeneratorTypeListRepeater):
	TYPE = 'forever'
	NAME = 'Forever'

	def count(self, list_size):
		return None

	def index(self, list_size, n):
		return n % list_size

class CodeGeneratorTypeListRepeaterRepeatLast(CodeGeneratorTypeListRepeater):
	TYPE = 'last_forever'
	NAME = 'Last Forever'

	def count(self, list_size):
		return None

	def index(self, list_size, n):
		return min(n, list_size-1)

class CodeGeneratorTypeListRepeaterRepeatInvertedOnce(CodeGeneratorTypeListRepeater):
	TYPE = 'inverted_once'
	NAME = 'Inverted Once'

	def count(self, list_size):
		return list_size * 2 - 2

	def index(self, list_size, n):
		if n >= list_size * 2 - 2:
			return None
		if n >= list_size:
			return list_size-(n - list_size + 2)
		return n % list_size

class CodeGeneratorTypeListRepeaterRepeatInvertedForever(CodeGeneratorTypeListRepeater):
	TYPE = 'inverted_forever'
	NAME = 'Inverted Forever'

	def count(self, list_size):
		return None

	def index(self, list_size, n):
		i = n % (list_size * 2 - 2)
		if i >= list_size:
			return list_size - (i - list_size + 2)
		return i

class CodeGeneratorTypeListRepeaterRepeatInvertedOnceRepeatEnd(CodeGeneratorTypeListRepeater):
	TYPE = 'inverted_once_repeat_end'
	NAME = 'Inverted Once (Repeat End)'

	def count(self, list_size):
		return list_size * 2

	def index(self, list_size, n):
		if n >= list_size * 2:
			return None
		if n >= list_size:
			return list_size-(n % list_size + 1)
		return n % list_size

class CodeGeneratorTypeListRepeaterRepeatInvertedForeverRepeatEnd(CodeGeneratorTypeListRepeater):
	TYPE = 'inverted_forever_repeat_end'
	NAME = 'Inverted Forever (Repeat Ends)'

	def count(self, list_size):
		return None

	def index(self, list_size, n):
		if (n / list_size) % 2:
			return list_size-(n % list_size + 1)
		return n % list_size

class CodeGeneratorEditorList(CodeGeneratorEditor):
	RESIZABLE = (True,True)
	REPEATERS = (
		CodeGeneratorTypeListRepeaterDont,
		CodeGeneratorTypeListRepeaterRepeatOnce,
		CodeGeneratorTypeListRepeaterRepeatForever,
		CodeGeneratorTypeListRepeaterRepeatLast,
		CodeGeneratorTypeListRepeaterRepeatInvertedOnce,
		CodeGeneratorTypeListRepeaterRepeatInvertedForever,
		CodeGeneratorTypeListRepeaterRepeatInvertedOnceRepeatEnd,
		CodeGeneratorTypeListRepeaterRepeatInvertedForeverRepeatEnd
	)

	def __init__(self, parent, generator):
		CodeGeneratorEditor.__init__(self, parent, generator)

		Label(self, text='Values:', anchor=W).pack(side=TOP, fill=X)
		textframe = Frame(self, bd=2, relief=SUNKEN)
		hscroll = Scrollbar(textframe, orient=HORIZONTAL)
		vscroll = Scrollbar(textframe)
		self.text = Text(textframe, height=1, bd=0, undo=1, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0)
		self.text.grid(sticky=NSEW)
		# self.text.bind(Ctrl.a, lambda e: self.after(1, self.selectall))
		hscroll.config(command=self.text.xview)
		hscroll.grid(sticky=EW)
		vscroll.config(command=self.text.yview)
		vscroll.grid(sticky=NS, row=0, column=1)
		textframe.grid_rowconfigure(0, weight=1)
		textframe.grid_columnconfigure(0, weight=1)
		textframe.pack(side=TOP, expand=1, fill=BOTH)

		self.repeater = IntVar()

		Label(self, text='Repeat:', anchor=W).pack(side=TOP, fill=X)
		DropDown(self, self.repeater, [r.NAME for r in CodeGeneratorEditorList.REPEATERS], width=20).pack(side=TOP, fill=X)

		self.text.insert(END, '\n'.join(generator.list))
		for n,repeater in enumerate(CodeGeneratorEditorList.REPEATERS):
			if repeater.TYPE == self.generator.repeater.TYPE:
				self.repeater.set(n)
				break

	def save(self):
		self.generator.list = self.text.get(1.0, END).rstrip('\n').split('\n')
		self.generator.repeater = CodeGeneratorEditorList.REPEATERS[self.repeater.get()]()

class CodeGeneratorTypeList(CodeGeneratorType):
	TYPE = 'list'
	EDITOR = CodeGeneratorEditorList
	REPEATERS = {
		CodeGeneratorTypeListRepeaterDont.TYPE: CodeGeneratorTypeListRepeaterDont,
		CodeGeneratorTypeListRepeaterRepeatOnce.TYPE: CodeGeneratorTypeListRepeaterRepeatOnce,
		CodeGeneratorTypeListRepeaterRepeatForever.TYPE: CodeGeneratorTypeListRepeaterRepeatForever,
		CodeGeneratorTypeListRepeaterRepeatLast.TYPE: CodeGeneratorTypeListRepeaterRepeatLast,
		CodeGeneratorTypeListRepeaterRepeatInvertedOnce.TYPE: CodeGeneratorTypeListRepeaterRepeatInvertedOnce,
		CodeGeneratorTypeListRepeaterRepeatInvertedForever.TYPE: CodeGeneratorTypeListRepeaterRepeatInvertedForever,
		CodeGeneratorTypeListRepeaterRepeatInvertedOnceRepeatEnd.TYPE: CodeGeneratorTypeListRepeaterRepeatInvertedOnceRepeatEnd,
		CodeGeneratorTypeListRepeaterRepeatInvertedForeverRepeatEnd.TYPE: CodeGeneratorTypeListRepeaterRepeatInvertedForeverRepeatEnd
	}

	@classmethod
	def validate(cls, save):
		if not 'list' in save and isinstance(save['list'], list) \
				or not 'repeater' in save or not save['repeater'] in CodeGeneratorTypeList.REPEATERS:
			return False
		for val in save['list']:
			if not isstr(val):
				return False
		return True

	def __init__(self, save={}):
		self.list = save.get('list', [])
		self.repeater = CodeGeneratorTypeList.REPEATERS.get(save.get('repeater'), CodeGeneratorTypeListRepeaterDont)()

	def count(self):
		return self.repeater.count(len(self.list))

	def value(self, lookup_value):
		n = self.repeater.index(len(self.list), lookup_value('n'))
		if n == None:
			return ''
		value = self.list[n]
		variable_re = re.compile(r'\$([a-zA-Z0-9_]+)')
		return variable_re.sub(lambda m: str(lookup_value(m.group(1))), value)

	def description(self):
		return 'Items from list: %s' % ', '.join(self.list)

	def save(self):
		save = CodeGeneratorType.save(self)
		save['list'] = list(self.list)
		save['repeater'] = self.repeater.TYPE
		return save

CodeGeneratorType.TYPES[CodeGeneratorTypeList.TYPE] = CodeGeneratorTypeList
