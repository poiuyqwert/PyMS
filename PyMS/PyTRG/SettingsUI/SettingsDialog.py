
from .FilesSettingsTab import FilesSettingsTab
from ..Config import PyTRGConfig

from ...Utilities.SettingsUI.BaseSettingsDialog import BaseErrorableSettingsDialog, ErrorableSettingsDialogDelegate
from ...Utilities.SettingsUI.ThemeSettingsTab import ThemeSettingsTab
from ...Utilities.UIKit import *
from ...Utilities.PyMSError import PyMSError
from ...Utilities.MPQHandler import MPQHandler

class SettingsDialog(BaseErrorableSettingsDialog[PyTRGConfig]):
    def __init__(self, parent: Misc, config: PyTRGConfig, delegate: ErrorableSettingsDialogDelegate, err: PyMSError | None, mpq_handler: MPQHandler):
        self.mpq_handler = mpq_handler
        super().__init__(parent, config, delegate, err)

    def widgetize(self) -> Misc | None:
        widget = super().widgetize()

        self.add_tab('File Settings', FilesSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_, self.mpq_handler))
        self.add_tab('Theme', ThemeSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_.theme))

        return widget

    def setup_complete(self) -> None:
        self.config_.windows.settings.main.load(self)
        super().setup_complete()

    def dismiss(self) -> None:
        self.config_.windows.settings.main.save(self)
        super().dismiss()
