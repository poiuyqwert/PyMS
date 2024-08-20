
from .HelpContent import TYPE_HELP, CMD_HELP
from .AICodeText import AICodeText
from .FindReplaceDialog import FindReplaceDialog
from .CodeColors import CodeColors
from .Config import PyAIConfig
from .Delegates import MainDelegate

from ..FileFormats.AIBIN import AIBIN
from ..FileFormats import TBL

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Assets
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.WarningDialog import WarningDialog
from ..Utilities import IO

import re

class CodeEditDialog(PyMSDialog):
	def __init__(self, parent: AnyWindow, delegate: MainDelegate, config: PyAIConfig, ids: list[str]):
		self.delegate = delegate
		self.config_ = config
		self.ids = ids
		self.decompile = ''
		self.file: str | None = None
		self.autocomptext = list(TYPE_HELP.keys())
		self.completing = False
		self.complete = [None, 0]
		t = ''
		if ids:
			t = ', '.join(ids[:5])
			if len(ids) > 5:
				t += '...'
			t += ' - '
		t += 'AI Script Editor'
		PyMSDialog.__init__(self, parent, t, grabwait=False)
		self.findwindow: FindReplaceDialog | None = None

	def widgetize(self) -> Widget:
		self.bind(Alt.Left(), lambda _: self.gotosection(0))
		self.bind(Alt.Right(), lambda _: self.gotosection(1))
		self.bind(Alt.Up(), lambda _: self.gotosection(2))
		self.bind(Alt.Down(), lambda _: self.gotosection(3))

		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s)
		self.toolbar.add_button(Assets.get_image('test'), self.test, 'Test Code', Ctrl.t)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export Code', Ctrl.e)
		self.toolbar.add_button(Assets.get_image('saveas'), self.exportas, 'Export As...', Ctrl.Alt.a)
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Code', Ctrl.i)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('find'), self.find, 'Find/Replace', Ctrl.f)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('colors'), self.colors, 'Color Settings', Ctrl.Alt.c)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.asc3topyai, 'Compile ASC3 to PyAI', Ctrl.Alt.p)
		self.toolbar.add_button(Assets.get_image('debug'), self.debuggerize, 'Debuggerize your code', Ctrl.d)
		self.toolbar.pack(fill=X, padx=2, pady=2)

		self.text = AICodeText(self, self.delegate.get_ai_bin(), self.edited, highlights=self.delegate.get_highlights())
		self.text.pack(fill=BOTH, expand=1, padx=1, pady=1)
		self.text.icallback = self.statusupdate
		self.text.scallback = self.statusupdate
		self.text.acallback = self.autocomplete

		self.status = StringVar()
		if self.ids:
			self.status.set("Original ID's: " + ', '.join(self.ids))
		self.scriptstatus = StringVar()
		self.scriptstatus.set('Line: 1  Column: 0  Selected: 0')

		statusbar = StatusBar(self)
		statusbar.add_label(self.status, weight=1)
		self.editstatus = statusbar.add_icon(Assets.get_image('save.gif'))
		statusbar.add_label(self.scriptstatus, weight=1)
		statusbar.pack(side=BOTTOM, fill=X)

		if self.ids:
			self.after(1, self.load)

		return self.text

	def setup_complete(self) -> None:
		self.config_.windows.code_edit.load_size(self)

	# TODO: Cleanup
	def gotosection(self, i: int) -> None:
		c = [self.text.tag_prevrange, self.text.tag_nextrange][i % 2]
		t = [('Error','Warning'),('AIID','Block')][i > 1]
		a = c(t[0], INSERT)
		b = c(t[1], INSERT)
		s = None
		if a:
			if not b or self.text.compare(a[0], '<' if i % 2 else '>', b[0]):
				s = a
			else:
				s = b
		elif b:
			s = b
		if s:
			self.text.see(s[0])
			self.text.mark_set(INSERT, s[0])

	def autocomplete(self) -> bool:
		i = self.text.tag_ranges('Selection')
		if i and '\n' in self.text.get(*i):
			return False
		self.completing = True
		self.text.taboverride = ' (,)'
		def docomplete(s, e, v, t):
			ss = '%s+%sc' % (s,len(t))
			se = '%s+%sc' % (s,len(v))
			self.text.delete(s, ss)
			self.text.insert(s, v)
			self.text.tag_remove('Selection', '1.0', END)
			self.text.tag_add('Selection', ss, se)
			if self.complete[0] is None:
				self.complete = [t, 1, s, se]
			else:
				self.complete[1] += 1
				self.complete[3] = se
		if self.complete[0] is not None:
			t,f,s,e = self.complete
		else:
			s,e = self.text.index('%s -1c wordstart' % INSERT),self.text.index('%s -1c wordend' % INSERT)
			t,f = self.text.get(s,e),0
			prefix = self.text.get('%s -1c' % s, s)
			if prefix == '@':
				s = self.text.index('%s -1c' % s)
				t = prefix + t
		if t and t[0].lower() in 'abcdefghijklmnopqrstuvwxyz@':
			ac = list(self.autocomptext)
			m = re.match('\\A\\s*[a-z\\{]+\\Z',t)
			if not m:
				for _,c in CMD_HELP.items():
					ac.extend(list(c.keys()))
				ac.extend(('extdef','aiscript','bwscript','LessThan','GreaterThan'))
			for ns in self.delegate.get_tbl().strings[:228]:
				cs = ns.split('\x00')
				if cs[1] != '*':
					cs = TBL.decompile_string('\x00'.join(cs[:2]), '\x0A\x28\x29\x2C')
				else:
					cs = TBL.decompile_string(cs[0], '\x0A\x28\x29\x2C')
				if not cs in ac:
					ac.append(cs)
			for i in range(61):
				cs = TBL.decompile_string(self.delegate.get_tbl().strings[self.delegate.get_upgrades_dat().get_entry(i).label - 1].split('\x00',1)[0].strip(), '\x0A\x28\x29\x2C')
				if not cs in ac:
					ac.append(cs)
			for i in range(44):
				cs = TBL.decompile_string(self.delegate.get_tbl().strings[self.delegate.get_tech_dat().get_entry(i).label - 1].split('\x00',1)[0].strip(), '\x0A\x28\x29\x2C')
				if not cs in ac:
					ac.append(cs)
			aiid = ''
			item = self.text.tag_prevrange('AIID', INSERT)
			if item:
				aiid = self.text.get(*item)
			head = '1.0'
			while True:
				item = self.text.tag_nextrange('Block', head)
				if not item:
					break
				head,tail = item
				block = ''
				if aiid:
					item = self.text.tag_prevrange('AIID', head)
					if item:
						id = self.text.get(*item)
						if id != aiid:
							block = id + ':'
				block += self.text.get('%s +2c' % head,'%s -2c' % tail)
				if not block in ac:
					ac.append(block)
				head = tail
			ac.extend(('@spellcaster','@supress_all','@suppress_next_line'))
			ac.sort()
			if m:
				x = []
				for _,c in CMD_HELP.items():
					x.extend(list(c.keys()))
				x.sort()
				ac = x + ac
			r = False
			matches = []
			for v in ac:
				if v and v.lower().startswith(t.lower()):
					matches.append(v)
			if matches:
				if f < len(matches):
					docomplete(s,e,matches[f],t)
					self.text.taboverride = ' (,)'
				elif self.complete[0] is not None:
					docomplete(s,e,t,t)
					self.complete[1] = 0
				r = True
			self.after(1, self.completed)
			return r
		return False

	def completed(self) -> None:
		self.completing = False

	def statusupdate(self) -> None:
		if not self.completing:
			self.text.taboverride = None
			self.complete = [None, 0]
		i = self.text.index(INSERT).split('.') + [0]
		item = self.text.tag_ranges('Selection')
		if item:
			i[2] = len(self.text.get(*item))
		self.scriptstatus.set('Line: %s  Column: %s  Selected: %s' % tuple(i))

	def edited(self) -> None:
		if not self.completing:
			self.text.taboverride = None
			self.complete = [None, 0]
		self.editstatus['state'] = NORMAL
		if self.file:
			self.title('AI Script Editor [*%s*]' % self.file)

	def cancel(self, _: Event | None = None) -> None:
		if self.text.edited:
			save = MessageBox.askquestion(parent=self, title='Save Code?', message="Would you like to save the code?", default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return
				self.save()
		self.ok()

	def save(self, _: Event | None = None) -> None:
		code = self.text.get('1.0', END)
		if self.delegate.save_code(code, self):
			self.text.edited = False
			self.editstatus['state'] = DISABLED

	def test(self, _: Event | None = None) -> None:
		aibin = AIBIN.AIBIN(AIBIN.BWBIN())
		code = self.text.get('1.0', END)
		parse_context = self.delegate.get_parse_context(code)
		try:
			aibin.compile(parse_context)
			# for id in list(i.ais.keys()):
			# 	if id in self.delegate.get_ai_bin().externaljumps[0]:
			# 		for _,l in self.delegate.get_ai_bin().externaljumps[0].items():
			# 			for cid in l:
			# 				if not cid in i.ais:
			# 					raise PyMSError('Interpreting',"You can't edit scripts (%s) that are referenced externally without editing the scripts with the external references (%s) at the same time." % (id,cid))
		except PyMSError as e:
			if e.line is not None:
				self.text.see('%s.0' % e.line)
				self.text.tag_add('Error', '%s.0' % e.line, '%s.end' % e.line)
			if e.warnings:
				for w in e.warnings:
					if w.line is not None:
						self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			ErrorDialog(self, e)
			return
		if parse_context.warnings:
			c = False
			for w in parse_context.warnings:
				if w.line is not None:
					if not c:
						self.text.see('%s.0' % w.line)
						c = True
					self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			WarningDialog(self, parse_context.warnings, True)
		else:
			MessageBox.askquestion(parent=self, title='Test Completed', message='The code compiles with no errors or warnings.', type=MessageBox.OK)

	def export(self, _: Event | None = None) -> None:
		if not self.file:
			self.exportas()
		else:
			f = open(self.file, 'w')
			f.write(self.text.get('1.0', END))
			f.close()
			self.title('AI Script Editor [%s]' % self.file)

	def exportas(self, _: Event | None = None) -> None:
		file = self.config_.last_path.txt.ai.select_save(self)
		if not file:
			return
		self.file = file
		self.export()

	def iimport(self, _: Event | None = None) -> None:
		iimport = self.config_.last_path.txt.ai.select_save(self)
		if iimport:
			try:
				f = open(iimport, 'r')
				self.text.delete('1.0', END)
				self.text.insert('1.0', f.read())
				self.text.edit_reset()
				f.close()
			except:
				ErrorDialog(self, PyMSError('Import',"Could not import file '%s'" % iimport))

	def find(self, _: Event | None = None) -> None:
		if not self.findwindow:
			self.findwindow = FindReplaceDialog(self)
			self.bind(Key.F3(), self.findwindow.findnext)
		elif self.findwindow.state() == 'withdrawn':
			self.findwindow.deiconify()
		self.findwindow.focus_set()

	def colors(self, _: Event | None = None) -> None:
		c = CodeColors(self, self.text.tags)
		if c.cont:
			self.text.setup(c.cont)
			self.delegate.set_highlights(c.cont)

	def asc3topyai(self, _: Event | None = None) -> None:
		beforeheader = ''
		header = '### NOTE: There is no way to determine the scripts flags or if it is a BW script or not!\n###       please update the header below appropriately!\n%s(%s, 111, %s): # Script Name: %s'
		headerinfo = [None,None,None,None]
		data = ''
		for line in self.text.text.get('1.0',END).split('\n'):
			if line.lstrip().startswith(';'):
				if not None in headerinfo:
					data += line.replace(';','#',1) + '\n'
				else:
					beforeheader += line.replace(';','#',1) + '\n'
			elif line.lstrip().startswith(':'):
				data += '        --%s--\n' % line.split('#',1)[0].strip()[1:]
			elif line.lstrip().startswith('script_name ') and headerinfo[3] is None:
				headerinfo[3] = line.lstrip()[12:]
				if re.match('bw|brood ?war',headerinfo[3],re.I):
					headerinfo[2] = 'bwscript'
				else:
					headerinfo[2] = 'aiscript'
				for n,string in enumerate(self.delegate.get_tbl().strings):
					if headerinfo[3] + '\x00' == string:
						headerinfo[1] = n
						break
				else:
					headerinfo[1] = 0
			elif line.lstrip().startswith('script_id ') and headerinfo[0] is None:
				headerinfo[0] = line.lstrip()[10:]
			elif line.strip():
				d = line.lstrip().split(';',1)[0].strip().split(' ')
				if d[0] in AIBIN.AIBIN.short_labels:
					if d[0] == 'debug' and len(d) >= 3:
						d = [d[0], d[1], '"%s"' % ' '.join(d[2:])]
					data += '    %s(%s)' % (d[0], ', '.join(d[1:]))
					if ';' in line:
						data += ' # ' + line.split(';',1)[1]
				else:
					if not None in headerinfo:
						data += '# ' + line
					else:
						beforeheader += '# ' + line + '\n'
				data += '\n'
			else:
				data += '\n'
		if None in headerinfo:
			MessageBox.askquestion(parent=self, title='Invalid Header', message='The script is either missing a script_name or a script_id.', type=MessageBox.OK)
			return
		self.text.delete('1.0', END)
		self.text.insert(END, beforeheader + '\n' + header % tuple(headerinfo) + data)
		self.text.edited = True
		self.editstatus['state'] = NORMAL

	def debuggerize(self) -> None:
		d = 0
		data = ''
		debug = {
			'goto':('debug(%(param1)s, Goto block "%(param1)s". %(s)s)%(c)s',0),
			'notowns_jump':('notowns_jump(%(param1)s,%(debug1)s)%(c)s\ndebug(%(debug2)s, I do not own the unit "%(param1)s"<44> continuing the current block... %(s)s)\n	--%(debug1)s--\ndebug(%(param2)s, I own the unit "%(param1)s"<44> going to block "%(param2)s". %(s)s)\n	--%(debug2)s--',2),
			'expand':('debug(%(debug1)s, Running block "%(param2)s" for expansion number "%(param1)s". %(s)s)\n	--%(debug1)s--\nexpand(%(param1)s, %(param2)s)%(c)s',1),
			'debug':('debug(%(param1)s, %(param2)s [%(param1)s]%(s)s)%(c)s',0),
			'random_jump':('random_jump(%(param1)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, I randomly chose to continue this block instead of going to block "%(param2)s". %(s)s)\n	--%(debug1)s--\ndebug(%(param2)s, I randomly chose to go to block "%(param2)s". %(s)s)\n	--%(debug2)s--',2),
			'time_jump':('time_jump(%(param1)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, "%(param1)s" minutes have not passed in game<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param2)s, "%(param1)s" minutes have passed in game<44> going to block "%(param2)s". %(s)s)\n	--%(debug2)s--',2),
			'race_jump':('race_jump(%(debug1)s, %(debug2)s, %(debug3)s)%(c)s\n	--%(debug1)s--\ndebug(%(param1)s, My current enemy is Terran<44> going to block "%(param1)s". %(s)s)\n	--%(debug2)s--\ndebug(%(param2)s, My current enemy is Zerg<44> going to block "%(param2)s". %(s)s)\n	--%(debug3)s--\ndebug(%(param3)s, My current enemy is Protoss<44> going to block "%(param3)s". %(s)s)',3),
			#'region_size':('',),
			'groundmap_jump':('groundmap_jump(%(debug1)s)%(c)s\ndebug(%(debug2)s, The map is not a ground map<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param1)s, The map is a ground map<44> going to "%(param1)s". %(s)s)\n	--%(debug2)s--',2),
			'call':('debug(%(debug1)s, Calling block "%(param1)s". %(s)s)\n	--%(debug1)s--\ncall(%(param1)s)%(c)s\ndebug(%(debug2)s, Returned from a call to block "%(param1)s". %(s)s)\n	--%(debug2)s--',2),
			#'panic':('',),
			'multirun':('debug(%(debug1)s, Running block "%(param1)s" in another thread. %(s)s)\n	--%(debug1)s--\nmultirun(%(param1)s)%(c)s',1),
			#'rush':('',),
			'resources_jump':('resources_jump(%(param1)s, %(param2)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, I do not have at least "%(param1)s" minerals and "%(param2)s" vespene<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param3)s, I have at least "%(param1)s" minerals and "%(param2)s" vespene<44> going to "%(param3)s". %(s)s)\n	--%(debug2)s--',2),
			'enemyowns_jump':('enemyowns_jump(%(param1)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, My current enemy doesn\'t own the unit "%(param1)s"<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param2)s, My current enemy owns the unit "%(param1)s"<44> going to "%(param2)s". %(s)s)\n	--%(debug2)s--',2),
			'enemyresources_jump':('enemyresources_jump(%(param1)s, %(param2)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, My current enemy doesn\'t have at least "%(param1)s" minerals and "%(param2)s" vespene<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param3)s, My current enemy has at least "%(param1)s" minerals and "%(param2)s" vespene<44> going to "%(param3)s". %(s)s)\n	--%(debug2)s--',2),
			'stop':('debug(%(debug1)s, Stopping the current block. %(s)s)\n	--%(debug1)s--\nstop()%(c)s',1),
			#'if_owned':('',),
			#'allies_watch':('',),
			#'try_townpoint':('',),
		}
		header = re.compile(r'\A([^(]{4})\([^)]+\):\s*(?:\{.+\})?(?:\s*#.*)?\Z')
		label = re.compile(r'\A\s*--\s*(.+)\s*--(?:\s*\{(.+)\})?(?:\s*#.*)?\\Z')
		jump = re.compile(r'\A(\s*)(%s)\((.+)\)(\s*#.*)?\Z' % '|'.join(list(debug.keys())))
		script,block = '',''
		for n,line in enumerate(self.text.text.get('1.0',END).split('\n')):
			m = header.match(line)
			if m:
				script = m.group(1)
				block = ''
				data += line + '\n'
				continue
			m = label.match(line)
			if m:
				block = m.group(1)
				data += line + '\n'
				continue
			m = jump.match(line)
			if m and m.group(2) in debug:
				inblock = ''
				if block:
					inblock = ' block "%s"' % block
				rep = {
					'debug1':'== Debug %s ==' % d,
					'debug2':'== Debug %s ==' % (d+1),
					'debug3':'== Debug %s ==' % (d+2),
					's':'[Line: %s | Inside script "%s"%s]' % (n, script, inblock),
					'c':m.group(4) or '',
				}
				params = self.delegate.get_ai_bin().parameters[self.delegate.get_ai_bin().short_labels.index(m.group(2))]
				if params:
					p = re.match('\\A%s\\Z' % ','.join(['\\s*(.+)\\s*'] * len(params)), m.group(3))
					if not p:
						data += line + '\n'
						continue
					for g,param in enumerate(p.groups()):
						rep['param%s' % (g+1)] = param
				data += m.group(1) + (debug[m.group(2)][0] % rep).replace('\n','\n' + m.group(1)) + '\n'
				d += debug[m.group(2)][1]
				continue
			data += line + '\n'
		self.text.delete('1.0', END)
		self.text.insert(END, data)
		self.text.edited = True
		self.editstatus['state'] = NORMAL

	def load(self) -> None:
		try:
			serialize_context = self.delegate.get_serialize_context()
			code = IO.output_to_text(lambda f: self.delegate.get_ai_bin().decompile(f, serialize_context, self.ids))
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.text.delete('1.0', END)
		self.text.insert(END, code)
		self.text.edited = False
		self.editstatus['state'] = DISABLED
		# TODO: Warnings?
		# if warnings:
		# 	WarningDialog(self, warnings)

	def close(self) -> None:
		if self.decompile:
			self.text.insert('1.0', self.decompile.strip())
			self.decompile = ''
			self.text.text.mark_set(INSERT, '1.0')
			self.text.text.see(INSERT)
			self.text.edit_reset()
			self.text.edited = False
			self.editstatus['state'] = DISABLED

	def destroy(self) -> None:
		if self.findwindow:
			Toplevel.destroy(self.findwindow)
		Toplevel.destroy(self)

	def dismiss(self) -> None:
		self.config_.windows.code_edit.save_size(self)
		PyMSDialog.dismiss(self)
