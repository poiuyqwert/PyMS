
from ..Notebook import Notebook, NotebookTab

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from ....SettingsDialog import SettingsDialog
	from .SettingsView import SettingsView

class SettingsTab(NotebookTab):
	# TODO: Remove compat once SettingsDialog rewritten
	def __init__(self, notebook: Notebook, setdlg_compat: SettingsDialog | None = None):
		NotebookTab.__init__(self, notebook)
		self.settings_views: list[SettingsView] = []
		# TODO: Remove compat once SettingsDialog rewritten
		if setdlg_compat is None:
			self.setdlg_compat = cast(SettingsDialog, notebook.parent)
		else:
			self.setdlg_compat = setdlg_compat

	def register_settings_view(self, settings_view: SettingsView):
		self.settings_views.append(settings_view)
		# TODO: Remove compat once SettingsDialog rewritten
		def mark_edited_compat():
			self.setdlg_compat.edited = True
		settings_view.mark_edited_compat = mark_edited_compat

	# TODO: Remove compat once SettingsDialog rewritten
	def save(self, *__compat):
		for settings_view in self.settings_views:
			settings_view.save()
