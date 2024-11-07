
from .utils import fit
from .UIKit import *
from .PyMSDialog import PyMSDialog

from typing import Sequence

class SyntaxHighlightingDialog(PyMSDialog):
	def __init__(self, parent: AnyWindow, highlight_components: Sequence[HighlightComponent]):
		self.highlight_components = highlight_components
		for highlight_component in self.highlight_components:
			highlight_component.highlight_style.store_state()
		self.updated = True
		PyMSDialog.__init__(self, parent, 'Color Settings', resizable=(False, False))

	def widgetize(self) -> Widget:
		self.listbox = ScrolledListbox(self, font=Font.fixed(), width=20, height=16)
		self.listbox.bind(WidgetEvent.Listbox.Select(), self.highlight_component_selected)
		for highlight_component in self.highlight_components:
			self.listbox.insert(END, highlight_component.name)
		self.listbox.select_set(0)
		self.listbox.pack(side=LEFT, fill=Y, padx=2, pady=2)

		self.fg = IntVar()
		self.fg.trace_add('write', lambda *_: self.toggle_foreground())
		self.bg = IntVar()
		self.bg.trace_add('write', lambda *_: self.toggle_background())
		self.bold = BooleanVar()
		self.bold.trace_add('write', lambda *_: self.toggle_bold())
		self.infotext = StringVar()

		r = Frame(self)
		opt = LabelFrame(r, text='Style:', padx=5, pady=5)
		f = Frame(opt)
		Checkbutton(f, text='Foreground', variable=self.fg, width=20, anchor=W).grid(sticky=W)
		Checkbutton(f, text='Background', variable=self.bg).grid(sticky=W)
		Checkbutton(f, text='Bold', variable=self.bold).grid(sticky=W)
		self.fgcanvas = Canvas(f, width=32, height=32, background='#000000')
		self.fgcanvas.bind(Mouse.Click_Left(), self.select_foreground)
		self.fgcanvas.grid(column=1, row=0)
		self.bgcanvas = Canvas(f, width=32, height=32, background='#000000')
		self.bgcanvas.bind(Mouse.Click_Left(), self.select_background)
		self.bgcanvas.grid(column=1, row=1)
		f.pack(side=TOP)
		Label(opt, textvariable=self.infotext, height=6, justify=LEFT).pack(side=BOTTOM, fill=X)
		opt.pack(side=TOP, fill=Y, expand=1, padx=2, pady=2)
		f = Frame(r)
		ok = Button(f, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3)
		Button(f, text='Cancel', width=10, command=self.cancel).pack(side=LEFT)
		f.pack(side=BOTTOM, pady=2)
		r.pack(side=LEFT, fill=Y)

		self.highlight_component_selected()

		return ok

	def selected_highlight_component(self) -> HighlightComponent:
		return self.highlight_components[self.listbox.curselection()[0]]

	def highlight_component_selected(self, event: Event | None = None) -> None:
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

	def select_foreground(self, event: Event | None = None) -> None:
		highlight_component = self.selected_highlight_component()
		color,_ = ColorChooser.askcolor(parent=self, initialcolor=highlight_component.highlight_style.style.foreground or '#000000', title='Select foreground color')
		if color:
			highlight_component.highlight_style.style.foreground = self.hex_color(color)
			self.fgcanvas['background'] = highlight_component.highlight_style.style.foreground
		self.focus_set()

	def select_background(self, event: Event | None = None) -> None:
		highlight_component = self.selected_highlight_component()
		color,_ = ColorChooser.askcolor(parent=self, initialcolor=highlight_component.highlight_style.style.background or '#000000', title='Select background color')
		if color:
			highlight_component.highlight_style.style.background = self.hex_color(color)
			self.fgcanvas['background'] = highlight_component.highlight_style.style.background
		self.focus_set()

	def cancel(self, event: Event | None = None) -> None:
		self.updated = False
		for highlight_component in self.highlight_components:
			highlight_component.highlight_style.restore_state()
		PyMSDialog.ok(self)
