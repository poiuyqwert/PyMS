
from ..CompressionSetting import CompressionOption, CompressionSetting

from ...Utilities import Assets
from ...Utilities.UIKit import *
from ...Utilities import Config
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.EditedState import EditedState

import os

class CompressionSettingsTab(SettingsTab):
	COMPRESSION_CHOICES = (
		CompressionOption.NoCompression,
		CompressionOption.Standard,
		CompressionOption.Deflate,
		CompressionOption.Audio
	)

	def __init__(self, notebook: Notebook, edited_state: EditedState, autocompression_config: Config.Dictionary) -> None:
		super().__init__(notebook)
		self.edited_state = edited_state
		self.autocompression_config = autocompression_config

		self.autocompression = dict(self.autocompression_config.data)

		self.extension = StringVar()
		self.extension.trace('w', lambda *e: self.action_states())

		left = Frame(self)
		Label(left, text='File Extension:', anchor=W, justify=LEFT).pack(fill=X)
		e = Frame(left)
		Entry(e, textvariable=self.extension).pack(side=LEFT, fill=X, expand=1)
		self.addbutton = Button(e, image=Assets.get_image('add'), width=20, height=20, command=self.add, state=DISABLED)
		self.addbutton.pack(side=LEFT, padx=2)
		e.pack(side=TOP)

		self.listbox = ScrolledListbox(left, width=15, height=1)
		self.listbox.bind(WidgetEvent.Listbox.Select(), lambda *e: self.select_extension())
		self.listbox.pack(fill=BOTH, padx=1, pady=1, expand=1)

		extensions = sorted(self.autocompression.keys())
		extensions.remove('Default')
		extensions.insert(0, 'Default')
		self.listbox.insert(END, *extensions)
		self.listbox.select_set(0)

		self.rembutton = Button(left, image=Assets.get_image('remove'), width=20, height=20, command=self.remove, state=DISABLED)
		self.rembutton.pack()
		left.pack(side=LEFT, fill=Y, padx=2)

		self.compression_index = IntVar()
		self.compression_level = IntVar()

		right = Frame(self)
		Label(right, text='Compression Type:', anchor=W, justify=LEFT).pack(fill=X)
		DropDown(right, self.compression_index, [type.display_name() for type in CompressionSettingsTab.COMPRESSION_CHOICES], self.choose_compression).pack(fill=X)
		
		self.levels_frame = Frame(right)
		Label(self.levels_frame, text='Compression Level:', anchor=W, justify=LEFT).pack(side=TOP, fill=X)
		self.levels_dropdown = DropDown(self.levels_frame, self.compression_level, [], self.choose_level)
		self.levels_dropdown.pack(side=BOTTOM, fill=X)
		right.pack(side=LEFT, fill=BOTH, expand=1, padx=2)

		self.select_extension()

	def action_states(self): # type: () -> None
		self.addbutton['state'] = NORMAL if self.extension.get() else DISABLED
		selected_index = int(self.listbox.curselection()[0])
		self.rembutton['state'] = NORMAL if selected_index else DISABLED

	def get_selected_extension(self): # type: () -> str
		extension_index = int(self.listbox.curselection()[0])
		return self.listbox.get(extension_index)

	def select_extension(self): # type: () -> None
		compression = CompressionSetting.parse_value(self.autocompression[self.get_selected_extension()])
		self.compression_index.set(CompressionSettingsTab.COMPRESSION_CHOICES.index(compression.type))
		self.update_levels(compression)
		self.action_states()

	def choose_compression(self, compression_type_index): # type: (int) -> None
		compression_type = CompressionSettingsTab.COMPRESSION_CHOICES[compression_type_index]
		extension = self.get_selected_extension()
		if CompressionSetting.parse_value(self.autocompression[extension]) == compression_type:
			return
		self.edited_state.mark_edited()
		compression = compression_type.setting()
		self.autocompression[extension] = str(compression)
		self.update_levels(compression)

	def update_levels(self, compression): # type: (CompressionSetting) -> None
		if compression.type.level_count() > 0:
			level_names = []
			for level in range(compression.type.level_count()):
				level_names.append(compression.type.setting(level).level_name())
			self.levels_dropdown.setentries(level_names)
			self.compression_level.set(compression.level)
			self.levels_frame.pack(pady=(5,0), fill=X)
		else:
			self.levels_frame.forget()

	def choose_level(self, level): # type: (int) -> None
		extension = self.get_selected_extension()
		compression = CompressionSetting.parse_value(self.autocompression[extension])
		if level != compression.level:
			self.autocompression[extension] = str(compression.type.setting(level))
			self.edited_state.mark_edited()
	
	def add(self, key=None): # type: (Event | None) -> None
		if self.addbutton['state'] == DISABLED:
			return
		e = self.extension.get()
		if not e.startswith(os.extsep):
			e = os.extsep + e
		self.extension.set('')
		self.action_states()
		if not e in self.autocompression:
			self.autocompression[e] = [0,0]
			s: int = self.listbox.size() # type: ignore[assignment]
			self.listbox.insert(END,e)
			self.listbox.select_clear(0,END)
			self.listbox.select_set(s)
			self.listbox.see(s)
			self.edited_state.mark_edited()
			self.action_states()

	def remove(self, key=None): # type: (Event | None) -> None
		if self.rembutton['state'] == DISABLED:
			return
		s = int(self.listbox.curselection()[0])
		del self.autocompression[self.listbox.get(s)]
		self.listbox.delete(s)
		if s == self.listbox.size():
			s -= 1
		self.listbox.select_set(s)
		self.listbox.see(s)
		self.edited_state.mark_edited()
		self.action_states()

	def save(self) -> None:
		self.autocompression_config.data = self.autocompression