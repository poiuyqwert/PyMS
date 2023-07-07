
from .Delegates import MainDelegate
from .Tooltips import ConditionsTooltip, ActionsTooltip, TrigPlugActionsTooltip

from ..FileFormats.TRG import TRG, Conditions, Actions

from ..Utilities.UIKit import *

from copy import deepcopy
import re

class TRGCodeText(CodeText):
	def __init__(self, parent: Misc, delegate: MainDelegate, ecallback=None, highlights=None, state: WidgetState = NORMAL) -> None:
		self.delegate = delegate
		self.boldfont = ('Courier New', -11, 'bold')
		self.re: re.Pattern | None = None
		if highlights:
			self.highlights = highlights
		else:
			self.highlights = {
				'Comment':{'foreground':'#008000','background':None,'font':None},
				'Headers':{'foreground':'#FF00FF','background':None,'font':self.boldfont},
				'Conditions':{'foreground':'#000000','background':'#EBEBEB','font':None},
				'Actions':{'foreground':'#000000','background':'#E1E1E1','font':None},
				#'TrigPlugConditions':{'foreground':'#000000','background':'#EBEBFF','font':None},
				'TrigPlugActions':{'foreground':'#000000','background':'#E1E1FF','font':None},
				'DynamicConditions':{'foreground':'#000000','background':'#FFEBEB','font':None},
				'DynamicActions':{'foreground':'#000000','background':'#FFE1E1','font':None},
				'Constants':{'foreground':'#FF963C','background':None,'font':None},
				'ConstDef':{'foreground':'#FF963C','background':None,'font':None},
				'Keywords':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Number':{'foreground':'#FF0000','background':None,'font':None},
				'TBLFormat':{'foreground':None,'background':'#E6E6E6','font':None},
				'Operators':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Newline':{'foreground':None,'background':None,'font':None},
				'Error':{'foreground':None,'background':'#FF8C8C','font':None},
				'Warning':{'foreground':None,'background':'#FFC8C8','font':None},
			}
		CodeText.__init__(self, parent, ecallback, state=state)

	def setedit(self) -> None:
		if self.ecallback is not None:
			self.ecallback()
		self.edited = True

	def setupparser(self) -> None:
		comment = r'(?P<Comment>#[^\n]*$)'
		header = r'^[ \t]*(?P<Headers>Trigger(?=\([^\n]+\):)|Conditions(?=(?: \w+)?:)|Actions(?=(?: \w+)?:)|Constant(?= \w+:)|String(?= \d+:)|Property(?= \d+:))'
		conditions = r'\b(?P<Conditions>%s)\b' % '|'.join([condition.name for condition in Conditions._CONDITION_DEFINITIONS_REGISTRY])
		actions = r'\b(?P<Actions>%s)\b' % '|'.join([action.name for action in Actions._ACTION_DEFINITIONS_REGISTRY])
		#trigplugconditions = r'\b(?P<TrigPlugConditions>%s)\b' % '|'.join([x for x in AIBIN.AIBIN.short_labels if x is not None])
		# trigplugactions = r'\b(?P<TrigPlugActions>%s)\b' % '|'.join([x for x in TRG.TRG.new_actions if x is not None])
		constants = r'(?P<Constants>\{\w+\})'
		constdef = r'(?<=Constant )(?P<ConstDef>\w+)(?=:)'
		# keywords = r'\b(?P<Keywords>%s)(?=[ \),])' % '|'.join(TRG.keywords)
		tblformat = r'(?P<TBLFormat><0*(?:25[0-5]|2[0-4]\d|1?\d?\d)?>)'
		num = r'\b(?P<Number>\d+|x(?:2|4|8|16|32)|0x[0-9a-fA-F]+)\b'
		operators = r'(?P<Operators>[():,\-])'
		# self.basic = '|'.join((comment, header, keywords, conditions, actions, trigplugactions, constants, constdef, tblformat, num, operators))
		self.basic = '|'.join((comment, header, conditions, actions, constants, constdef, tblformat, num, operators))
		ConditionsTooltip(self)
		ActionsTooltip(self)
		TrigPlugActionsTooltip(self)
		self.tags = deepcopy(self.highlights)

	def colorize(self) -> None:
		if not self.re:
			self.re = re.compile('|'.join((self.basic,r'(?P<Newline>\n)')), re.M)
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
				for tag in list(self.tags.keys()):
					if tag != 'Selection':
						self.tag_remove(tag, mark, next)
				chars = chars + line
				m = self.re.search(chars)
				while m:
					for key, value in list(m.groupdict().items()):
						if value is not None:
							a, b = m.span(key)
							self.tag_add(key, head + '+%dc' % a, head + '+%dc' % b)
					m = self.re.search(chars, m.end())
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
