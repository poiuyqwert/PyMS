
from .Config import PyAIConfig

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Assets

class ExternalDefDialog(PyMSDialog):
	def __init__(self, parent: AnyWindow, config: PyAIConfig):
		self.config_ = config
		PyMSDialog.__init__(self, parent, 'External Definitions')

	def widgetize(self) -> Widget:
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add File', Key.Insert)
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove File', Key.Insert, tags='def_selected')
		self.toolbar.pack(side=TOP, fill=X, padx=2, pady=1)

		self.listbox = ScrolledListbox(self, font=Font.fixed(), width=1, height=1)
		self.listbox.pack(fill=BOTH, expand=1)
		self.update()
		self.listbox.bind(WidgetEvent.Listbox.Select(), lambda _: self.action_states())

		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		buttons.pack()

		return ok

	def setup_complete(self) -> None:
		self.minsize(200,150)
		self.config_.windows.extdefs.load_size(self)

	def def_selected(self) -> bool:
		return not not self.listbox.curselection()

	def action_states(self) -> None:
		self.toolbar.tag_enabled('def_selected', self.def_selected())

	def add(self, key: Event | None = None) -> None:
		iimport = self.config_.last_path.txt.extdefs.select_open(self)
		if iimport and iimport not in self.config_.extdefs.data:
			self.config_.extdefs.data.append(iimport)
			self.update()
			self.listbox.select_set(END)
			self.listbox.see(END)

	def remove(self, key: Event | None = None) -> None:
		if not self.def_selected():
			return
		index = int(self.listbox.curselection()[0])
		del self.config_.extdefs.data[index]
		if self.config_.extdefs.data and index == len(self.config_.extdefs.data):
			self.listbox.select_set(index-1)
			self.listbox.see(index-1)
		self.update()

	def update(self) -> None:
		sel = 0
		if self.listbox.size():
			sel = self.listbox.curselection()[0]
			self.listbox.delete(0, END)
		if self.config_.extdefs.data:
			for file in self.config_.extdefs.data:
				self.listbox.insert(END, file)
			self.listbox.select_set(sel)
		self.action_states()

	def ok(self, event: Event | None = None) -> None:
		PyMSDialog.ok(self)

	def dismiss(self) -> None:
		self.config_.windows.extdefs.save_size(self)
		PyMSDialog.dismiss(self)
