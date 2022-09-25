
from .CodeTooltip import AnimationTooltip, CommandTooltip

from ..FileFormats import IScriptBIN

from ..Utilities.CodeText import CodeText
from ..Utilities.EventPattern import *

import re
from copy import deepcopy

class IScriptCodeText(CodeText):
	def __init__(self, parent, ibin, ecallback=None, icallback=None, scallback=None, highlights=None):
		self.ibin = ibin
		self.boldfont = ('Courier New', -11, 'bold')
		if highlights:
			self.highlights = highlights
		else:
			self.highlights = {
				'Block':{'foreground':'#FF00FF','background':None,'font':None},
				'Keywords':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'HeaderStart':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				#'Types':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Animations':{'foreground':'#0000AA','background':None,'font':self.boldfont},
				'Commands':{'foreground':'#0000AA','background':None,'font':None},
				'Number':{'foreground':'#FF0000','background':None,'font':None},
				'Comment':{'foreground':'#008000','background':None,'font':None},
				'Operators':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Newline':{'foreground':None,'background':None,'font':None},
				'Error':{'foreground':None,'background':'#FF8C8C','font':None},
				'Warning':{'foreground':None,'background':'#FFC8C8','font':None},
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
				m = re.match('(\\s*)(#?)(.*)', self.get(head, '%s lineend' % head))
				if m.group(2):
					self.tk.call(self.text.orig, 'delete', '%s +%sc' % (head, len(m.group(1))))
				elif m.group(3):
					self.tk.call(self.text.orig, 'insert', head, '#')
				head = self.index('%s +1line' % head)
			self.update_range(self.index('%s linestart' % item[0]), self.index('%s lineend' % item[1]))

	def setupparser(self):
		comment = '(?P<Comment>#(?!#[gG][rR][pP]:|#[nN][aA][mM][eE]:)[^\\n]*$)'
		block = '^[ \\t]*(?P<Block>[^\x00:(),\\n]+)(?=:)'
		opcodes = []
		for o in IScriptBIN.OPCODES:
			opcodes.extend(o[0])
		cmds = '\\b(?P<Commands>%s)\\b' % '|'.join(opcodes)
		anims = ['IsId','Type']
		for h in IScriptBIN.HEADER:
			anims.extend(h)
		animations = '\\b(?P<Animations>%s)\\b' % '|'.join(anims)
		num = '\\b(?P<Number>\\d+|0x[0-9a-fA-F]+)\\b'
		operators = '(?P<Operators>[():,=])'
		kw = '(?P<Keywords>\\.headerend|##[gG][rR][pP]:|##[nN][aA][mM][eE]:|\\[NONE\\])'
		#types = '\\b(?P<Types>%s)\\b' % '|'.join(AIBIN.types)
		self.basic = re.compile('|'.join((comment, kw, block, cmds, animations, num, operators, '(?P<HeaderStart>\\.headerstart)', '(?P<Newline>\\n)')), re.S | re.M)
		AnimationTooltip(self)
		CommandTooltip(self)
		self.tags = deepcopy(self.highlights)

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
