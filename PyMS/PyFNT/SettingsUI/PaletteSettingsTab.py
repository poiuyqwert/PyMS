
from ..Config import PyFNTConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class PaletteSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyFNTConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		tfontgam = FileSettingView(self, edited_state, 'tfontgam.pcx', 'The special palette which holds the text color.', config.settings.files.tfontgam, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		tfontgam.pack(side=TOP, fill=X)
		self.register_settings_view(tfontgam)
