
from ..Config import PyTILEConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class FilesSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyTILEConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		stat_txt = FileSettingView(self, edited_state, 'stat_txt.tbl', 'Contains Doodad group names', config.settings.files.stat_txt, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		stat_txt.pack(side=TOP, fill=X)
		self.register_settings_view(stat_txt)
