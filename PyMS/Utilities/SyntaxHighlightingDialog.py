
from .utils import fit
from . import UIKit as UI
from .PyMSDialog import PyMSDialog
from .SyntaxHighlightingFile import SyntaxHighlightingFile
from .ErrorDialog import ErrorDialog
from .PyMSError import PyMSError
from . import Config
from . import Assets

import os

from typing import Sequence

class SyntaxHighlightingDialog(PyMSDialog):
	def __init__(self, parent: UI.AnyWindow, highlight_components: Sequence[UI.HighlightComponent], select_file: Config.SelectFile):
		self.highlight_components = highlight_components
		self.select_file = select_file
		for highlight_component in self.highlight_components:
			highlight_component.highlight_style.store_state()
		self.updated = True
		PyMSDialog.__init__(self, parent, 'Color Settings', resizable=(False, False))

	def widgetize(self) -> UI.Widget:
		l = UI.Frame(self)
		self.listbox = UI.ScrolledListbox(l, font=UI.Font.fixed(), width=20, height=16)
		self.listbox.bind(UI.WidgetEvent.Listbox.Select(), self.highlight_component_selected)
		for highlight_component in self.highlight_components:
			self.listbox.insert(UI.END, highlight_component.name)
		self.listbox.select_set(0)
		self.listbox.pack(side=UI.TOP, fill=UI.BOTH, expand=1, padx=2, pady=2)

		self.toolbar = UI.Toolbar(l)
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import...')
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export...')
		self.toolbar.add_gap()
		self.reset_button = self.toolbar.add_button(Assets.get_image('reset'), self.show_reset_menu, 'Reset to Defaults')
		self.toolbar.pack(side=UI.TOP, fill=UI.X, padx=2)
		l.pack(side=UI.LEFT, fill=UI.Y)

		self.reset_menu = UI.Menu(self, tearoff=0)
		self.reset_menu.add_command(label='All Styles', command=self.reset_all)
		self.reset_menu.add_command(label='Selected Style', command=self.reset_selected)

		self.fg = UI.IntVar()
		self.fg.trace_add('write', lambda *_: self.toggle_foreground())
		self.bg = UI.IntVar()
		self.bg.trace_add('write', lambda *_: self.toggle_background())
		self.bold = UI.BooleanVar()
		self.bold.trace_add('write', lambda *_: self.toggle_bold())
		self.infotext = UI.StringVar()

		r = UI.Frame(self)
		opt = UI.LabelFrame(r, text='Style:', padx=5, pady=5)
		f = UI.Frame(opt)
		UI.Checkbutton(f, text='Foreground', variable=self.fg, width=20, anchor=UI.W).grid(sticky=UI.W)
		UI.Checkbutton(f, text='Background', variable=self.bg).grid(sticky=UI.W)
		UI.Checkbutton(f, text='Bold', variable=self.bold).grid(sticky=UI.W)
		self.fgcanvas = UI.Canvas(f, width=32, height=32, background='#000000')
		self.fgcanvas.bind(UI.Mouse.Click_Left(), self.select_foreground)
		self.fgcanvas.grid(column=1, row=0)
		self.bgcanvas = UI.Canvas(f, width=32, height=32, background='#000000')
		self.bgcanvas.bind(UI.Mouse.Click_Left(), self.select_background)
		self.bgcanvas.grid(column=1, row=1)
		f.pack(side=UI.TOP)
		UI.Label(opt, textvariable=self.infotext, height=6, justify=UI.LEFT).pack(side=UI.BOTTOM, fill=UI.X)
		opt.pack(side=UI.TOP, fill=UI.Y, expand=1, padx=2, pady=2)
		f = UI.Frame(r)
		ok = UI.Button(f, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.LEFT, padx=3)
		UI.Button(f, text='Cancel', width=10, command=self.cancel).pack(side=UI.LEFT)
		f.pack(side=UI.BOTTOM, pady=2)
		r.pack(side=UI.LEFT, fill=UI.Y)

		self.highlight_component_selected()

		return ok

	def selected_highlight_component(self) -> UI.HighlightComponent:
		return self.highlight_components[self.listbox.curselection()[0]]

	def highlight_component_selected(self, _event: UI.Event | None = None) -> None:
		highlight_component = self.selected_highlight_component()

		self.infotext.set(fit('  ' if '\n' in highlight_component.description else '', highlight_component.description, 35))

		if highlight_component.highlight_style.style.foreground is None:
			self.fg.set(0)
			self.fgcanvas['background'] = '#000000'
		else:
			self.fg.set(1)
			self.fgcanvas['background'] = highlight_component.highlight_style.style.foreground

		if highlight_component.highlight_style.style.background is None:
			self.bg.set(0)
			self.bgcanvas['background'] = '#000000'
		else:
			self.bg.set(1)
			self.bgcanvas['background'] = highlight_component.highlight_style.style.background

		self.bold.set(highlight_component.highlight_style.style.bold)

	def toggle_foreground(self) -> None:
		highlight_component = self.selected_highlight_component()
		if self.fg.get() and highlight_component.highlight_style.style.foreground is None:
			highlight_component.highlight_style.style.foreground = '#000000'
		elif not self.fg.get():
			highlight_component.highlight_style.style.foreground = None
			self.fgcanvas['background'] = '#000000'

	def toggle_background(self) -> None:
		highlight_component = self.selected_highlight_component()
		if self.bg.get() and highlight_component.highlight_style.style.background is None:
			highlight_component.highlight_style.style.background = '#000000'
		elif not self.bg.get():
			highlight_component.highlight_style.style.background = None
			self.bgcanvas['background'] = '#000000'

	def toggle_bold(self) -> None:
		highlight_component = self.selected_highlight_component()
		highlight_component.highlight_style.style.bold = self.bold.get()

	def hex_color(self, color: tuple[int, int, int]) -> str:
		return f'#{color[0]:02X}{color[1]:02X}{color[2]:02X}'

	def select_foreground(self, _event: UI.Event | None = None) -> None:
		highlight_component = self.selected_highlight_component()
		color,_ = UI.ColorChooser.askcolor(parent=self, initialcolor=highlight_component.highlight_style.style.foreground or '#000000', title='Select foreground color')
		if color:
			highlight_component.highlight_style.style.foreground = self.hex_color(color)
			self.fgcanvas['background'] = highlight_component.highlight_style.style.foreground
		self.focus_set()

	def select_background(self, _event: UI.Event | None = None) -> None:
		highlight_component = self.selected_highlight_component()
		color,_ = UI.ColorChooser.askcolor(parent=self, initialcolor=highlight_component.highlight_style.style.background or '#000000', title='Select background color')
		if color:
			highlight_component.highlight_style.style.background = self.hex_color(color)
			self.bgcanvas['background'] = highlight_component.highlight_style.style.background
		self.focus_set()

	def iimport(self) -> None:
		path = self.select_file.select_open(self)
		if not path:
			return
		highlights_file = SyntaxHighlightingFile()
		try:
			highlights_file.load(path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		if not highlights_file.apply(self.highlight_components):
			ErrorDialog(self, PyMSError('Import', 'The file has no syntax highlighting styles used by this program'))
			return
		self.highlight_component_selected()

	def export(self) -> None:
		path = self.select_file.select_save(self)
		if not path:
			return
		highlights_file = SyntaxHighlightingFile()
		if os.path.exists(path):
			# Merge into the existing file so styles for other programs are kept
			try:
				highlights_file.load(path)
			except PyMSError:
				if not UI.MessageBox.askyesno(parent=self, title='Overwrite?', message=f"'{os.path.basename(path)}' is not a valid syntax highlighting file, so its styles can't be kept. Overwrite it?"):
					return
				highlights_file = SyntaxHighlightingFile()
		highlights_file.update(self.highlight_components)
		try:
			highlights_file.save(path)
		except Exception as e:
			ErrorDialog(self, PyMSError('Export', f"Couldn't write '{path}'", cause=e))

	def show_reset_menu(self) -> None:
		self.reset_menu.post(self.reset_button.winfo_rootx(), self.reset_button.winfo_rooty() + self.reset_button.winfo_height())

	def reset_all(self) -> None:
		for highlight_component in self.highlight_components:
			highlight_component.highlight_style.reset()
		self.highlight_component_selected()

	def reset_selected(self) -> None:
		self.selected_highlight_component().highlight_style.reset()
		self.highlight_component_selected()

	def cancel(self, _event: UI.Event | None = None) -> None:
		self.updated = False
		for highlight_component in self.highlight_components:
			highlight_component.highlight_style.restore_state()
		PyMSDialog.ok(self)
