
from ..Config import PyAIConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class FileSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyAIConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		stat_txt = FileSettingView(parent=self, edited_state=edited_state, name='stat_txt.tbl', description='Contains names of AI Scripts, Units, Upgrades, and Tech', setting=config.settings.files.stat_txt, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		stat_txt.pack(side=TOP, fill=X)
		self.register_settings_view(stat_txt)

		# unitnames = FileSettingView(self, edited_state, 'unitnames.tbl', 'Contains Unit names for expanded dat files', config.settings.files.tbls.unitnames, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		# unitnames.pack(side=TOP, fill=X)
		# self.register_settings_view(unitnames)

		unitsdat = FileSettingView(parent=self, edited_state=edited_state, name='units.dat', description='Used to check if a unit is a Building or has Air/Ground attacks', setting=config.settings.files.dat.units, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		unitsdat.pack(side=TOP, fill=X)
		self.register_settings_view(unitsdat)

		upgradesdat = FileSettingView(parent=self, edited_state=edited_state, name='upgrades.dat', description='Used to specify upgrade string entries in stat_txt.tbl', setting=config.settings.files.dat.upgrades, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		upgradesdat.pack(side=TOP, fill=X)
		self.register_settings_view(upgradesdat)

		techdat = FileSettingView(parent=self, edited_state=edited_state, name='techdata.dat', description='Used to specify technology string entries in stat_txt.tbl', setting=config.settings.files.dat.techdata, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		techdat.pack(side=TOP, fill=X)
		self.register_settings_view(techdat)
