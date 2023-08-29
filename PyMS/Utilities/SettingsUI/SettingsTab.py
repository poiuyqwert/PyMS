
from __future__ import annotations

from ..UIKit.Components.Notebook import Notebook, NotebookTab
from .SettingView import SettingView

class SettingsTab(NotebookTab):
	def __init__(self, notebook: Notebook):
		NotebookTab.__init__(self, notebook)
		self.settings_views: list[SettingView] = []

	def register_settings_view(self, settings_view: SettingView):
		self.settings_views.append(settings_view)

	def save(self):
		for settings_view in self.settings_views:
			settings_view.save()
