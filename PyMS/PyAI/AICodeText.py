
from .CodeTooltip import *

from ..FileFormats import AIBIN

from ..Utilities.CodeText import CodeText

import re, copy

class AICodeText(CodeText):
	def __init__(self, parent, ai, ecallback=None, icallback=None, scallback=None, highlights=None):
		self.ai = ai
		self.boldfont = ('Courier New', -11, 'bold')
		if highlights:
			self.highlights = highlights
		else:
			self.highlights = {
				'Block':{'foreground':'#FF00FF','background':None,'font':None},
				'Keywords':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Types':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Commands':{'foreground':'#0000AA','background':None,'font':None},
				'Number':{'foreground':'#FF0000','background':None,'font':None},
				'TBLFormat':{'foreground':None,'background':'#E6E6E6','font':None},
				'InfoComment':{'foreground':'#FF963C','background':None,'font':None},
				'MultiInfoComment':{'foreground':'#FF963C','background':None,'font':None},
				'Comment':{'foreground':'#008000','background':None,'font':None},
				'AIID':{'foreground':'#FF00FF','background':None,'font':self.boldfont},
				'HeaderString':{'foreground':'#FF0000','background':None,'font':self.boldfont},
				'HeaderFlags':{'foreground':'#8000FF','background':None,'font':self.boldfont},
				'Operators':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Newline':{'foreground':None,'background':None,'font':None},
				'Error':{'foreground':None,'background':'#FF8C8C','font':None},
				'Warning':{'foreground':None,'background':'#FFC8C8','font':None},
				'Directives':{'foreground':'#0000FF','background':None,'font':self.boldfont}
			}
		CodeText.__init__(self, parent, ecallback, icallback, scallback)
		self.text.bind(Ctrl.q, self.commentrange)

	def setedit(self):
		if self.ecallback != None:
			self.ecallback()
		self.edited = True

	def commentrange(self, e=None):
		item = self.tag_ranges('Selection')
		if item:
			head,tail = self.index('%s linestart' % item[0]),self.index('%s linestart' % item[1])
			while self.text.compare(head, '<=', tail):
				m = re.match(r'(\s*)(#?)(.*)', self.get(head, '%s lineend' % head))
				if m.group(2):
					self.tk.call(self.text.orig, 'delete', '%s +%sc' % (head, len(m.group(1))))
				elif m.group(3):
					self.tk.call(self.text.orig, 'insert', head, '#')
				head = self.index('%s +1line' % head)
			self.update_range(self.index('%s linestart' % item[0]), self.index('%s lineend' % item[1]))

	def setupparser(self):
		infocomment = '(?P<InfoComment>\\{[^\\n]+\\})'
		multiinfocomment = '^[ \\t]*(?P<MultiInfoComment>\\{[ \\t]*(?:\\n[^}]*)?\\}?)$'
		comment = '(?P<Comment>#[^\\n]*$)'
		header = '^(?P<AIID>[^\n\x00,():]{4})(?=\\([^#]+,[^#]+,[^#]+\\):.+$)'
		header_string = '\\b(?P<HeaderString>\\d+)(?=,[^#]+,[^#]+\\):.+$)'
		header_flags = '\\b(?P<HeaderFlags>[01]{3})(?=,[^#]+\\):.+$)'
		block = '^[ \\t]*(?P<Block>--[^\x00:(),\\n]+--)(?=.+$)'
		cmds = '\\b(?P<Commands>%s)\\b' % '|'.join(AIBIN.AIBIN.short_labels)
		num = '\\b(?P<Number>\\d+)\\b'
		tbl = r'(?P<TBLFormat><0*(?:25[0-5]|2[0-4]\d|1?\d?\d)?>)'
		operators = '(?P<Operators>[():,=])'
		kw = '\\b(?P<Keywords>extdef|aiscript|bwscript|LessThan|GreaterThan)\\b'
		types = '\\b(?P<Types>%s)\\b' % '|'.join(AIBIN.types)
		directives = r'(?P<Directives>@(?:spellcaster|supress_all|suppress_next_line))\b'
		self.basic = re.compile('|'.join((infocomment, multiinfocomment, comment, header, header_string, header_flags, block, cmds, num, tbl, operators, kw, types, directives, '(?P<Newline>\\n)')), re.S | re.M)
		CommandCodeTooltip(self.text,self.ai)
		TypeCodeTooltip(self.text,self.ai)
		StringCodeTooltip(self.text,self.ai)
		FlagCodeTooltip(self.text,self.ai)
		DirectiveTooltip(self.text,self.ai)
		self.tags = copy.deepcopy(self.highlights)

	def colorize(self):
		next = '1.0'
		while True:
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
				for tag in self.tags.keys():
					if tag != 'Selection':
						self.tag_remove(tag, mark, next)
				chars = chars + line
				m = self.basic.search(chars)
				while m:
					for key, value in m.groupdict().items():
						if value != None:
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
