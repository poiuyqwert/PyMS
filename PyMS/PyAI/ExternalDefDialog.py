
from .Config import PyAIConfig

from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Assets

class ExternalDefDialog(PyMSDialog):
	def __init__(self, parent: UI.AnyWindow, config: PyAIConfig):
		self.config_ = config
		PyMSDialog.__init__(self, parent, 'External Definitions')

	def widgetize(self) -> UI.Widget:
		self.toolbar = UI.Toolbar(self)
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add File', UI.Key.Insert)
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove File', UI.Key.Delete, tags='def_selected')
		self.toolbar.pack(side=UI.TOP, fill=UI.X, padx=2, pady=1)

		self.listbox = UI.ScrolledListbox(self, font=UI.Font.fixed(), width=1, height=1)
		self.listbox.pack(fill=UI.BOTH, expand=1)
		self.update_list()
		self.listbox.bind(UI.WidgetEvent.Listbox.Select(), lambda _: self.action_states())

		buttons = UI.Frame(self)
		ok = UI.Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.LEFT, padx=3, pady=3)
		buttons.pack()

		return ok

	def setup_complete(self) -> None:
		self.minsize(200,150)
		self.config_.windows.extdefs.load_size(self)

	def def_selected(self) -> bool:
		return not not self.listbox.curselection()

	def action_states(self) -> None:
		self.toolbar.tag_enabled('def_selected', self.def_selected())

	def add(self, _event: UI.Event | None = None) -> None:
		iimport = self.config_.last_path.txt.extdefs.select_open(self)
		if iimport and iimport not in self.config_.extdefs.data:
			self.config_.extdefs.data.append(iimport)
			self.update_list()
			self.listbox.select_set(UI.END)
			self.listbox.see(UI.END)

	def remove(self, _event: UI.Event | None = None) -> None:
		if not self.def_selected():
			return
		index = int(self.listbox.curselection()[0])
		del self.config_.extdefs.data[index]
		if self.config_.extdefs.data and index == len(self.config_.extdefs.data):
			self.listbox.select_set(index-1)
			self.listbox.see(index-1)
		self.update_list()

	def update_list(self) -> None:
		sel = 0
		if self.listbox.size():
			selection = self.listbox.curselection()
			if selection:
				sel = selection[0]
			self.listbox.delete(0, UI.END)
		if self.config_.extdefs.data:
			for file in self.config_.extdefs.data:
				self.listbox.insert(UI.END, file)
			self.listbox.select_set(sel)
		self.action_states()

	def ok(self, _event: UI.Event | None = None) -> None:
		PyMSDialog.ok(self)

	def dismiss(self) -> None:
		self.config_.windows.extdefs.save_size(self)
		PyMSDialog.dismiss(self)
