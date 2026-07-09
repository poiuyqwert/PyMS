
from ..Config import PyTILEConfig

from ...Utilities import UIKit as UI
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class FilesSettingsTab(SettingsTab):
	def __init__(self, notebook: UI.Notebook, edited_state: EditedState, config: PyTILEConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		stat_txt = FileSettingView(parent=self, edited_state=edited_state, name='stat_txt.tbl', description='Contains Doodad group names', setting=config.settings.files.stat_txt, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		stat_txt.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(stat_txt)
