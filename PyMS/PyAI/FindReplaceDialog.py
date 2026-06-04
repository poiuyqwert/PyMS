
from .Delegates import FindReplaceDelegate

from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.Config import WindowGeometry

import re

# TODO: Update file
class FindReplaceDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, delegate: FindReplaceDelegate, window_geometry_config: WindowGeometry) -> None:
		self.resettimer: str | None = None
		self.delegate = delegate
		self.window_geometry_config = window_geometry_config
		PyMSDialog.__init__(self, parent, 'Find/Replace', grabwait=False, resizable=(True, False))

	def widgetize(self) -> UI.Widget | None:
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
		self.findentry = UI.TextDropDown(s, self.find, self.delegate.get_find_history(), 30)
		self.findentry_c = self.findentry['bg']
		self.findentry.pack(fill=UI.X)
		self.findentry.entry.selection_range(0, UI.END)
		self.findentry.focus_set()
		s.pack(fill=UI.X)
		s = UI.Frame(f)
		UI.Label(s, text='Replace With:', anchor=UI.E, width=12).pack(side=UI.LEFT)
		self.replaceentry = UI.TextDropDown(s, self.replacewith, self.delegate.get_replace_history(), 30)
		self.replaceentry.pack(fill=UI.X)
		s.pack(fill=UI.X)
		f.pack(side=UI.TOP, fill=UI.X, pady=2)
		f = UI.Frame(l)
		self.selectcheck = UI.Checkbutton(f, text='In Selection', variable=self.inselection, anchor=UI.W)
		self.selectcheck.pack(fill=UI.X)
		UI.Checkbutton(f, text='Case Sensitive', variable=self.casesens, anchor=UI.W).pack(fill=UI.X)
		UI.Checkbutton(f, text='Regular Expression', variable=self.regex, anchor=UI.W, command=lambda i=1: self.check(i)).pack(fill=UI.X)
		self.multicheck = UI.Checkbutton(f, text='Multi-Line', variable=self.multiline, anchor=UI.W, state=UI.DISABLED, command=lambda i=2: self.check(i))
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
		self.replacebtn = UI.Button(l, text='Replace', command=lambda i=1: self.findnext(replace=i))
		self.replacebtn.pack(fill=UI.X, pady=1)
		self.repallbtn = UI.Button(l, text='Replace All', command=self.replaceall)
		self.repallbtn.pack(fill=UI.X, pady=1)
		UI.Button(l, text='Close', command=self.ok).pack(fill=UI.X, pady=4)
		l.pack(side=UI.LEFT, fill=UI.Y, padx=2)

		self.bind(UI.Key.Return(), self.findnext)
		def check(_event: UI.Event) -> None:
			self.check(3)
		self.bind(UI.Focus.In(), check)

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
			if self.delegate.get_code_text().tag_ranges('Selection'):
				self.selectcheck['state'] = UI.NORMAL
			else:
				self.selectcheck['state'] = UI.DISABLED
				self.inselection.set(0)

	def findnext(self, event: UI.Event | None = None, replace: int = 0) -> None:
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
		except Exception:
			self.resettimer = self.after_managed(1000, self.updatecolor)
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
		p: UI.Misc = self
		if event and event.keycode == 13:
			p = self.parent
		if self.multiline.get():
			m = r.search(code_text.get(UI.INSERT, UI.END))
			if m:
				code_text.tag_remove('Selection', '1.0', UI.END)
				s = f'{UI.INSERT} +{m.start(0)}c'
				e = f'{UI.INSERT} +{m.end(0)}c'
				code_text.tag_add('Selection', s, e)
				code_text.mark_set(UI.INSERT, e)
				code_text.see(s)
				self.check(3)
			else:
				UI.MessageBox.showinfo(parent=p, title='Find', message="Can't find text.")
		else:
			u = self.updown.get()
			s,lse,rlse,e = ['-','+'][u],['lineend','linestart'][u],['linestart','lineend'][u],[code_text.index('1.0 lineend'),code_text.index(UI.END)][u]
			i = code_text.index(UI.INSERT)
			if i == e:
				return
			if i == code_text.index(f'{UI.INSERT} {rlse}'):
				i = code_text.index(f'{UI.INSERT} {s}1lines {lse}')
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
					code_text.tag_remove('Selection', '1.0', UI.END)
					if u:
						s = f'{i} +{m.start(0)}c'
						e = f'{i} +{m.end(0)}c'
						code_text.mark_set(UI.INSERT, e)
					else:
						s = f'{i} linestart +{m.start(0)}c'
						e = f'{i} linestart +{m.end(0)}c'
						code_text.mark_set(UI.INSERT, s)
					code_text.tag_add('Selection', s, e)
					code_text.see(s)
					self.check(3)
					break
				if (not u and n == -1 and code_text.index(f'{i} lineend') == e) or i == e:
					UI.MessageBox.showinfo(parent=p, title='Find', message="Can't find text.")
					break
				i = code_text.index(f'{i} {s}1lines {lse}')
			else:
				UI.MessageBox.showinfo(parent=p, title='Find', message="Can't find text.")

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
		UI.MessageBox.showinfo(parent=self, title='Count', message=f'{len(r.findall(self.delegate.get_code_text().get("1.0", UI.END)))} matches found.')

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
		except Exception:
			self.resettimer = self.after_managed(1000, self.updatecolor)
			self.findentry['bg'] = '#FFB4B4'
			return
		text = r.subn(self.replacewith.get(), code_text.get('1.0', UI.END))
		if text[1]:
			with code_text.undo_group():
				code_text.delete('1.0', UI.END)
				code_text.insert('1.0', text[0].rstrip('\n'))
		UI.MessageBox.showinfo(parent=self, title='Replace Complete', message=f'{text[1]} matches replaced.')

	def updatecolor(self) -> None:
		if self.resettimer:
			self.after_managed_cancel(self.resettimer)
			self.resettimer = None
		self.findentry['bg'] = self.findentry_c

	def destroy(self) -> None:
		self.window_geometry_config.save_size(self)
		PyMSDialog.withdraw(self)
