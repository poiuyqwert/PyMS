
from .SettingView import SettingView

from .. import Config
from .. import UIKit as UI
from ..EditedState import EditedState
from .. import Assets
from ..MPQHandler import MPQHandler

from typing import overload, Any

class FileSettingView(SettingView):
	@overload
	def __init__(self, *, parent: UI.Misc, edited_state: EditedState, name: str, description: str | None, setting: Config.File, mpq_handler: MPQHandler, mpq_history_config: Config.List, mpq_window_geometry_config: Config.WindowGeometry) -> None: ...
	@overload
	def __init__(self, *, parent: UI.Misc, edited_state: EditedState, name: str, description: str | None, setting: Config.File, mpq_handler: None = None, mpq_history_config: None = None, mpq_window_geometry_config: None = None) -> None: ...
	def __init__(self, *, parent: UI.Misc, edited_state: EditedState, name: str, description: str | None, setting: Config.File, mpq_handler: MPQHandler | None = None, mpq_history_config: Config.List | None = None, mpq_window_geometry_config: Config.WindowGeometry | None = None) -> None:
		super().__init__(parent, edited_state)
		self.setting = setting
		self.mpq_handler = mpq_handler
		self.mpq_history_config = mpq_history_config
		self.mpq_window_geometry_config = mpq_window_geometry_config

		self.variable = UI.StringVar()
		self.variable.set(setting.file_path)
		self.variable.trace_add('write', self.changed)

		self.editable = True
		self.enabled = True

		UI.Label(self, text=name, font=UI.Font.default().bolded(), anchor=UI.W).pack(fill=UI.X, expand=1)
		if description is not None:
			UI.Label(self, text=description, anchor=UI.W).pack(fill=UI.X, expand=1)
		entry_frame = UI.Frame(self)
		self.entry = UI.Entry(entry_frame, textvariable=self.variable)
		self.entry.pack(side=UI.LEFT, fill=UI.X, expand=1)
		self.find_button = UI.Button(entry_frame, image=Assets.get_image('find'), width=20, height=20, command=self.select_file)
		self.find_button.pack(side=UI.LEFT)
		self.find_mpq_button: UI.Button | None = None
		if self.mpq_handler is not None:
			self.find_mpq_button = UI.Button(entry_frame, image=Assets.get_image('openmpq'), width=20, height=20, command=self.select_mpq)
			self.find_mpq_button.pack(side=UI.LEFT)
		entry_frame.pack(fill=UI.X, expand=1)

	def _update_state(self) -> None:
		self.entry['state'] = UI.NORMAL if (self.editable and self.enabled) else UI.DISABLED

		self.find_button['state'] = UI.NORMAL if self.enabled else UI.DISABLED
		if self.find_mpq_button is not None:
			self.find_mpq_button['state'] = UI.NORMAL if self.enabled else UI.DISABLED

	def set_editable(self, editable: bool) -> None:
		self.editable = editable
		self._update_state()

	def set_enabled(self, enabled: bool) -> None:
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
		file_path = self.setting.select_mpq(parent=self, mpq_handler=self.mpq_handler, history_config=self.mpq_history_config, window_geometry_config=self.mpq_window_geometry_config, name=self.setting.name, filetype=self.setting.filetypes[0])
		if file_path:
			self.variable.set(file_path)

	def changed(self, *_: Any) -> None:
		edited = self.variable.get() != self.setting.file_path
		self.edited_state.mark_edited(edited)

	def save(self) -> None:
		self.setting.file_path = self.variable.get()
