
from .utils import isstr
from .UIKit import *

import re

class CodeText(Frame):
	autoindent = re.compile('^([ \\t]*)')
	selregex = re.compile('\\bsel\\b')

	def __init__(self, parent, ecallback=None, icallback=None, scallback=None, acallback=None, state=NORMAL):
		self.dispatch_output = False
		self.edited = False
		self.taboverride = False
		# Edit Callback
		# INSERT Callback
		# Selection Callback
		# Auto-complete Callback
		self.ecallback = ecallback
		self.icallback = icallback
		self.scallback = scallback
		self.acallback = acallback

		Frame.__init__(self, parent, bd=2, relief=SUNKEN)
		frame = Frame(self)
		font = ('Courier New', -12, 'normal')
		self.lines = Text(frame, height=1, font=font, bd=0, bg='#E4E4E4', fg='#808080', width=8, cursor='')
		self.lines.pack(side=LEFT, fill=Y)
		hscroll = Scrollbar(self, orient=HORIZONTAL)
		self.vscroll = Scrollbar(self)
		self.text = Text(frame, height=1, font=font, bd=0, undo=1, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=self.yscroll, exportselection=0)
		self.text.configure(tabs=self.tk.call("font", "measure", self.text["font"], "-displayof", frame, '    '))
		self.text.pack(side=LEFT, fill=BOTH, expand=1)
		self.text.bind(Ctrl.a, lambda e: self.after(1, self.selectall))
		self.text.bind(Shift.Tab, lambda e,i=True: self.indent(e, i))
		self.text.bind(ButtonRelease.Click_Right, self.popup)
		frame.grid(sticky=NSEW)
		hscroll.config(command=self.text.xview)
		hscroll.grid(sticky=EW)
		self.vscroll.config(command=self.yview)
		self.vscroll.grid(sticky=NS, row=0, column=1)
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)

		textmenu = [
			('Undo', self.undo, 0), # 0
			None,
			('Cut', lambda: self.copy(True), 2), # 2
			('Copy', self.copy, 0), # 3
			('Paste', self.paste, 0), # 4
			('Delete', lambda: self.text.delete('Selection.first', 'Selection.last'), 0), # 5
			None,
			('Select All', lambda: self.after(1, self.selectall), 7), # 7
		]
		self.textmenu = Menu(self, tearoff=0)
		for m in textmenu:
			if m:
				l,c,u = m
				self.textmenu.add_command(label=l, command=c, underline=u)
			else:
				self.textmenu.add_separator()

		self.lines.insert('1.0', '      1')
		self.lines.bind(Focus.In, self.selectline)
		self.text.mark_set('return', '1.0')
		self.text.orig = self.text._w + '_orig'
		self.tk.call('rename', self.text._w, self.text.orig)
		self.tk.createcommand(self.text._w, self.dispatch)

		self['state'] = state

		self.tag_configure = self.text.tag_configure
		self.tag_add = self.text.tag_add
		self.tag_remove = self.text.tag_remove
		self.tag_raise = self.text.tag_raise
		self.tag_nextrange = self.text.tag_nextrange
		self.tag_prevrange = self.text.tag_prevrange
		self.tag_ranges = self.text.tag_ranges
		self.tag_names = self.text.tag_names
		self.tag_bind = self.text.tag_bind
		self.tag_delete = self.text.tag_delete
		self.mark_set = self.text.mark_set
		self.index = self.text.index
		self.get = self.text.get
		self.see = self.text.see
		self.compare = self.text.compare
		self.edited = False
		self.afterid = None
		self.last_delete = None
		self.tags = {}
		# None - Nothing, True - Continue coloring, False - Stop coloring
		self.coloring = None
		self.dnd = False

		self.setup()

	def popup(self, e):
		if self.text['state'] == NORMAL:
			s,i,r = self.text.index('@1,1'),self.text.index(INSERT),self.text.tag_ranges('Selection')
			try:
				self.text.edit_undo()
			except:
				self.textmenu.entryconfig(0, state=DISABLED)
			else:
				self.text.edit_redo()
				self.textmenu.entryconfig(0, state=NORMAL)
			if r:
				self.tag_add('Selection', *r)
			self.text.mark_set(INSERT,i)
			self.text.yview_pickplace(s)
			s = s.split('.')[0]
			if s in '1 2 3 4 5 6 7 8':
				self.text.yview_scroll(s, 'lines')
			if not self.text.tag_ranges('Selection'):
				sel = DISABLED
			else:
				sel = NORMAL
			for i in [2,3,5]:
				self.textmenu.entryconfig(i, state=sel)
			try:
				c = not self.selection_get(selection='CLIPBOARD')
			except:
				c = 1
			self.textmenu.entryconfig(4, state=[NORMAL,DISABLED][c])
			self.textmenu.post(e.x_root, e.y_root)

	def undo(self):
		self.text.edit_undo()

	def edit_reset(self):
		self.text.edit_reset()

	def copy(self, cut=False):
		self.clipboard_clear()
		self.clipboard_append(self.text.get('Selection.first','Selection.last'))
		if cut:
			r = self.text.tag_ranges('Selection')
			self.text.delete('Selection.first','Selection.last')
			self.update_lines()
			self.update_range('%s linestart' % r[0], '%s lineend' % r[1])

	def paste(self):
		try:
			text = self.selection_get(selection='CLIPBOARD')
		except:
			pass
		else:
			if self.text.tag_ranges('Selection'):
				self.text.mark_set(INSERT, 'Selection.first')
				self.text.delete('Selection.first','Selection.last')
			i = self.text.index(INSERT)
			try:
				self.tk.call(self.text.orig, 'insert', INSERT, text)
			except:
				pass
			self.update_lines()
			self.update_range(i, i + "+%dc" % len(text))

	def focus_set(self):
		self.text.focus_set()

	def __setitem__(self, item, value):
		if item == 'state':
			self.lines['state'] = value
			self.text['state'] = value
		else:
			Frame.__setitem__(self, item, value)

	def selectall(self, e=None):
		self.text.tag_remove('Selection', '1.0', END)
		self.text.tag_add('Selection', '1.0', END)
		self.text.mark_set(INSERT, '1.0')

	def indent(self, e=None, dedent=False):
		item = self.text.tag_ranges('Selection')
		if item and not self.taboverride:
			head,tail = self.index('%s linestart' % item[0]),self.index('%s linestart' % item[1])
			while self.text.compare(head, '!=', END) and self.text.compare(head, '<=', tail):
				if dedent and self.text.get(head) in ' \t':
					self.tk.call(self.text.orig, 'delete', head)
				elif not dedent:
					self.tk.call(self.text.orig, 'insert', head, '\t')
				head = self.index('%s +1line' % head)
			self.update_range(self.index('%s linestart' % item[0]), self.index('%s lineend' % item[1]))
			return True
		elif not item and self.taboverride:
			self.taboverride = False

	def yview(self, *args):
		self.lines.yview(*args)
		self.text.yview(*args)

	def yscroll(self, *args):
		self.vscroll.set(*args)
		self.lines.yview(MOVETO, args[0])

	def selectline(self, e=None):
		self.text.tag_remove('Selection', '1.0', END)
		head = self.lines.index('current linestart')
		tail = self.index('%s lineend+1c' % head)
		self.text.tag_add('Selection', head, tail)
		self.text.mark_set(INSERT, tail)
		self.text.focus_set()

	def setedit(self):
		self.edited = True

	def insert(self, index, text, tags=None):
		if text == '\t':
			if self.last_delete and '\n' in self.last_delete[2]:
				self.tk.call(self.text.orig, 'insert', self.last_delete[0], self.last_delete[2])
				self.tag_add('Selection', self.last_delete[0], self.last_delete[1])
				if self.indent():
					self.setedit()
				return
			if self.acallback != None and self.acallback():
				self.setedit()
				return
		elif self.taboverride and text in self.taboverride and self.last_delete:
			self.tk.call(self.text.orig, 'insert', self.last_delete[0], self.last_delete[2])
			self.taboverride = False
		self.last_delete = None
		self.setedit()
		if text == '\n':
			i = self.index('%s linestart' % index)
			while i != '1.0' and not self.get(i, '%s lineend' % i).split('#',1)[0]:
				i = self.index('%s -1lines' % i)
			m = self.autoindent.match(self.get(i, '%s lineend' % i))
			if m:
				text += m.group(1)
		i = self.text.index(index)
		self.tk.call(self.text.orig, 'insert', i, text, tags)
		self.update_lines()
		self.update_range(i, i + "+%dc" % len(text))

	def delete(self, start, end=None):
		self.after(1, self.setedit)
		try:
			self.tk.call(self.text.orig, 'delete', start, end)
		except:
			pass
		else:
			self.update_lines()
			self.update_range(start)

	def update_lines(self):
		lines = self.lines.get('1.0', END).count('\n')
		dif = self.text.get('1.0', END).count('\n') - lines
		if dif > 0:
			self.lines.insert(END, '\n' + '\n'.join(['%s%s' % (' ' * (7-len(str(n))), n) for n in range(lines+1,lines+1+dif)]))
		elif dif:
			self.lines.delete('%s%slines' % (END,dif),END)

	def update_range(self, start='1.0', end=END):
		self.tag_add("Update", start, end)
		if self.coloring:
			self.coloring = False
		if not self.afterid:
			self.afterid = self.after(1, self.docolor)

	def update_insert(self):
		if self.icallback != None:
			self.icallback()

	def update_selection(self):
		if self.scallback != None:
			self.scallback()

	def dispatch(self, cmd, *args):
		a = []
		if args:
			for n in args:
				if isstr(n):
					a.append(self.selregex.sub('Selection', n))
		a = tuple(a)
		# if self.dispatch_output:
			# sys.stderr.write('%s %s' % (cmd, a))
		if cmd == 'insert':
			self.after(1, self.update_insert)
			self.after(1, self.update_selection)
			return self.insert(*a)
		elif cmd == 'delete':
			self.after(1, self.update_insert)
			self.after(1, self.update_selection)
			# When you press Tab to indent, it actually deletes the selection and then types \t, so we must keep
			#  the last deletion to indent it
			if len(a) == 2 and a[0] == 'Selection.first' and a[1] == 'Selection.last':
				self.last_delete = (self.text.index(a[0]), self.text.index(a[1]), self.text.get(a[0], a[1]))
				def remove_last_delete(*_):
					self.last_delete = None
				self.after(1, remove_last_delete)
			return self.delete(*a)
		elif cmd == 'edit' and a[0] != 'separator':
			self.after(1, self.update_lines)
			self.after(1, self.update_range)
			self.after(1, self.update_insert)
			self.after(1, self.update_selection)
		elif cmd == 'mark' and a[0:2] == ('set', INSERT):
			self.after(1, self.update_insert)
		elif cmd == 'tag' and a[1] == 'Selection' and a[0] in ['add','remove']:
			if self.dnd:
				return ''
			self.after(1, self.update_selection)
		try:
			return self.tk.call((self.text.orig, cmd) + a)
		except TclError:
			return ""

	def setup(self, tags=None):
		r = self.tag_ranges('Selection')
		if self.tags:
			for tag in self.tags.keys():
				self.tag_delete(tag)
		if tags:
			self.tags = tags
		else:
			self.setupparser()
		self.tags['Update'] = {'foreground':None,'background':None,'font':None}
		if not 'Selection' in self.tags:
			self.tags['Selection'] = {'foreground':None,'background':'#C0C0C0','font':None}
		for tag, cnf in self.tags.iteritems():
			if cnf:
				self.tag_configure(tag, **cnf)
		self.tag_raise('Selection')
		if r:
			self.tag_add('Selection', *r)
		self.text.tag_bind('Selection', Mouse.Click_Left, self.selclick)
		self.text.tag_bind('Selection', ButtonRelease.Click_Left, self.selrelease)
		self.text.focus_set()
		self.update_range()

	def docolor(self):
		self.afterid = None
		if self.coloring:
			return
		self.coloring = True
		self.colorize()
		self.coloring = None
		if self.tag_nextrange('Update', '1.0'):
			self.after_id = self.after(1, self.docolor)

	def setupparser(self):
		# Overload to setup your own parser
		pass

	def colorize(self):
		# Overload to do parsing
		pass

	def readlines(self):
		return self.text.get('1.0',END).split('\n')

	def selclick(self, e):
		self.dnd = True
		self.text.bind(Mouse.Motion, self.selmotion)

	def selmotion(self, e):
		self.text.mark_set(INSERT, '@%s,%s' % (e.x,e.y))

	def selrelease(self, e):
		self.dnd = False
		self.text.unbind(Mouse.Motion)
		sel = self.tag_nextrange('Selection', '1.0')
		text = self.text.get(*sel)
		self.delete(*sel)
		self.text.insert(INSERT, text)
