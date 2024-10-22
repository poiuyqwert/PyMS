
from . import CodeGenerator

from ...Utilities.UIKit import *
from ...Utilities import JSON
from ...Utilities.PyMSError import PyMSError

import re
from dataclasses import dataclass

from typing import Self, Callable, Protocol

class CodeGeneratorTypeListRepeater(Protocol):
	@staticmethod
	def type_name() -> str:
		...

	@staticmethod
	def display_name() -> str:
		...

	def count(self, list_size: int) -> int | None:
		raise NotImplementedError(self.__class__.__name__ + '.count(list_size)')

	def index(self, list_size: int, n: int) -> int | None:
		raise NotImplementedError(self.__class__.__name__ + '.index(list_size, n)')

class CodeGeneratorTypeListRepeaterDont(CodeGeneratorTypeListRepeater):
	@staticmethod
	def type_name() -> str:
		return 'dont'

	@staticmethod
	def display_name() -> str:
		return "Don't Repeat"

	def count(self, list_size: int) -> int | None:
		return list_size

	def index(self, list_size: int, n: int) -> int | None:
		if n >= list_size:
			return None
		return n

class CodeGeneratorTypeListRepeaterRepeatOnce(CodeGeneratorTypeListRepeater):
	@staticmethod
	def type_name() -> str:
		return 'once'

	@staticmethod
	def display_name() -> str:
		return 'Once'

	def count(self, list_size: int) -> int | None:
		return list_size * 2

	def index(self, list_size: int, n: int) -> int | None:
		if n >= list_size * 2:
			return None
		return n % list_size

class CodeGeneratorTypeListRepeaterRepeatForever(CodeGeneratorTypeListRepeater):
	@staticmethod
	def type_name() -> str:
		return 'forever'

	@staticmethod
	def display_name() -> str:
		return 'Forever'

	def count(self, list_size: int) -> int | None:
		return None

	def index(self, list_size: int, n: int) -> int | None:
		return n % list_size

class CodeGeneratorTypeListRepeaterRepeatLast(CodeGeneratorTypeListRepeater):
	@staticmethod
	def type_name() -> str:
		return 'last_forever'

	@staticmethod
	def display_name() -> str:
		return 'Last Forever'

	def count(self, list_size: int) -> int | None:
		return None

	def index(self, list_size: int, n: int) -> int | None:
		return min(n, list_size-1)

class CodeGeneratorTypeListRepeaterRepeatInvertedOnce(CodeGeneratorTypeListRepeater):
	@staticmethod
	def type_name() -> str:
		return 'inverted_once'

	@staticmethod
	def display_name() -> str:
		return 'Inverted Once'

	def count(self, list_size: int) -> int | None:
		return list_size * 2 - 2

	def index(self, list_size: int, n: int) -> int | None:
		if n >= list_size * 2 - 2:
			return None
		if n >= list_size:
			return list_size-(n - list_size + 2)
		return n % list_size

class CodeGeneratorTypeListRepeaterRepeatInvertedForever(CodeGeneratorTypeListRepeater):
	@staticmethod
	def type_name() -> str:
		return 'inverted_forever'

	@staticmethod
	def display_name() -> str:
		return 'Inverted Forever'

	def count(self, list_size: int) -> int | None:
		return None

	def index(self, list_size: int, n: int) -> int | None:
		i = n % (list_size * 2 - 2)
		if i >= list_size:
			return list_size - (i - list_size + 2)
		return i

class CodeGeneratorTypeListRepeaterRepeatInvertedOnceRepeatEnd(CodeGeneratorTypeListRepeater):
	@staticmethod
	def type_name() -> str:
		return 'inverted_once_repeat_end'

	@staticmethod
	def display_name() -> str:
		return 'Inverted Once (Repeat End)'

	def count(self, list_size: int) -> int | None:
		return list_size * 2

	def index(self, list_size: int, n: int) -> int | None:
		if n >= list_size * 2:
			return None
		if n >= list_size:
			return list_size-(n % list_size + 1)
		return n % list_size

