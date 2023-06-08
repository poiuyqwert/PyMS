
from ..Utilities.SettingsDialog import SettingsDialog
from ..Utilities.MPQSettings import MPQSettings
from ..Utilities.SettingsPanel import SettingsPanel
from ..Utilities.UIKit import *
from ..Utilities.UIKit.Components.Settings.SettingsTab import SettingsTab
from ..Utilities.UIKit.Components.Settings.ThemeSettingView import ThemeSettingView

class DATSettingsDialog(SettingsDialog):
	def widgetize(self):
		self.custom = IntVar()
		self.custom.set(self.settings.settings.get('customlabels', False))
		self.tabs = Notebook(self)
		self.mpqsettings = MPQSettings(self.tabs, self.mpqhandler.mpq_paths(), self.settings, self)
		self.tabs.add_tab(self.mpqsettings, 'MPQ Settings')
		for d in self.data:
			if d == 'Theme':
				tab = SettingsTab(self.tabs)
				theme_view = ThemeSettingView(tab, self.settings)
				theme_view.pack(fill=BOTH, expand=1)
				tab.register_settings_view(theme_view)
				self.pages.append(tab)
				self.tabs.add_tab(tab, d)
			else:
				f = Frame(self.tabs)
				f.parent = self
				pane = SettingsPanel(f, d[1], self.settings, self.mpqhandler)
				pane.pack(fill=BOTH, expand=1)
				self.pages.append(pane)
				if d[0].startswith('TBL'):
					Checkbutton(f, text='Use custom labels', variable=self.custom, command=self.doedit).pack()
				self.tabs.add_tab(f, d[0])
		self.tabs.pack(fill=BOTH, expand=1, padx=5, pady=5)
		btns = Frame(self)
		ok = Button(btns, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(btns, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		btns.pack()
		if self.err:
			self.after(1, self.showerr)
		return ok

	def doedit(self, e=None):
		self.edited = True

	def save_settings(self):
		SettingsDialog.save_settings(self)
		self.settings.settings.customlabels = not not self.custom.get()
