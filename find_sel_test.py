#!/usr/bin/env python3
# Standalone test for Find dialog selection visibility (PyAI Code Editor on Windows).
#
# FindReplaceDialog marks a match by adding the 'sel' tag to the editor's Text while
# keyboard focus stays in the Find dialog. An unfocused Text draws 'sel' using
# -inactiveselectbackground, which may be empty (= hidden) on some platforms.
# Each scenario opens an editor + Find window pair with different Text settings.

from __future__ import annotations

import platform
import re
import sys
import tkinter as tk
from tkinter import font as tkfont

SAMPLE_LINES = [
	'script_name Terran Expansion (TMCx):',
	'# A comment about the script',
	'\tstart_town()',
	'\twait(50)',
	'\tbuild(1, Command Center, 80)',
	'\ttrain(4, SCV)',
	'\tdefense_build_gg(1, Marine)',
	'\twait_build(1, Barracks)',
	'\tgoto(TMCx_loop)',
	'--TMCx_loop--',
	'\tattack_add(8, Marine)',
	'\tattack_prepare()',
	'\twait(500)',
	'\tstop()',
	'',
]
FIND_TEXT = 'Marine'
FOUND_BG = '#FFD84D'


class Scenario:
	def __init__(self, title, description, exportselection=False, inactive=None, sel_bg=None, found_tag=False):
		self.title = title
		self.description = description
		self.exportselection = exportselection
		# None = leave Tk default; 'selectbackground' = copy the widget's selectbackground; otherwise a color
		self.inactive = inactive
		self.sel_bg = sel_bg
		self.found_tag = found_tag


SCENARIOS = [
	Scenario('1. Baseline (PyMS CodeText)',
		'exportselection=False, inactiveselectbackground left at Tk default. Expected to fail on Windows.'),
	Scenario('2. exportselection=True only',
		'exportselection=True, inactiveselectbackground left at Tk default.',
		exportselection=True),
	Scenario('3. inactiveselectbackground only',
		'exportselection=False, inactiveselectbackground = selectbackground.',
		inactive='selectbackground'),
	Scenario('4. Both changed',
		'exportselection=True, inactiveselectbackground = selectbackground.',
		exportselection=True, inactive='selectbackground'),
	Scenario('5. inactiveselectbackground = gray',
		'exportselection=False, inactiveselectbackground = #C3C3C3 (Tk\'s X11 default).',
		inactive='#C3C3C3'),
	Scenario('6. Explicit sel tag background',
		'Baseline + tag_configure(\'sel\', background=...). Does a tag-level bg survive losing focus?',
		sel_bg=FOUND_BG),
	Scenario('7. Separate "found" tag',
		'Baseline + a separate "found" tag with its own background, raised above sel. Focus independent.',
		found_tag=True),
]


def describe_text(text):
	return (
		f"exportselection={text.cget('exportselection')!r}  "
		f"selectbackground={text.cget('selectbackground')!r}  "
		f"inactiveselectbackground={text.cget('inactiveselectbackground')!r}  "
		f"sel background={text.tag_cget('sel', 'background')!r}"
	)


def copy_to_clipboard(widget, text):
	widget.clipboard_clear()
	widget.clipboard_append(text)
	# Process the clipboard request so it survives the window closing
	widget.update()


def add_copy_bar(parent, get_text, extra_buttons=()):
	bar = tk.Frame(parent)
	bar.pack(fill=tk.X, padx=6, pady=(0, 6))
	status = tk.Label(bar, fg='#606060')
	def copy():
		copy_to_clipboard(parent, get_text())
		status['text'] = 'Copied!'
		parent.after(1500, lambda: status.configure(text=''))
	tk.Button(bar, text='Copy Info', command=copy).pack(side=tk.LEFT)
	for title, command in extra_buttons:
		tk.Button(bar, text=title, command=command).pack(side=tk.LEFT, padx=(4, 0))
	status.pack(side=tk.LEFT, padx=6)
	return bar


