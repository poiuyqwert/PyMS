
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.CodeHandlers.LanguageDefinition import LanguageContext

class AddedPluginsDialog(PyMSDialog):
	def __init__(self, parent: Misc, language_context: LanguageContext, added_plugin_ids: set[str]) -> None:
		self.language_context = language_context
		self.added_plugin_ids = list(added_plugin_ids)
		self.add = False
		super().__init__(parent, 'Plugins Required')

	def widgetize(self) -> Misc | None:
		Label(self, text='The changes being applied require at least one plugin to be used.\nPlease review and choose to continue or cancel.', justify=LEFT, anchor=W).pack(fill=X, expand=True, padx=5, pady=5)

		details_frame = Frame(self)
		frame = Frame(details_frame)
		Label(frame, text='Plugins:', justify=LEFT, anchor=W).pack(fill=X, expand=True)
		self.plugins_listbox = ScrolledListbox(frame, width=20)
		self.plugins_listbox.pack()
		self.plugins_listbox.bind(WidgetEvent.Listbox.Select.event(), self.update_reasons)
		frame.pack(side=LEFT, padx=5, pady=5)

		frame = Frame(details_frame)
		Label(frame, text='Reasons:', justify=LEFT, anchor=W).pack(fill=X, expand=True)
		self.reasons_listbox = ScrolledListbox(frame, width=40)
		self.reasons_listbox.pack()
		frame.pack(side=LEFT, padx=5, pady=5)
		details_frame.pack()

		frame = Frame(self)
		continue_button = Button(frame, text='Continue', width=10, command=self.yes)
		continue_button.pack(side=LEFT, padx=3)
		Button(frame, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3)
		frame.pack(pady=10, padx=5)

		self.plugins_listbox.insert(END, *self.added_plugin_ids)
		self.plugins_listbox.select_set(0)
		self.update_reasons()

		return continue_button

	def yes(self) -> None:
		self.add = True
		self.ok()

	def update_reasons(self, event: Event | None = None) -> None:
		selected_index: int = self.plugins_listbox.curselection()[0]
		plugin_id = self.added_plugin_ids[selected_index]
		reasons = self.language_context.get_reasons(plugin_id)
		self.reasons_listbox.delete(0, END)
		self.reasons_listbox.insert(END, *reasons)
