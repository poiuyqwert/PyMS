
from ..Config import PyMPQConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.EditedState import EditedState
from ...Utilities import Assets

class ListfileSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyMPQConfig):
		super().__init__(notebook)
		self.edited_state = edited_state
		self.config_ = config

		Label(self, text='File Lists', font=Font.default().bolded(), anchor=W).pack(fill=X)
		Label(self, text="Note: Each file list added will increase the load time for archives", anchor=W, justify=LEFT).pack(fill=X)
		self.listbox = ScrolledListbox(self, width=35, height=1)
		self.listbox.pack(fill=BOTH, padx=1, pady=1, expand=1)
		self.listbox.bind(WidgetEvent.Listbox.Select(), lambda *e: self.action_states())
		for l in self.config_.settings.listfiles.data:
			self.listbox.insert(0,l)
		if self.listbox.size():
			self.listbox.select_set(0)

		self.toolbar = Toolbar(self)
		self.toolbar.add_spacer(0, flexible=True)
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add MPQ', Key.Insert)
		self.toolbar.add_spacer(0, flexible=True)
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove MPQ', Key.Delete, enabled=False, tags='listfile_selected')
		self.toolbar.add_spacer(0, flexible=True)
		self.toolbar.pack(fill=X, padx=51, pady=1)

		self.action_states()

	def is_listfile_selected(self) -> bool:
		return not not self.listbox.curselection()

	def action_states(self) -> None:
		self.toolbar.tag_enabled('listfile_selected', self.is_listfile_selected())

	def add(self, key: Event | None = None) -> None:
		add = self.config_.settings.last_path.listfiles.select_open(self)
		if add:
			for i in add:
				self.listbox.insert(END,i)
			self.action_states()
			self.edited_state.mark_edited()

	def remove(self, key: Event | None = None) -> None:
		if not self.is_listfile_selected():
			return
		i = int(self.listbox.curselection()[0])
		self.listbox.delete(i)
		if self.listbox.size():
			i = min(i,self.listbox.size()-1) # type: ignore
			self.listbox.select_set(i)
			self.listbox.see(i)
		self.action_states()
		self.edited_state.mark_edited()

	def save(self) -> None:
		self.config_.settings.listfiles.data.remove()
		for i in range(self.listbox.size()): # type: ignore
			self.config_.settings.listfiles.data.append(self.listbox.get(i))
