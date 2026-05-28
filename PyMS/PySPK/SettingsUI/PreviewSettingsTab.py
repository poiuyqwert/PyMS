
from ..Config import PySPKConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class PreviewSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PySPKConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		unit_pal = FileSettingView(parent=self, edited_state=edited_state, name='platform.wpe', description='The palette which holds the star palette.', setting=config.settings.files.platform_wpe, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		unit_pal.pack(side=TOP, fill=X)
		self.register_settings_view(unit_pal)
