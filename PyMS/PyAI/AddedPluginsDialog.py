
from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.CodeHandlers.LanguageDefinition import LanguageContext

class AddedPluginsDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, language_context: LanguageContext, added_plugin_ids: set[str]) -> None:
		self.language_context = language_context
		self.added_plugin_ids = list(added_plugin_ids)
		self.add = False
		super().__init__(parent, 'Plugins Required')

	def widgetize(self) -> UI.Misc | None:
		UI.Label(self, text='The changes being applied require at least one plugin to be used.\nPlease review and choose to continue or cancel.', justify=UI.LEFT, anchor=UI.W).pack(fill=UI.X, expand=True, padx=5, pady=5)

		details_frame = UI.Frame(self)
		frame = UI.Frame(details_frame)
		UI.Label(frame, text='Plugins:', justify=UI.LEFT, anchor=UI.W).pack(fill=UI.X, expand=True)
		self.plugins_listbox = UI.ScrolledListbox(frame, width=20)
		self.plugins_listbox.pack()
		self.plugins_listbox.bind(UI.WidgetEvent.Listbox.Select.event(), self.update_reasons)
		frame.pack(side=UI.LEFT, padx=5, pady=5)

		frame = UI.Frame(details_frame)
		UI.Label(frame, text='Reasons:', justify=UI.LEFT, anchor=UI.W).pack(fill=UI.X, expand=True)
		self.reasons_listbox = UI.ScrolledListbox(frame, width=40)
		self.reasons_listbox.pack()
		frame.pack(side=UI.LEFT, padx=5, pady=5)
		details_frame.pack()

		frame = UI.Frame(self)
		continue_button = UI.Button(frame, text='Continue', width=10, command=self.yes)
		continue_button.pack(side=UI.LEFT, padx=3)
		UI.Button(frame, text='Cancel', width=10, command=self.cancel).pack(side=UI.LEFT, padx=3)
		frame.pack(pady=10, padx=5)

		self.plugins_listbox.insert(UI.END, *self.added_plugin_ids)
		self.plugins_listbox.select_set(0)
		self.update_reasons()

		return continue_button

	def yes(self) -> None:
		self.add = True
		self.ok()

	def update_reasons(self, _event: UI.Event | None = None) -> None:
		selection = self.plugins_listbox.curselection()
		if not selection:
			return
		selected_index = selection[0]
		plugin_id = self.added_plugin_ids[selected_index]
		reasons = self.language_context.get_reasons(plugin_id)
		self.reasons_listbox.delete(0, UI.END)
		self.reasons_listbox.insert(UI.END, *reasons)
