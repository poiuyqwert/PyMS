
from ..Config import PyMPQConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.IntSettingView import IntSettingView
from ...Utilities.EditedState import EditedState

class GeneralSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyMPQConfig):
		super().__init__(notebook)
		self.config_ = config

		max_files = IntSettingView(self, edited_state, 'Max Files', 'Max file capacity for new archives (cannot be changed for an existing archive)', self.config_.settings.defaults.maxfiles)
		max_files.pack(side=TOP, fill=X)
		self.register_settings_view(max_files)

		block_size = IntSettingView(self, edited_state, 'Block Size', 'Block size for new archives (default is 3)', self.config_.settings.defaults.blocksize)
		block_size.pack(side=TOP, fill=X)
		self.register_settings_view(block_size)
