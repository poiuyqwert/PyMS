
from ..Config import PyICEConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class DATSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyICEConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		units = FileSettingView(parent=self, edited_state=edited_state, name='units.dat', description='Contains link to flingy.dat entries', setting=config.settings.files.dat.units, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		units.pack(side=TOP, fill=X)
		self.register_settings_view(units)

		weapons = FileSettingView(parent=self, edited_state=edited_state, name='weapons.dat', description='Contains stat_txt.tbl string entry for weapon names', setting=config.settings.files.dat.weapons, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		weapons.pack(side=TOP, fill=X)
		self.register_settings_view(weapons)

		flingy = FileSettingView(parent=self, edited_state=edited_state, name='flingy.dat', description='Contains link to sprite.dat entries', setting=config.settings.files.dat.flingy, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		flingy.pack(side=TOP, fill=X)
		self.register_settings_view(flingy)

		sprites = FileSettingView(parent=self, edited_state=edited_state, name='sprites.dat', description='Contains link to images.dat entries', setting=config.settings.files.dat.sprites, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		sprites.pack(side=TOP, fill=X)
		self.register_settings_view(sprites)

		images = FileSettingView(parent=self, edited_state=edited_state, name='images.dat', description='Contains link to IScript entries and images.tbl string indexs', setting=config.settings.files.dat.images, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		images.pack(side=TOP, fill=X)
		self.register_settings_view(images)

		sfxdata = FileSettingView(parent=self, edited_state=edited_state, name='sfxdata.dat', description='Contains sfxdata.tbl string entries for mpq file paths', setting=config.settings.files.dat.sfxdata, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		sfxdata.pack(side=TOP, fill=X)
		self.register_settings_view(sfxdata)
