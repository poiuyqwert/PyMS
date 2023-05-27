
from ..Notebook import NotebookTab

class SettingsTab(NotebookTab):
	# TODO: Remove compat once SettingsDialog rewritten
	def __init__(self, notebook, setdlg_compat=None):
		NotebookTab.__init__(self, notebook)
		self.settings_views = []
		# TODO: Remove compat once SettingsDialog rewritten
		if setdlg_compat is None:
			self.setdlg_compat = notebook.parent
		else:
			self.setdlg_compat = setdlg_compat

	def register_settings_view(self, settings_view):
		self.settings_views.append(settings_view)
		# TODO: Remove compat once SettingsDialog rewritten
		def mark_edited_compat():
			if hasattr(self.setdlg_compat, 'edited'):
				self.setdlg_compat.edited = True
		settings_view.mark_edited_compat = mark_edited_compat

	# TODO: Remove compat once SettingsDialog rewritten
	def save(self, *__compat):
		for settings_view in self.settings_views:
			settings_view.save()
