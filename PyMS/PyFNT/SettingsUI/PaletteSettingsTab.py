
from ..Config import PyFNTConfig

from ...Utilities import UIKit as UI
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class PaletteSettingsTab(SettingsTab):
	def __init__(self, notebook: UI.Notebook, edited_state: EditedState, config: PyFNTConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		tfontgam = FileSettingView(parent=self, edited_state=edited_state, name='tfontgam.pcx', description='The special palette which holds the text color.', setting=config.settings.files.tfontgam, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		tfontgam.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(tfontgam)
