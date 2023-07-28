
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.Settings import Settings

import re

class FindReplaceDialog(PyMSDialog):
	def __init__(self, parent: Misc, text: CodeText, settings: Settings) -> None:
		self.text = text
		self.settings = settings
		self.resettimer: str | None = None
		self.findhistory: list[str] = []
		self.replacehistory: list[str] = []
		PyMSDialog.__init__(self, parent, 'Find/Replace', grabwait=False, resizable=(True, False))

	def widgetize(self) -> Misc | None:
		self.find = StringVar()
		self.replacewith = StringVar()
		self.replace = IntVar()
		self.inselection = IntVar()
		self.casesens = IntVar()
		self.regex = IntVar()
		self.multiline = IntVar()
		self.updown = IntVar()
		self.updown.set(1)

		l = Frame(self)
		f = Frame(l)
		s = Frame(f)
		Label(s, text='Find:', anchor=E, width=12).pack(side=LEFT)
		self.findentry = TextDropDown(s, self.find, self.findhistory, 30)
		self.findentry_c = self.findentry['bg']
		self.findentry.pack(fill=X)
		self.findentry.entry.selection_range(0, END)
		self.findentry.focus_set()
		s.pack(fill=X)
		s = Frame(f)
		Label(s, text='Replace With:', anchor=E, width=12).pack(side=LEFT)
		self.replaceentry = TextDropDown(s, self.replacewith, self.replacehistory, 30)
		self.replaceentry.pack(fill=X)
		s.pack(fill=X)
		f.pack(side=TOP, fill=X, pady=2)
		f = Frame(l)
		self.selectcheck = Checkbutton(f, text='In Selection', variable=self.inselection, anchor=W)
		self.selectcheck.pack(fill=X)
		Checkbutton(f, text='Case Sensitive', variable=self.casesens, anchor=W).pack(fill=X)
		Checkbutton(f, text='Regular Expression', variable=self.regex, anchor=W, command=lambda: self.check(1)).pack(fill=X)
		self.multicheck = Checkbutton(f, text='Multi-Line', variable=self.multiline, anchor=W, state=DISABLED, command=lambda: self.check(2))
		self.multicheck.pack(fill=X)
		f.pack(side=LEFT, fill=BOTH)
		f = Frame(l)
		lf = LabelFrame(f, text='Direction')
		self.up = Radiobutton(lf, text='Up', variable=self.updown, value=0, anchor=W)
		self.up.pack(fill=X)
		self.down = Radiobutton(lf, text='Down', variable=self.updown, value=1, anchor=W)
		self.down.pack()
		lf.pack()
		f.pack(side=RIGHT, fill=Y)
		l.pack(side=LEFT, fill=BOTH, pady=2, expand=1)

		l = Frame(self)
		Button(l, text='Find Next', command=self.findnext, default=NORMAL).pack(fill=X, pady=1)
		Button(l, text='Count', command=self.count).pack(fill=X, pady=1)
		self.replacebtn = Button(l, text='Replace', command=lambda: self.findnext(replace=True))
		self.replacebtn.pack(fill=X, pady=1)
		self.repallbtn = Button(l, text='Replace All', command=self.replaceall)
		self.repallbtn.pack(fill=X, pady=1)
		Button(l, text='Close', command=self.ok).pack(fill=X, pady=4)
		l.pack(side=LEFT, fill=Y, padx=2)

		self.bind(Key.Return(), self.findnext)
		self.bind(Focus.In(), lambda e: self.check(3))

		return self.findentry

	def setup_complete(self) -> None:
		self.settings.windows.load_window_size('find_replace', self)

	def check(self, i: int) -> None:
		if i == 1:
			if self.regex.get():
				self.multicheck['state'] = NORMAL
			else:
				self.multicheck['state'] = DISABLED
				self.multiline.set(0)
		if i in [1,2]:
			s = [NORMAL,DISABLED][self.multiline.get()]
			self.up['state'] = s
			self.down['state'] = s
			if s == DISABLED:
				self.updown.set(1)
		elif i == 3:
			if self.text.tag_ranges('Selection'):
				self.selectcheck['state'] = NORMAL
			else:
				self.selectcheck['state'] = DISABLED
				self.inselection.set(0)

	def findnext(self, key: Event | None = None, replace: bool = False):
		f = self.find.get()
		if not f in self.findhistory:
			self.findhistory.append(f)
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			if replace:
				rep = self.replacewith.get()
				if not rep in self.replacehistory:
					self.replacehistory.append(rep)
				item: tuple[str, str] = self.text.tag_ranges('Selection') # type: ignore[assignment]
				if item and r.match(self.text.get(*item)):
					ins = r.sub(rep, self.text.get(*item))
					self.text.delete(*item)
					self.text.insert(item[0], ins)
					self.text.update_range(item[0])
			if self.multiline.get():
				m = r.search(self.text.get(INSERT, END))
				if m:
					self.text.tag_remove('Selection', '1.0', END)
					s,e = '%s +%sc' % (INSERT, m.start(0)),'%s +%sc' % (INSERT,m.end(0))
					self.text.tag_add('Selection', s, e)
					self.text.mark_set(INSERT, e)
					self.text.see(s)
					self.check(3)
				else:
					p: Misc = self
					if key and key.keycode == 13:
						p = self.parent
					MessageBox.askquestion(parent=p, title='Find', message="Can't find text.", type=MessageBox.OK)
			else:
				u = self.updown.get()
				s,lse,rlse,e = ['-','+'][u],['lineend','linestart'][u],['linestart','lineend'][u],[self.text.index('1.0 lineend'),self.text.index(END)][u]
				i = self.text.index(INSERT)
				if i == e:
					return
				if i == self.text.index('%s %s' % (INSERT, rlse)):
					i = self.text.index('%s %s1lines %s' % (INSERT, s, lse))
				n = -1
				while not u or i != e:
					if u:
						m = r.search(self.text.get(i, '%s %s' % (i, rlse)))
					else:
						m = None
						a = r.finditer(self.text.get('%s %s' % (i, rlse), i))
						c = 0
						for x,am in enumerate(a):
							if x == n or n == -1:
								m = am
								c = x
						n = c - 1
					if m:
						self.text.tag_remove('Selection', '1.0', END)
						if u:
							s,e = '%s +%sc' % (i,m.start(0)),'%s +%sc' % (i,m.end(0))
							self.text.mark_set(INSERT, e)
						else:
							s,e = '%s linestart +%sc' % (i,m.start(0)),'%s linestart +%sc' % (i,m.end(0))
							self.text.mark_set(INSERT, s)
						self.text.tag_add('Selection', s, e)
						self.text.see(s)
						self.check(3)
						break
					if (not u and n == -1 and self.text.index('%s lineend' % i) == e) or i == e:
						p = self
						if key and key.keycode == 13:
							p = self.parent
						MessageBox.askquestion(parent=p, title='Find', message="Can't find text.", type=MessageBox.OK)
						break
					i = self.text.index('%s %s1lines %s' % (i, s, lse))
				else:
					p = self
					if key and key.keycode == 13:
						p = self.parent
					MessageBox.askquestion(parent=p, title='Find', message="Can't find text.", type=MessageBox.OK)

	def count(self) -> None:
		f = self.find.get()
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			MessageBox.askquestion(parent=self, title='Count', message='%s matches found.' % len(r.findall(self.text.get('1.0', END))), type=MessageBox.OK)

	def replaceall(self) -> None:
		f = self.find.get()
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			text = r.subn(self.replacewith.get(), self.text.get('1.0', END))
			if text[1]:
				self.text.delete('1.0', END)
				self.text.insert('1.0', text[0].rstrip('\n'))
				self.text.update_range('1.0')
			MessageBox.askquestion(parent=self, title='Replace Complete', message='%s matches replaced.' % text[1], type=MessageBox.OK)

	def updatecolor(self) -> None:
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.findentry['bg'] = self.findentry_c

	def dismiss(self) -> None:
		self.settings.windows.save_window_size('find_replace', self)
		PyMSDialog.dismiss(self)
