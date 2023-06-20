
from .SettingsView import SettingsView
from ..ScrolledListbox import ScrolledListbox
from ...Widgets import *
from ...EventPattern import *
from ...Font import Font
from ...Theme import Theme
from .... import Assets
from ....setutils import PYMS_SETTINGS

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ....Settings import Settings

class ThemeSettingView(SettingsView):
	def __init__(self, parent: Misc, settings: Settings):
		SettingsView.__init__(self, parent, settings)

		self.default = BooleanVar()
		self.default.trace('w', self.default_updated)
		self.author = StringVar()
		self.description = StringVar()

		Label(self, text='Theme:', font=Font.default().bolded(), anchor=W).pack(fill=X)
		Label(self, text='Choose a default theme for all programs or override the theme for this program.\nNote: If you change the theme you will need to restart the program for it to apply.', anchor=W, justify=LEFT).pack(fill=X, pady=(0,10))

		frame = Frame(self)
		frame.pack(fill=BOTH, expand=1)

		listbox_frame = Frame(frame)
		listbox_frame.pack(side=LEFT, fill=Y)
		self.listbox = ScrolledListbox(listbox_frame, width=20, height=10)
		self.listbox.bind(WidgetEvent.Listbox.Select(), self.selection_updated)
		self.listbox.pack(fill=Y, expand=1)
		Checkbutton(listbox_frame, text='Default', variable=self.default).pack()

		detail_frame = Frame(frame)
		detail_frame.pack(side=RIGHT, fill=BOTH, expand=1, padx=(10,0))

		Label(detail_frame, text='Author: ').grid(column=0, row=0, sticky=E)
		Label(detail_frame, textvariable=self.author, anchor=W).grid(column=1, row=0, sticky=W)
		Label(detail_frame, text='Description: ').grid(column=0, row=1, sticky=E)
		Label(detail_frame, textvariable=self.description, anchor=W).grid(column=1, row=1, sticky=W)

		detail_frame.grid_columnconfigure(0, weight=0)
		detail_frame.grid_columnconfigure(1, weight=1)

		self.listbox.insert(END, 'None')
		self.listbox.insert(END, *Assets.theme_list())

		theme = self.current_theme()
		self.default.set(not theme)
		if not theme:
			theme = self.current_default()
		if not theme in Assets.theme_list():
			theme = None
		theme_index = self.theme_index(theme)
		self.listbox.select_set(theme_index)
		self.listbox.see(theme_index)
		self.selection_updated()

	def current_default(self) -> (str | None):
		return PYMS_SETTINGS.get('theme')

	def current_theme(self) -> (str | None):
		return self.settings.get('theme')

	def selected_theme(self) -> (str | None):
		theme = None
		theme_index = self.listbox.curselection()[0]
		if theme_index > 0:
			theme = Assets.theme_list()[theme_index - 1]
		return theme

	def theme_index(self, theme: str | None) -> int:
		if theme is None or not theme in Assets.theme_list():
			return 0
		return 1 + Assets.theme_list().index(theme)

	def default_updated(self, *_) -> None:
		is_default = self.current_theme() is None
		if is_default != self.default.get():
			self.mark_edited()
		if self.default.get():
			theme = self.current_default()
			theme_index = self.theme_index(theme)
			self.listbox.select_clear(0, END)
			self.listbox.select_set(theme_index)
			self.listbox.see(theme_index)

	def selection_updated(self, _=None) -> None:
		self.preview_theme()

	def preview_theme(self) -> None:
		theme_name = None
		theme_index = self.listbox.curselection()[0]
		if theme_index > 0:
			theme_name = Assets.theme_list()[theme_index - 1]
		self.mark_edited()
		if not theme_name:
			self.author.set('None')
			self.description.set('Use the default style applied by your OS')
		else:
			try:
				theme = Theme(theme_name)
				self.author.set(theme.author)
				self.description.set(theme.description)
			except:
				self.author.set('ERROR')
				self.description.set("Couldn't load theme")

	def save(self) -> None:
		theme = None
		theme_index = self.listbox.curselection()[0]
		if theme_index > 0:
			theme = Assets.theme_list()[theme_index - 1]
		if self.default.get():
			self.settings['theme'] = None
			PYMS_SETTINGS['theme'] = theme
			PYMS_SETTINGS.save()
		else:
			self.settings['theme'] = theme
