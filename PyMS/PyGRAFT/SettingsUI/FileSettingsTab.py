
from ..Config import PyGRAFTConfig

from ...Utilities import UIKit as UI
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class FileSettingsTab(SettingsTab):
	def __init__(self, notebook: UI.Notebook, edited_state: EditedState, config: PyGRAFTConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		files = (
			('stat_txt.tbl', 'Contains the names of Units, Upgrades, Technologies, and Orders', config.settings.files.stat_txt),
			('unitnames.tbl', 'Contains Unit names for expanded dat files (optional, Unit names come from stat_txt.tbl when it is not found)', config.settings.files.unitnames),
			('units.dat', 'Used to name Units', config.settings.files.dat.units),
			('upgrades.dat', 'Used to look up Upgrade names in stat_txt.tbl', config.settings.files.dat.upgrades),
			('techdata.dat', 'Used to look up Technology names in stat_txt.tbl', config.settings.files.dat.techdata),
			('orders.dat', 'Used to look up Order names in stat_txt.tbl', config.settings.files.dat.orders),
		)
		for name, description, setting in files:
			view = FileSettingView(parent=self, edited_state=edited_state, name=name, description=description, setting=setting, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
			view.pack(side=UI.TOP, fill=UI.X)
			self.register_settings_view(view)
