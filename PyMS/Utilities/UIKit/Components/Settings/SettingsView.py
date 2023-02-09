
from ...Widgets import Frame

class SettingsView(Frame):
	def __init__(self, parent, settings):
		Frame.__init__(self, parent)
		self.edited = False
		self.settings = settings

	def mark_edited(self, edited=True):
		self.edited = edited
		# TODO: Remove compat once SettingsDialog rewritten
		if self.edited and hasattr(self, 'mark_edited_compat'):
			self.mark_edited_compat()

	def save(self):
		pass
