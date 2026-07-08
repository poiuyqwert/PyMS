
from . import UIKit as UI
from .ReusablePyMSDialog import ReusablePyMSDialog
from . import Config

import re
from enum import Enum

class _Update(Enum):
	regex = 1
	multiline = 2
	selection = 3

class FindReplaceDialog(ReusablePyMSDialog):
	def __init__(self, parent: UI.Misc, text: UI.CodeText, window_geometry_config: Config.WindowGeometry, *, can_replace: bool = True, find_history: UI.InputHistory | None = None, replace_history: UI.InputHistory | None = None) -> None:
		self.text = text
		self.window_geometry_config = window_geometry_config
		self.can_replace = can_replace
		self.find_history = find_history if find_history is not None else UI.InputHistory()
		self.replace_history = replace_history if replace_history is not None else UI.InputHistory()
		self.resettimer: str | None = None
		ReusablePyMSDialog.__init__(self, parent, 'Find/Replace' if can_replace else 'Find', resizable=(True, False))

	def widgetize(self) -> UI.Misc | None:
		self.find = UI.StringVar()
		self.replacewith = UI.StringVar()
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
		self.findentry.entry.selection_range(0, UI.END)
		self.findentry.focus_set()
		s.pack(fill=UI.X)
		if self.can_replace:
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
		UI.Checkbutton(f, text='Regular Expression', variable=self.regex, anchor=UI.W, command=lambda: self.check(_Update.regex)).pack(fill=UI.X)
		self.multicheck = UI.Checkbutton(f, text='Multi-Line', variable=self.multiline, anchor=UI.W, state=UI.DISABLED, command=lambda: self.check(_Update.multiline))
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
		UI.Button(l, text='Find Next', command=self.findnext, default=UI.NORMAL).pack(fill=UI.X, pady=1)
		UI.Button(l, text='Count', command=self.count).pack(fill=UI.X, pady=1)
		if self.can_replace:
			UI.Button(l, text='Replace', command=lambda: self.findnext(replace=True)).pack(fill=UI.X, pady=1)
			UI.Button(l, text='Replace All', command=self.replaceall).pack(fill=UI.X, pady=1)
		UI.Button(l, text='Close', command=self.ok).pack(fill=UI.X, pady=4)
		l.pack(side=UI.LEFT, fill=UI.Y, padx=2)

		self.bind(UI.Key.Return(), self.findnext)
		self.bind(UI.Focus.In(), lambda _: self.check(_Update.selection))

		return self.findentry

	def setup_complete(self) -> None:
		self.window_geometry_config.load_size(self)

	def on_show(self) -> None:
		self.findentry.focus_set(highlight=True)

	def check(self, update: _Update) -> None:
		if update == _Update.regex:
			if self.regex.get():
				self.multicheck['state'] = UI.NORMAL
			else:
				self.multicheck['state'] = UI.DISABLED
				self.multiline.set(0)
		if update in (_Update.regex, _Update.multiline):
			state = UI.DISABLED if self.multiline.get() else UI.NORMAL
			self.up['state'] = state
			self.down['state'] = state
			if state == UI.DISABLED:
				self.updown.set(1)
		if update == _Update.selection:
			if self.text.tag_ranges('sel'):
				self.selectcheck['state'] = UI.NORMAL
			else:
				self.selectcheck['state'] = UI.DISABLED
				self.inselection.set(0)

	def _compile_pattern(self) -> re.Pattern[str] | None:
		pattern = self.find.get()
		if not self.regex.get():
			pattern = re.escape(pattern)
		flags = 0 if self.casesens.get() else re.I
		if self.multiline.get():
			flags |= re.M | re.S
		try:
			return re.compile(pattern, flags)
		except Exception:
			self.resettimer = self.after_managed(1000, self.updatecolor)
			self.findentry['bg'] = '#FFB4B4'
			return None

	def findnext(self, event: UI.Event | None = None, replace: bool = False) -> None:
		f = self.find.get()
		if not f:
			return
		self.find_history.record(f)
		r = self._compile_pattern()
		if r is None:
			return
		def not_found() -> None:
			parent: UI.Misc = self
			if event and UI.Keysym(event.keysym) != UI.Key.Return:
				parent = self.parent
			UI.MessageBox.showinfo(parent=parent, title='Find', message="Can't find text.")
		if replace:
			rep = self.replacewith.get()
			self.replace_history.record(rep)
			sel_range = tuple(str(index) for index in self.text.tag_ranges('sel'))
			if sel_range and r.match(self.text.get(*sel_range)):
				ins = r.sub(rep, self.text.get(*sel_range))
				with self.text.undo_group():
					self.text.delete(*sel_range)
					self.text.insert(sel_range[0], ins)
				self.text.mark_recolor_range(f'{sel_range[0]} linestart', f'{sel_range[0]} lineend')
		if self.multiline.get():
			m = r.search(self.text.get(UI.INSERT, UI.END))
			if m:
				s = f'{UI.INSERT} +{m.start(0)}c'
				e = f'{UI.INSERT} +{m.end(0)}c'
				self._select_match(s, e, insert=e)
			else:
				not_found()
		else:
			down = bool(self.updown.get())
			found = self._search_down(r) if down else self._search_up(r)
			if found:
				from_index, m = found
				s = f'{from_index} +{m.start(0)}c'
				e = f'{from_index} +{m.end(0)}c'
				# Moving the insert cursor past the match (in the search direction)
				# makes the next find continue instead of re-finding this match
				self._select_match(s, e, insert=e if down else s)
			else:
				not_found()

	def _select_match(self, start: str, end: str, insert: str) -> None:
		self.text.tag_remove('sel', '1.0', UI.END)
		self.text.tag_add('sel', start, end)
		self.text.mark_set(UI.INSERT, insert)
		self.text.see(start)
		self.check(_Update.selection)

	def _search_down(self, r: re.Pattern[str]) -> tuple[str, re.Match[str]] | None:
		# Search line-by-line from the insert cursor to the end of the text,
		# taking the first match on each line
		end = self.text.index(UI.END)
		index = self.text.index(UI.INSERT)
		if index == self.text.index(f'{index} lineend'):
			index = self.text.index(f'{index} +1lines linestart')
		while self.text.compare(index, '<', end):
			m = r.search(self.text.get(index, f'{index} lineend'))
			if m:
				return (index, m)
			index = self.text.index(f'{index} +1lines linestart')
		return None

	def _search_up(self, r: re.Pattern[str]) -> tuple[str, re.Match[str]] | None:
		# Search line-by-line from the insert cursor back to the start of the
		# text, taking the last match before the cursor on each line
		index = self.text.index(UI.INSERT)
		while True:
			linestart = self.text.index(f'{index} linestart')
			last_match: re.Match[str] | None = None
			for m in r.finditer(self.text.get(linestart, index)):
				last_match = m
			if last_match:
				return (linestart, last_match)
			if self.text.compare(linestart, '==', '1.0'):
				return None
			index = self.text.index(f'{linestart} -1lines lineend')

	def count(self) -> None:
		if not self.find.get():
			return
		r = self._compile_pattern()
		if r is None:
			return
		UI.MessageBox.showinfo(parent=self, title='Count', message=f'{len(r.findall(self.text.get("1.0", UI.END)))} matches found.')

	def replaceall(self) -> None:
		if not self.find.get():
			return
		r = self._compile_pattern()
		if r is None:
			return
		replaced, count = r.subn(self.replacewith.get(), self.text.get('1.0', UI.END))
		if count:
			with self.text.undo_group():
				self.text.delete('1.0', UI.END)
				self.text.insert('1.0', replaced.rstrip('\n'))
			self.text.mark_recolor_range('1.0', UI.END)
		UI.MessageBox.showinfo(parent=self, title='Replace Complete', message=f'{count} matches replaced.')

	def updatecolor(self) -> None:
		if self.resettimer:
			self.after_managed_cancel(self.resettimer)
			self.resettimer = None
		self.findentry['bg'] = self.findentry_c

	def on_hide(self) -> None:
		# Cancel any pending color-reset timer so it doesn't fire after close
		if self.resettimer:
			self.after_managed_cancel(self.resettimer)
			self.resettimer = None
		self.window_geometry_config.save_size(self)