class CodeGeneratorTypeListRepeaterRepeatInvertedForeverRepeatEnd(CodeGeneratorTypeListRepeater):
	@staticmethod
	def type_name() -> str:
		return 'inverted_forever_repeat_end'

	@staticmethod
	def display_name() -> str:
		return 'Inverted Forever (Repeat Ends)'

	def count(self, list_size: int) -> int | None:
		return None

	def index(self, list_size: int, n: int) -> int | None:
		if (n // list_size) % 2:
			return list_size-(n % list_size + 1)
		return n % list_size

_REPEATERS: dict[str, CodeGeneratorTypeListRepeater] = {
	CodeGeneratorTypeListRepeaterDont.type_name(): CodeGeneratorTypeListRepeaterDont(),
	CodeGeneratorTypeListRepeaterRepeatOnce.type_name(): CodeGeneratorTypeListRepeaterRepeatOnce(),
	CodeGeneratorTypeListRepeaterRepeatForever.type_name(): CodeGeneratorTypeListRepeaterRepeatForever(),
	CodeGeneratorTypeListRepeaterRepeatLast.type_name(): CodeGeneratorTypeListRepeaterRepeatLast(),
	CodeGeneratorTypeListRepeaterRepeatInvertedOnce.type_name(): CodeGeneratorTypeListRepeaterRepeatInvertedOnce(),
	CodeGeneratorTypeListRepeaterRepeatInvertedForever.type_name(): CodeGeneratorTypeListRepeaterRepeatInvertedForever(),
	CodeGeneratorTypeListRepeaterRepeatInvertedOnceRepeatEnd.type_name(): CodeGeneratorTypeListRepeaterRepeatInvertedOnceRepeatEnd(),
	CodeGeneratorTypeListRepeaterRepeatInvertedForeverRepeatEnd.type_name(): CodeGeneratorTypeListRepeaterRepeatInvertedForeverRepeatEnd()
}

@dataclass
class CodeGeneratorTypeList(CodeGenerator.CodeGeneratorType):
	values: list[str]
	repeater: CodeGeneratorTypeListRepeater

	@classmethod
	def type_name(cls) -> str:
		return 'list'

	@classmethod
	def from_json(cls, json: JSON.Object) -> Self:
		values = JSON.get_array(json, 'list', str)
		repeater_name = JSON.get(json, 'repeater', str)
		if not repeater_name in _REPEATERS:
			raise PyMSError('JSON', 'Invalid JSON format (`repeater` has invalid value)')
		return cls(values, _REPEATERS[repeater_name])

	def to_json(self) -> JSON.Object:
		json = CodeGenerator.CodeGeneratorType.to_json(self)
		json['list'] = list(self.values)
		json['repeater'] = self.repeater.type_name()
		return json

	def count(self) -> int | None:
		return self.repeater.count(len(self.values))

	def value(self, lookup_value: Callable[[str], int]) -> str:
		n = self.repeater.index(len(self.values), lookup_value('n'))
		if n is None:
			return ''
		value = self.values[n]
		variable_re = re.compile(r'\$([a-zA-Z0-9_]+)')
		return variable_re.sub(lambda m: str(lookup_value(m.group(1))), value)

	def description(self):
		return 'Items from list: %s' % ', '.join(self.values)

	def editor_type(self) -> Type[CodeGenerator.CodeGeneratorEditor]:
		return CodeGeneratorEditorList

class CodeGeneratorEditorList(CodeGenerator.CodeGeneratorEditor[CodeGeneratorTypeList]):
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

	def __init__(self, parent: Misc, generator: CodeGeneratorTypeList):
		CodeGenerator.CodeGeneratorEditor.__init__(self, parent, generator)

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
		DropDown(self, self.repeater, [r.type_name() for r in CodeGeneratorEditorList.REPEATERS], width=20).pack(side=TOP, fill=X)

		self.text.insert(END, '\n'.join(generator.values))
		for n,repeater in enumerate(CodeGeneratorEditorList.REPEATERS):
			if repeater == self.generator.repeater:
				self.repeater.set(n)
				break

	def save(self):
		self.generator.list = self.text.get(1.0, END).rstrip('\n').split('\n')
		self.generator.repeater = CodeGeneratorEditorList.REPEATERS[self.repeater.get()]()

CodeGenerator.register_type(CodeGeneratorTypeList)