class EditorWindow(tk.Toplevel):
	def __init__(self, parent, scenario):
		tk.Toplevel.__init__(self, parent)
		self.scenario = scenario
		self.title(f'Editor - {scenario.title}')
		self.geometry('760x420')

		tk.Label(self, text=scenario.description, anchor=tk.W, justify=tk.LEFT, wraplength=740).pack(fill=tk.X, padx=6, pady=(6, 0))
		self.info = tk.Label(self, anchor=tk.W, justify=tk.LEFT, fg='#606060', wraplength=740)
		self.info.pack(fill=tk.X, padx=6, pady=(2, 6))
		add_copy_bar(self, self.info_text, extra_buttons=(('Show Find', self.show_find),))

		frame = tk.Frame(self, bd=2, relief=tk.SUNKEN)
		frame.pack(fill=tk.BOTH, expand=1, padx=6, pady=(0, 6))
		vscroll = tk.Scrollbar(frame)
		vscroll.pack(side=tk.RIGHT, fill=tk.Y)
		# Mirrors PyMS/Utilities/UIKit/Components/CodeText.py
		font = tkfont.nametofont('TkFixedFont').copy()
		font.configure(size=12)
		self.text = tk.Text(frame, height=1, font=font, undo=True, maxundo=100, wrap=tk.NONE, highlightthickness=0, yscrollcommand=vscroll.set, exportselection=scenario.exportselection)
		self.text.config(bd=0)
		self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
		vscroll.config(command=self.text.yview)
		self.text.tag_configure('sel', foreground='')

		if scenario.inactive == 'selectbackground':
			self.text.config(inactiveselectbackground=self.text.cget('selectbackground'))
		elif scenario.inactive:
			self.text.config(inactiveselectbackground=scenario.inactive)
		if scenario.sel_bg:
			self.text.tag_configure('sel', background=scenario.sel_bg)
		if scenario.found_tag:
			self.text.tag_configure('found', background=FOUND_BG)
			self.text.tag_raise('found')
		self.text.tag_raise('sel')

		for n in range(6):
			self.text.insert(tk.END, f'# ---- Block {n + 1} ----\n')
			self.text.insert(tk.END, '\n'.join(SAMPLE_LINES))
		self.text.mark_set(tk.INSERT, '1.0')
		self.text.edit_reset()
		self.text.edit_modified(False)
		self.update_info()

		self.find_window: FindWindow | None = FindWindow(self)
		self.protocol('WM_DELETE_WINDOW', self.close)

	def update_info(self, extra=''):
		focus = self.focus_get()
		focus_name = 'None' if focus is None else focus.winfo_class()
		self.info['text'] = f'{describe_text(self.text)}\nfocus: {focus_name}  {extra}'

	def info_text(self):
		return f"{self.title()}\n{self.scenario.description}\n{self.info['text']}"

	def show_find(self):
		if self.find_window is None:
			self.find_window = FindWindow(self)
		else:
			self.find_window.focus_entry()

	def close(self):
		if self.find_window is not None:
			self.find_window.destroy()
		self.destroy()


