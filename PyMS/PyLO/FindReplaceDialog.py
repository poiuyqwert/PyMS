
from .Delegates import FindDelegate

from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import UIKit as UI
from ..Utilities import Config

import re

from typing import Callable

class FindReplaceDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, window_geometry_config: Config.WindowGeometry, delegate: FindDelegate) -> None:
		self.window_geometry_config = window_geometry_config
		self.delegate = delegate
		self.resettimer: str | None = None
		self.find_history: list[str] = []
		self.replace_history: list[str] = []
		PyMSDialog.__init__(self, parent, 'Find/Replace', grabwait=False, resizable=(True, False))

	def widgetize(self) -> (UI.Misc | None):
		self.find = UI.StringVar()
		self.replacewith = UI.StringVar()
		self.replace = UI.IntVar()
		self.inselection = UI.IntVar()
		self.casesens = UI.IntVar()
		self.regex = UI.IntVar()
		self.multiline = UI.IntVar()
		self.updown = UI.IntVar()
		self.updown.set(1)

		l = UI.Frame(self)
		f = UI.Frame(l)
		s = UI.Frame(f)
		UI.Label(s, text='Find:', anchor=UI.E, width=12).pack(side=UI.LEFT)
		self.findentry = UI.TextDropDown(s, self.find, self.find_history, 30)
		self.findentry_c = self.findentry['bg']
		self.findentry.pack(fill=UI.X)
		s.pack(fill=UI.X)
		s = UI.Frame(f)
		UI.Label(s, text='Replace With:', anchor=UI.E, width=12).pack(side=UI.LEFT)
		self.replaceentry = UI.TextDropDown(s, self.replacewith, self.replace_history, 30)
		self.replaceentry.pack(fill=UI.X)
		s.pack(fill=UI.X)
		f.pack(side=UI.TOP, fill=UI.X, pady=2)
		f = UI.Frame(l)
		self.selectcheck = UI.Checkbutton(f, text='In Selection', variable=self.inselection, anchor=UI.W)
		self.selectcheck.pack(fill=UI.X)
		UI.Checkbutton(f, text='Case Sensitive', variable=self.casesens, anchor=UI.W).pack(fill=UI.X)
		def check_callback1(i: int) -> Callable[[], None]:
			def check() -> None:
				self.check(i)
			return check
		UI.Checkbutton(f, text='Regular Expression', variable=self.regex, anchor=UI.W, command=check_callback1(1)).pack(fill=UI.X)
		self.multicheck = UI.Checkbutton(f, text='Multi-Line', variable=self.multiline, anchor=UI.W, state=UI.DISABLED, command=check_callback1(2))
		self.multicheck.pack(fill=UI.X)
		f.pack(side=UI.LEFT, fill=UI.BOTH)
		f = UI.Frame(l)
		lf = UI.LabelFrame(f, text='Direction')
		self.up = UI.Radiobutton(lf, text='Up', variable=self.updown, value=0, anchor=UI.W)
		self.up.pack(fill=UI.X)
		self.down = UI.Radiobutton(lf, text='Down', variable=self.updown, value=1, anchor=UI.W)
		self.down.pack()
		lf.pack()
		f.pack(side=UI.RIGHT, fill=UI.Y)
		l.pack(side=UI.LEFT, fill=UI.BOTH, pady=2, expand=1)

		l = UI.Frame(self)
		UI.Button(l, text='Find Next', command=self.findnext).pack(fill=UI.X, pady=1)
		UI.Button(l, text='Count', command=self.count).pack(fill=UI.X, pady=1)
		self.replacebtn = UI.Button(l, text='Replace', command=lambda: self.findnext(replace=True))
		self.replacebtn.pack(fill=UI.X, pady=1)
		self.repallbtn = UI.Button(l, text='Replace All', command=self.replaceall)
		self.repallbtn.pack(fill=UI.X, pady=1)
		UI.Button(l, text='Close', command=self.ok).pack(fill=UI.X, pady=4)
		l.pack(side=UI.LEFT, fill=UI.Y, padx=2)

		def check_callback2(i: int) -> Callable[[UI.Event], None]:
			def check(_event: UI.Event) -> None:
				self.check(i)
			return check
		self.bind(UI.Focus.In(), check_callback2(3))

		return self.findentry

	def setup_complete(self) -> None:
		self.window_geometry_config.load_size(self)

	def check(self, i: int) -> None:
		if i == 1:
			if self.regex.get():
				self.multicheck['state'] = UI.NORMAL
			else:
				self.multicheck['state'] = UI.DISABLED
				self.multiline.set(0)
		if i in [1,2]:
			s = [UI.NORMAL,UI.DISABLED][self.multiline.get()]
			self.up['state'] = s
			self.down['state'] = s
			if s == UI.DISABLED:
				self.updown.set(1)
		elif i == 3:
			if self.delegate.get_text().tag_ranges('sel'):
				self.selectcheck['state'] = UI.NORMAL
			else:
				self.selectcheck['state'] = UI.DISABLED
				self.inselection.set(0)

	def findnext(self, event: UI.Event | None = None, replace: bool = False) -> None:
		f = self.find.get()
		if not f in self.find_history:
			self.find_history.append(f)
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except Exception:
				self.resettimer = self.after_managed(1000, self.updatecolor)
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
				m = r.search(text.get(UI.INSERT, UI.END))
				if m:
					text.tag_remove('sel', '1.0', UI.END)
					s = f'{UI.INSERT} +{m.start(0)}c'
					e = f'{UI.INSERT} +{m.end(0)}c'
					text.tag_add('sel', s, e)
					text.mark_set(UI.INSERT, e)
					text.see(s)
					self.check(3)
				else:
					UI.MessageBox.showinfo(parent=self.parent if event else self, title='Find', message="Can't find text.")
			else:
				u = self.updown.get()
				s,lse,rlse,e = ['-','+'][u],['lineend','linestart'][u],['linestart','lineend'][u],[text.index('1.0 lineend'),text.index(UI.END)][u]
				i = text.index(UI.INSERT)
				if i == e:
					return
				if i == text.index(f'{UI.INSERT} {rlse}'):
					i = text.index(f'{UI.INSERT} {s}1lines {lse}')
				n = -1
				while not u or i != e:
					if u:
						m = r.search(text.get(i, f'{i} {rlse}'))
					else:
						m = None
						a = r.finditer(text.get(f'{i} {rlse}', i))
						c = 0
						for xb,fb in enumerate(a):
							if n in (xb, -1):
								m = fb
								c = xb
						n = c - 1
					if m:
						text.tag_remove('sel', '1.0', UI.END)
						if u:
							s = f'{i} +{m.start(0)}c'
							e = f'{i} +{m.end(0)}c'
							text.mark_set(UI.INSERT, e)
						else:
							s = f'{i} linestart +{m.start(0)}c'
							e = f'{i} linestart +{m.end(0)}c'
							text.mark_set(UI.INSERT, s)
						text.tag_add('sel', s, e)
						text.see(s)
						self.check(3)
						break
					if (not u and n == -1 and text.index(f'{i} lineend') == e) or i == e:
						UI.MessageBox.showinfo(parent=self.parent if event else self, title='Find', message="Can't find text.")
						break
					i = text.index(f'{i} {s}1lines {lse}')
				else:
					UI.MessageBox.showinfo(parent=self.parent if event else self, title='Find', message="Can't find text.")

	def count(self) -> None:
		f = self.find.get()
		if not f:
			return
		regex = f
		if not self.regex.get():
			regex = re.escape(regex)
		try:
			r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
		except Exception:
			self.resettimer = self.after_managed(1000, self.updatecolor)
			self.findentry['bg'] = '#FFB4B4'
			return
		UI.MessageBox.showinfo(parent=self, title='Count', message=f'{len(r.findall(self.delegate.get_text().get("1.0", UI.END)))} matches found.')

	def replaceall(self) -> None:
		f = self.find.get()
		if not f:
			return
		regex = f
		if not self.regex.get():
			regex = re.escape(regex)
		try:
			r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
		except Exception:
			self.resettimer = self.after_managed(1000, self.updatecolor)
			self.findentry['bg'] = '#FFB4B4'
			return
		text_widget = self.delegate.get_text()
		text = r.subn(self.replacewith.get(), text_widget.get('1.0', UI.END))
		if text[1]:
			with text_widget.undo_group():
				text_widget.delete('1.0', UI.END)
				text_widget.insert('1.0', text[0].rstrip('\n'))
			text_widget.mark_recolor_range('1.0', UI.END)
		UI.MessageBox.showinfo(parent=self, title='Replace Complete', message=f'{text[1]} matches replaced.')

	def updatecolor(self) -> None:
		if self.resettimer:
			self.after_managed_cancel(self.resettimer)
			self.resettimer = None
		self.findentry['bg'] = self.findentry_c

	def destroy(self) -> None:
		self.window_geometry_config.save_size(self)
		PyMSDialog.withdraw(self)
