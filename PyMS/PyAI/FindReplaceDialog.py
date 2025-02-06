
from .Delegates import FindReplaceDelegate

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.Config import WindowGeometry

import re

# TODO: Update file
class FindReplaceDialog(PyMSDialog):
	def __init__(self, parent: Misc, delegate: FindReplaceDelegate, window_geometry_config: WindowGeometry) -> None:
		self.resettimer: str | None = None
		self.delegate = delegate
		self.window_geometry_config = window_geometry_config
		PyMSDialog.__init__(self, parent, 'Find/Replace', grabwait=False, resizable=(True, False))

	def widgetize(self) -> Widget | None:
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
		self.findentry = TextDropDown(s, self.find, self.delegate.get_find_history(), 30)
		self.findentry_c = self.findentry['bg']
		self.findentry.pack(fill=X)
		self.findentry.entry.selection_range(0, END)
		self.findentry.focus_set()
		s.pack(fill=X)
		s = Frame(f)
		Label(s, text='Replace With:', anchor=E, width=12).pack(side=LEFT)
		self.replaceentry = TextDropDown(s, self.replacewith, self.delegate.get_replace_history(), 30)
		self.replaceentry.pack(fill=X)
		s.pack(fill=X)
		f.pack(side=TOP, fill=X, pady=2)
		f = Frame(l)
		self.selectcheck = Checkbutton(f, text='In Selection', variable=self.inselection, anchor=W)
		self.selectcheck.pack(fill=X)
		Checkbutton(f, text='Case Sensitive', variable=self.casesens, anchor=W).pack(fill=X)
		Checkbutton(f, text='Regular Expression', variable=self.regex, anchor=W, command=lambda i=1: self.check(i)).pack(fill=X)
		self.multicheck = Checkbutton(f, text='Multi-Line', variable=self.multiline, anchor=W, state=DISABLED, command=lambda i=2: self.check(i))
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
		Button(l, text='Find Next', command=self.findnext).pack(fill=X, pady=1)
		Button(l, text='Count', command=self.count).pack(fill=X, pady=1)
		self.replacebtn = Button(l, text='Replace', command=lambda i=1: self.findnext(replace=i))
		self.replacebtn.pack(fill=X, pady=1)
		self.repallbtn = Button(l, text='Replace All', command=self.replaceall)
		self.repallbtn.pack(fill=X, pady=1)
		Button(l, text='Close', command=self.ok).pack(fill=X, pady=4)
		l.pack(side=LEFT, fill=Y, padx=2)

		self.bind(Key.Return(), self.findnext)
		def check(_event: Event) -> None:
			self.check(3)
		self.bind(Focus.In(), check)

		return self.findentry

	def setup_complete(self) -> None:
		self.window_geometry_config.load_size(self)

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
			if self.delegate.get_code_text().tag_ranges('Selection'):
				self.selectcheck['state'] = NORMAL
			else:
				self.selectcheck['state'] = DISABLED
				self.inselection.set(0)

	def findnext(self, event: Event | None = None, replace: int = 0) -> None:
		f = self.find.get()
		if not f in self.delegate.get_find_history():
			self.delegate.get_find_history().append(f)
		if not f:
			return
		code_text = self.delegate.get_code_text()
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
			if not rep in self.delegate.get_replace_history():
				self.delegate.get_replace_history().append(rep)
			item = code_text.tag_ranges('Selection')
			if item and r.match(code_text.get(*item)):
				ins = r.sub(rep, code_text.get(*item))
				with code_text.undo_group():
					code_text.delete(*item)
					code_text.insert(item[0], ins)
		m: re.Match[str] | None
		p: Misc = self
		if event and event.keycode == 13:
			p = self.parent
		if self.multiline.get():
			m = r.search(code_text.get(INSERT, END))
			if m:
				code_text.tag_remove('Selection', '1.0', END)
				s = f'{INSERT} +{m.start(0)}c'
				e = f'{INSERT} +{m.end(0)}c'
				code_text.tag_add('Selection', s, e)
				code_text.mark_set(INSERT, e)
				code_text.see(s)
				self.check(3)
			else:
				MessageBox.askquestion(parent=p, title='Find', message="Can't find text.", type=MessageBox.OK)
		else:
			u = self.updown.get()
			s,lse,rlse,e = ['-','+'][u],['lineend','linestart'][u],['linestart','lineend'][u],[code_text.index('1.0 lineend'),code_text.index(END)][u]
			i = code_text.index(INSERT)
			if i == e:
				return
			if i == code_text.index(f'{INSERT} {rlse}'):
				i = code_text.index(f'{INSERT} {s}1lines {lse}')
			n = -1
			while not u or i != e:
				if u:
					m = r.search(code_text.get(i, f'{i} {rlse}'))
				else:
					a = r.finditer(code_text.get(f'{i} {rlse}', i))
					c = 0
					for x,fm in enumerate(a):
						if n in (x, -1):
							m = fm
							c = x
					n = c - 1
				if m:
					code_text.tag_remove('Selection', '1.0', END)
					if u:
						s = f'{i} +{m.start(0)}c'
						e = f'{i} +{m.end(0)}c'
						code_text.mark_set(INSERT, e)
					else:
						s = f'{i} linestart +{m.start(0)}c'
						e = f'{i} linestart +{m.end(0)}c'
						code_text.mark_set(INSERT, s)
					code_text.tag_add('Selection', s, e)
					code_text.see(s)
					self.check(3)
					break
				if (not u and n == -1 and code_text.index(f'{i} lineend') == e) or i == e:
					MessageBox.askquestion(parent=p, title='Find', message="Can't find text.", type=MessageBox.OK)
					break
				i = code_text.index(f'{i} {s}1lines {lse}')
			else:
				MessageBox.askquestion(parent=p, title='Find', message="Can't find text.", type=MessageBox.OK)

	def count(self) -> None:
		f = self.find.get()
		if not f:
			return
		regex = f
		if not self.regex.get():
			regex = re.escape(regex)
		try:
			r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
		except:
			self.resettimer = self.after(1000, self.updatecolor)
			self.findentry['bg'] = '#FFB4B4'
			return
		MessageBox.askquestion(parent=self, title='Count', message=f'{len(r.findall(self.delegate.get_code_text().get("1.0", END)))} matches found.', type=MessageBox.OK)

	def replaceall(self) -> None:
		f = self.find.get()
		if not f:
			return
		code_text = self.delegate.get_code_text()
		regex = f
		if not self.regex.get():
			regex = re.escape(regex)
		try:
			r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
		except:
			self.resettimer = self.after(1000, self.updatecolor)
			self.findentry['bg'] = '#FFB4B4'
			return
		text = r.subn(self.replacewith.get(), code_text.get('1.0', END))
		if text[1]:
			with code_text.undo_group():
				code_text.delete('1.0', END)
				code_text.insert('1.0', text[0].rstrip('\n'))
		MessageBox.askquestion(parent=self, title='Replace Complete', message=f'{text[1]} matches replaced.', type=MessageBox.OK)

	def updatecolor(self) -> None:
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.findentry['bg'] = self.findentry_c

	def destroy(self) -> None:
		self.window_geometry_config.save_size(self)
		PyMSDialog.withdraw(self)