class FindWindow(tk.Toplevel):
	def __init__(self, editor):
		tk.Toplevel.__init__(self, editor)
		self.editor = editor
		self.text = editor.text
		self.title('Find')
		self.transient(editor)
		self.resizable(False, False)

		row = tk.Frame(self)
		row.pack(fill=tk.X, padx=6, pady=6)
		tk.Label(row, text='Find:').pack(side=tk.LEFT)
		self.find = tk.StringVar(value=FIND_TEXT)
		self.entry = tk.Entry(row, textvariable=self.find, width=24)
		self.entry.pack(side=tk.LEFT, padx=4)
		tk.Button(row, text='Find Next', command=self.findnext).pack(side=tk.LEFT)
		self.status = tk.Label(self, anchor=tk.W, fg='#606060')
		self.status.pack(fill=tk.X, padx=6, pady=(0, 6))

		self.entry.bind('<Return>', self.findnext)
		self.protocol('WM_DELETE_WINDOW', self.close)

		editor.update_idletasks()
		self.geometry(f'+{editor.winfo_rootx() + 380}+{editor.winfo_rooty() + 60}')
		# Like FindReplaceDialog.on_show
		self.after(100, self.focus_entry)

	# Closing Find leaves the editor open, to check the selection survives focus changes
	def close(self):
		self.editor.find_window = None
		self.destroy()
		self.editor.after(100, lambda: self.editor.update_info('(Find window closed)'))

	def focus_entry(self):
		self.lift()
		self.entry.focus_force()
		self.entry.select_range(0, tk.END)
		self.after(50, self.editor.update_info)

	def findnext(self, event=None):
		f = self.find.get()
		if not f:
			return
		r = re.compile(re.escape(f), re.I)
		found = self.search_down(r)
		if not found:
			# Wrap around for convenience
			self.text.mark_set(tk.INSERT, '1.0')
			found = self.search_down(r)
		if not found:
			self.status['text'] = "Can't find text."
			return
		from_index, m = found
		s = f'{from_index} +{m.start(0)}c'
		e = f'{from_index} +{m.end(0)}c'
		self.select_match(s, e, insert=e)
		self.status['text'] = f'Found at {self.text.index(s)}'
		self.after(50, lambda: self.editor.update_info(f'sel ranges: {[str(i) for i in self.text.tag_ranges("sel")]}'))

	# Same as FindReplaceDialog._select_match, plus the scenario variations
	def select_match(self, start, end, insert):
		self.text.tag_remove('sel', '1.0', tk.END)
		self.text.tag_add('sel', start, end)
		if self.editor.scenario.found_tag:
			self.text.tag_remove('found', '1.0', tk.END)
			self.text.tag_add('found', start, end)
		self.text.mark_set(tk.INSERT, insert)
		self.text.see(start)

	# Same as FindReplaceDialog._search_down
	def search_down(self, r):
		end = self.text.index(tk.END)
		index = self.text.index(tk.INSERT)
		if index == self.text.index(f'{index} lineend'):
			index = self.text.index(f'{index} +1lines linestart')
		while self.text.compare(index, '<', end):
			m = r.search(self.text.get(index, f'{index} lineend'))
			if m:
				return (index, m)
			index = self.text.index(f'{index} +1lines linestart')
		return None


class MainWindow(tk.Tk):
	def __init__(self):
		tk.Tk.__init__(self)
		self.title('Find Selection Test')

		probe = tk.Text(self)
		header = (
			f'Platform: {platform.platform()}\n'
			f'Python: {sys.version.split()[0]}   Tk: {self.tk.call("info", "patchlevel")}   windowing system: {self.tk.call("tk", "windowingsystem")}\n'
			f'Fresh Text defaults: {describe_text(probe)}'
		)
		probe.destroy()
		tk.Label(self, text=header, anchor=tk.W, justify=tk.LEFT, wraplength=560).pack(fill=tk.X, padx=8, pady=8)
		add_copy_bar(self, lambda: header)
		tk.Label(self, text='Each scenario opens an editor plus a Find window. Press Return / Find Next in the Find window and check whether the match is highlighted in the editor while focus stays in the Find entry.', anchor=tk.W, justify=tk.LEFT, wraplength=560).pack(fill=tk.X, padx=8, pady=(0, 8))

		for scenario in SCENARIOS:
			tk.Button(self, text=scenario.title, anchor=tk.W, command=lambda s=scenario: EditorWindow(self, s)).pack(fill=tk.X, padx=8, pady=2)
		tk.Button(self, text='Quit', command=self.destroy).pack(pady=8)


if __name__ == '__main__':
	MainWindow().mainloop()
