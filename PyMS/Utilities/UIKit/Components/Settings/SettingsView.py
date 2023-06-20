
from ...Widgets import Frame, Misc

from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
	from ....Settings import Settings

class SettingsView(Frame):
	def __init__(self, parent: Misc, settings: Settings) -> None:
		Frame.__init__(self, parent)
		self.edited = False
		self.settings = settings
		# TODO: Remove compat once SettingsDialog rewritten
		self.mark_edited_compat: Callable[[], None] | None = None

	def mark_edited(self, edited: bool = True) -> None:
		self.edited = edited
		# TODO: Remove compat once SettingsDialog rewritten
		if self.edited and self.mark_edited_compat is not None:
			self.mark_edited_compat()

	def save(self) -> None:
		pass
