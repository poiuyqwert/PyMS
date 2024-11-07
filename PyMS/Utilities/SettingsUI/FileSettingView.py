
from .SettingView import SettingView

from .. import Config
from ..UIKit import *
from ..EditedState import EditedState
from .. import Assets
from ..MPQHandler import MPQHandler

from typing import overload

class FileSettingView(SettingView):
	@overload
	def __init__(self, parent: Misc, edited_state: EditedState, name: str, description: str | None, setting: Config.File, mpq_handler: MPQHandler, mpq_history_config: Config.List, mpq_window_geometry_config: Config.WindowGeometry) -> None: ...
	@overload
	def __init__(self, parent: Misc, edited_state: EditedState, name: str, description: str | None, setting: Config.File, mpq_handler: None = None, mpq_history_config: None = None, mpq_window_geometry_config: None = None) -> None: ...
	def __init__(self, parent: Misc, edited_state: EditedState, name: str, description: str | None, setting: Config.File, mpq_handler: MPQHandler | None = None, mpq_history_config: Config.List | None = None, mpq_window_geometry_config: Config.WindowGeometry | None = None) -> None:
		super().__init__(parent, edited_state)
		self.setting = setting
		self.mpq_handler = mpq_handler
		self.mpq_history_config = mpq_history_config
		self.mpq_window_geometry_config = mpq_window_geometry_config
		
		self.variable = StringVar()
		self.variable.set(setting.file_path)
		self.variable.trace('w', self.changed)

		self.editable = True
		self.enabled = True

		Label(self, text=name, font=Font.default().bolded(), anchor=W).pack(fill=X, expand=1)
		if description is not None:
			Label(self, text=description, anchor=W).pack(fill=X, expand=1)
		entry_frame = Frame(self)
		self.entry = Entry(entry_frame, textvariable=self.variable)
		self.entry.pack(side=LEFT, fill=X, expand=1)
		self.find_button = Button(entry_frame, image=Assets.get_image('find'), width=20, height=20, command=self.select_file)
		self.find_button.pack(side=LEFT)
		self.find_mpq_button: Button | None = None
		if self.mpq_handler is not None:
			self.find_mpq_button = Button(entry_frame, image=Assets.get_image('openmpq'), width=20, height=20, command=self.select_mpq)
			self.find_mpq_button.pack(side=LEFT)
		entry_frame.pack(fill=X, expand=1)

	def _update_state(self) -> None:
		self.entry['state'] = NORMAL if (self.editable and self.enabled) else DISABLED

		self.find_button['state'] = NORMAL if self.enabled else DISABLED
		if self.find_mpq_button is not None:
			self.find_mpq_button['state'] = NORMAL if self.enabled else DISABLED

	def set_editable(self, editable: bool) -> None:
		self.editable = editable
		self._update_state()

	def set_enabled(self, enabled: bool):
		self.enabled = enabled
		self._update_state()

	def select_file(self) -> None:
		file_path = self.setting.select_file(self)
		if file_path:
			self.variable.set(file_path)

	def select_mpq(self) -> None:
		assert self.mpq_handler is not None
		assert self.mpq_history_config is not None
		assert self.mpq_window_geometry_config is not None
		file_path = self.setting.select_mpq(self, self.mpq_handler, self.mpq_history_config, self.mpq_window_geometry_config, self.setting._name, self.setting._filetypes[0])
		if file_path:
			self.variable.set(file_path)

	def changed(self, *_) -> None:
		edited = self.variable.get() != self.setting.file_path
		self.edited_state.mark_edited(edited)

	def save(self) -> None:
		self.setting.file_path = self.variable.get()
