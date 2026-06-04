
from ..Config import PyMPQConfig

from ...Utilities import UIKit as UI
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.EditedState import EditedState
from ...Utilities import Assets

class ListfileSettingsTab(SettingsTab):
	def __init__(self, notebook: UI.Notebook, edited_state: EditedState, config: PyMPQConfig):
		super().__init__(notebook)
		self.edited_state = edited_state
		self.config_ = config

		UI.Label(self, text='File Lists', font=UI.Font.default().bolded(), anchor=UI.W).pack(fill=UI.X)
		UI.Label(self, text="Note: Each file list added will increase the load time for archives", anchor=UI.W, justify=UI.LEFT).pack(fill=UI.X)
		self.listbox = UI.ScrolledListbox(self, width=35, height=1)
		self.listbox.pack(fill=UI.BOTH, padx=1, pady=1, expand=1)
		self.listbox.bind(UI.WidgetEvent.Listbox.Select(), lambda *e: self.action_states())
		for l in self.config_.settings.listfiles.data:
			self.listbox.insert(0,l)
		if self.listbox.size():
			self.listbox.select_set(0)

		self.toolbar = UI.Toolbar(self)
		self.toolbar.add_spacer(0, flexible=True)
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add MPQ', UI.Key.Insert)
		self.toolbar.add_spacer(0, flexible=True)
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove MPQ', UI.Key.Delete, enabled=False, tags='listfile_selected')
		self.toolbar.add_spacer(0, flexible=True)
		self.toolbar.pack(fill=UI.X, padx=51, pady=1)

		self.action_states()

	def is_listfile_selected(self) -> bool:
		return not not self.listbox.curselection()

	def action_states(self) -> None:
		self.toolbar.tag_enabled('listfile_selected', self.is_listfile_selected())

	def add(self, _event: UI.Event | None = None) -> None:
		add = self.config_.settings.last_path.listfiles.select_open_multiple(self)
		if add:
			for i in add:
				self.listbox.insert(UI.END,i)
			self.action_states()
			self.edited_state.mark_edited()

	def remove(self, _event: UI.Event | None = None) -> None:
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
		self.config_.settings.listfiles.data.clear()
		for i in range(self.listbox.size()): # type: ignore
			self.config_.settings.listfiles.data.append(self.listbox.get(i))
