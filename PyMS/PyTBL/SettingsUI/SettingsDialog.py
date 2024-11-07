
from .PreviewSettingsTab import PreviewSettingsTab
from ..Config import PyTBLConfig

from ...Utilities.SettingsUI.BaseSettingsDialog import BaseErrorableSettingsDialog, ErrorableSettingsDialogDelegate
from ...Utilities.SettingsUI.ThemeSettingsTab import ThemeSettingsTab
from ...Utilities.SettingsUI.MPQSettingsTab import MPQSettingsTab
from ...Utilities.UIKit import *
from ...Utilities.PyMSError import PyMSError
from ...Utilities.MPQHandler import MPQHandler

class SettingsDialog(BaseErrorableSettingsDialog[PyTBLConfig]):
	def __init__(self, parent: Misc, config: PyTBLConfig, delegate: ErrorableSettingsDialogDelegate, err: PyMSError | None, mpq_handler: MPQHandler):
		self.mpq_handler = mpq_handler
		super().__init__(parent, config, delegate, err)

	def widgetize(self) -> Misc | None:
		widget = super().widgetize()

		self.add_tab('MPQ Settings', MPQSettingsTab(self.notebook, self.edited_state.sub_state(), self.mpq_handler, self.config_.settings.mpqs, self.config_.settings.last_path.mpqs))
		self.add_tab('Preview Settings', PreviewSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_, self.mpq_handler))
		self.add_tab('Theme', ThemeSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_.theme))

		return widget

	def setup_complete(self) -> None:
		self.config_.windows.settings.main.load_size(self)
		super().setup_complete()

	def dismiss(self) -> None:
		self.config_.windows.settings.main.save_size(self)
		super().dismiss()
