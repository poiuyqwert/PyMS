
from ..Config import PyMPQConfig

from ...Utilities import UIKit as UI
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.IntSettingView import IntSettingView
from ...Utilities.EditedState import EditedState

class GeneralSettingsTab(SettingsTab):
	def __init__(self, notebook: UI.Notebook, edited_state: EditedState, config: PyMPQConfig):
		super().__init__(notebook)
		self.config_ = config

		max_files = IntSettingView(parent=self, edited_state=edited_state, name='Max Files', description='Max file capacity for new archives (cannot be changed for an existing archive)', setting=self.config_.settings.defaults.maxfiles)
		max_files.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(max_files)

		block_size = IntSettingView(parent=self, edited_state=edited_state, name='Block Size', description='Block size for new archives (default is 3)', setting=self.config_.settings.defaults.blocksize)
		block_size.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(block_size)
