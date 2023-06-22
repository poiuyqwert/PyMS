
from .CodeTooltip import CodeTooltip
from .Constants import SIGNED_INT

from ..Utilities.UIKit import *

import re
from copy import deepcopy

from typing import Callable, cast

class LOCodeText(CodeText):
	def __init__(self, parent: Misc, ecallback: Callable[[], None] | None = None, icallback=None, highlights: Highlights | None = None, state: WidgetState = NORMAL) -> None:
		boldfont = Font.fixed().bolded()
		if highlights:
			self.highlights = highlights
		else:
			self.highlights = {
				'Comment':{'foreground':'#008000','background':None,'font':None},
				'Header':{'foreground':'#FF00FF','background':None,'font':boldfont},
				'Number':{'foreground':'#FF0000','background':None,'font':None},
				'Operators':{'foreground':'#0000FF','background':None,'font':boldfont},
				'Newline':{'foreground':None,'background':None,'font':None},
				'Error':{'foreground':None,'background':'#FF8C8C','font':None},
				'Warning':{'foreground':None,'background':'#FFC8C8','font':None},
			}
		CodeText.__init__(self, parent, ecallback, icallback, state=state)

	def setedit(self) -> None:
		if self.ecallback is not None:
			self.ecallback()
		self.edited = True

	def setupparser(self) -> None:
		comment = '(?P<Comment>#[^\\n]*$)'
		header = '^(?P<Header>Frame:)(?=[ \\t]*(#[^\\n]*)?)'
		num = '(?<!\\w)(?P<Number>%s)(?!\\w)' % SIGNED_INT
		operators = '(?P<Operators>[():,])'
		self.basic = re.compile('|'.join((comment, header, num, operators, '(?P<Newline>\\n)')), re.M)
		CodeTooltip(cast(Text, self))
		self.tags = deepcopy(self.highlights)

	def colorize(self) -> None:
		next = '1.0'
		while next:
			item = self.tag_nextrange("Update", next)
			if not item:
				break
			head, tail = item
			self.tag_remove('Newline', head, tail)
			item = self.tag_prevrange('Newline', head)
			if item:
				head = item[1] + ' linestart'
			else:
				head = "1.0"
			chars = ""
			next = head
			lines_to_get = 1
			ok = False
			while not ok:
				mark = next
				next = self.index(mark + '+%d lines linestart' % lines_to_get)
				lines_to_get = min(lines_to_get * 2, 100)
				ok = 'Newline' in self.tag_names(next + '-1c')
				line = self.get(mark, next)
				if not line:
					return
				for tag in list(self.tags.keys()):
					if tag != 'Selection':
						self.tag_remove(tag, mark, next)
				chars = chars + line
				m = self.basic.search(chars)
				while m:
					for key, value in list(m.groupdict().items()):
						if value is not None:
							a, b = m.span(key)
							self.tag_add(key, head + '+%dc' % a, head + '+%dc' % b)
					m = self.basic.search(chars, m.end())
				if 'Newline' in self.tag_names(next + '-1c'):
					head = next
					chars = ''
				else:
					ok = False
				if not ok:
					self.tag_add('Update', next)
				self.update()
				if not self.coloring:
					return
