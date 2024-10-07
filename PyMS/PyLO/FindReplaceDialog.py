
from .Delegates import FindDelegate

from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.UIKit import *
from ..Utilities import Config

import re

from typing import Callable, cast

class FindReplaceDialog(PyMSDialog):
	def __init__(self, parent: Misc, window_geometry_config: Config.WindowGeometry, delegate: FindDelegate) -> None:
		self.window_geometry_config = window_geometry_config
		self.delegate = delegate
		self.resettimer: str | None = None
		self.find_history: list[str] = []
		self.replace_history: list[str] = []
		PyMSDialog.__init__(self, parent, 'Find/Replace', grabwait=False, resizable=(True, False))

	def widgetize(self) -> (Misc | None):
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
		self.findentry = TextDropDown(s, self.find, self.find_history, 30)
		self.findentry_c = self.findentry['bg']
		self.findentry.pack(fill=X)
		s.pack(fill=X)
		s = Frame(f)
		Label(s, text='Replace With:', anchor=E, width=12).pack(side=LEFT)
		self.replaceentry = TextDropDown(s, self.replacewith, self.replace_history, 30)
		self.replaceentry.pack(fill=X)
		s.pack(fill=X)
		f.pack(side=TOP, fill=X, pady=2)
		f = Frame(l)
		self.selectcheck = Checkbutton(f, text='In Selection', variable=self.inselection, anchor=W)
		self.selectcheck.pack(fill=X)
		Checkbutton(f, text='Case Sensitive', variable=self.casesens, anchor=W).pack(fill=X)
		def check_callback1(i: int) -> Callable[[], None]:
			def check() -> None:
				self.check(i)
			return check
		Checkbutton(f, text='Regular Expression', variable=self.regex, anchor=W, command=check_callback1(1)).pack(fill=X)
		self.multicheck = Checkbutton(f, text='Multi-Line', variable=self.multiline, anchor=W, state=DISABLED, command=check_callback1(2))
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
		self.replacebtn = Button(l, text='Replace', command=lambda: self.findnext(replace=True))
		self.replacebtn.pack(fill=X, pady=1)
		self.repallbtn = Button(l, text='Replace All', command=self.replaceall)
		self.repallbtn.pack(fill=X, pady=1)
		Button(l, text='Close', command=self.ok).pack(fill=X, pady=4)
		l.pack(side=LEFT, fill=Y, padx=2)

		def check_callback2(i: int) -> Callable[[Event], None]:
			def check(event: Event) -> None:
				self.check(i)
			return check
		self.bind(Focus.In(), check_callback2(3))

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
			if self.delegate.get_text().tag_ranges('sel'):
				self.selectcheck['state'] = NORMAL
			else:
				self.selectcheck['state'] = DISABLED
				self.inselection.set(0)

	def findnext(self, event: Event | None = None, replace: bool = False) -> None:
		f = self.find.get()
		if not f in self.find_history:
			self.find_history.append(f)
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
			text = self.delegate.get_text()
			if replace:
				rep = self.replacewith.get()
				if not rep in self.replace_history:
					self.replace_history.append(rep)
				item = tuple(str(i) for i in text.tag_ranges('sel'))
				if item and r.match(text.get(*item)):
					ins = r.sub(rep, text.get(*item))
					with text.undo_group():
						text.delete(*item)
						text.insert(item[0], ins)
					text.mark_recolor_range(f'{item[0]} linestart', f'{item[0]} lineend')
			if self.multiline.get():
				m = r.search(text.get(INSERT, END))
				if m:
					text.tag_remove('sel', '1.0', END)
					s,e = '%s +%sc' % (INSERT, m.start(0)),'%s +%sc' % (INSERT,m.end(0))
					text.tag_add('sel', s, e)
					text.mark_set(INSERT, e)
					text.see(s)
					self.check(3)
				else:
					MessageBox.askquestion(parent=self.parent if event else self, title='Find', message="Can't find text.", type=MessageBox.OK)
			else:
				u = self.updown.get()
				s,lse,rlse,e = ['-','+'][u],['lineend','linestart'][u],['linestart','lineend'][u],[text.index('1.0 lineend'),text.index(END)][u]
				i = text.index(INSERT)
				if i == e:
					return
				if i == text.index('%s %s' % (INSERT, rlse)):
					i = text.index('%s %s1lines %s' % (INSERT, s, lse))
				n = -1
				while not u or i != e:
					if u:
						m = r.search(text.get(i, '%s %s' % (i, rlse)))
					else:
						m = None
						a = r.finditer(text.get('%s %s' % (i, rlse), i))
						c = 0
						for xb,fb in enumerate(a):
							if xb == n or n == -1:
								m = fb
								c = xb
						n = c - 1
					if m:
						text.tag_remove('sel', '1.0', END)
						if u:
							s,e = '%s +%sc' % (i,m.start(0)),'%s +%sc' % (i,m.end(0))
							text.mark_set(INSERT, e)
						else:
							s,e = '%s linestart +%sc' % (i,m.start(0)),'%s linestart +%sc' % (i,m.end(0))
							text.mark_set(INSERT, s)
						text.tag_add('sel', s, e)
						text.see(s)
						self.check(3)
						break
					if (not u and n == -1 and text.index('%s lineend' % i) == e) or i == e:
						MessageBox.askquestion(parent=self.parent if event else self, title='Find', message="Can't find text.", type=MessageBox.OK)
						break
					i = text.index('%s %s1lines %s' % (i, s, lse))
				else:
					MessageBox.askquestion(parent=self.parent if event else self, title='Find', message="Can't find text.", type=MessageBox.OK)

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
		MessageBox.askquestion(parent=self, title='Count', message='%s matches found.' % len(r.findall(self.delegate.get_text().get('1.0', END))), type=MessageBox.OK)

	def replaceall(self) -> None:
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
		text_widget = self.delegate.get_text()
		text = r.subn(self.replacewith.get(), text_widget.get('1.0', END))
		if text[1]:
			with text_widget.undo_group():
				text_widget.delete('1.0', END)
				text_widget.insert('1.0', text[0].rstrip('\n'))
			text_widget.mark_recolor_range('1.0', END)
		MessageBox.askquestion(parent=self, title='Replace Complete', message='%s matches replaced.' % text[1], type=MessageBox.OK)

	def updatecolor(self) -> None:
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.findentry['bg'] = self.findentry_c

	def destroy(self) -> None:
		self.window_geometry_config.save_size(self)
		PyMSDialog.withdraw(self)
