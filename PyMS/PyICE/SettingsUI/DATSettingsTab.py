
from ..Config import PyICEConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.SettingsUI.CheckboxSettingView import CheckboxSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class DATSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyICEConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		units = FileSettingView(self, edited_state, 'units.dat', 'Contains link to flingy.dat entries', config.settings.files.dat.units, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		units.pack(side=TOP, fill=X)
		self.register_settings_view(units)

		weapons = FileSettingView(self, edited_state, 'weapons.dat', 'Contains stat_txt.tbl string entry for weapon names', config.settings.files.dat.weapons, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		weapons.pack(side=TOP, fill=X)
		self.register_settings_view(weapons)

		flingy = FileSettingView(self, edited_state, 'flingy.dat', 'Contains link to sprite.dat entries', config.settings.files.dat.flingy, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		flingy.pack(side=TOP, fill=X)
		self.register_settings_view(flingy)

		sprites = FileSettingView(self, edited_state, 'sprites.dat', 'Contains link to images.dat entries', config.settings.files.dat.sprites, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		sprites.pack(side=TOP, fill=X)
		self.register_settings_view(sprites)

		images = FileSettingView(self, edited_state, 'images.dat', 'Contains link to IScript entries and images.tbl string indexs', config.settings.files.dat.images, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		images.pack(side=TOP, fill=X)
		self.register_settings_view(images)

		sfxdata = FileSettingView(self, edited_state, 'sfxdata.dat', 'Contains sfxdata.tbl string entries for mpq file paths', config.settings.files.dat.sfxdata, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		sfxdata.pack(side=TOP, fill=X)
		self.register_settings_view(sfxdata)
