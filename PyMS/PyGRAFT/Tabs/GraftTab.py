
from __future__ import annotations

from ..GraftData import AnyGraftData

from ...Utilities import UIKit as UI
from ...Utilities.utils import fit

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

# A tab of the main window. The main window's list shows the tab's `entry_names()`, and selecting in the list selects that entry in the tab.
class GraftTab(UI.NotebookTab):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate) -> None:
		self.delegate = delegate
		# Index of the selected entry in `entry_names()`
		self.selected = 0
		super().__init__(parent)
		self.build_editor()

	def build_editor(self) -> None:
		# Tabs without an editor yet show a placeholder of the selected entry
		self.placeholder = UI.StringVar()
		UI.Label(self, textvariable=self.placeholder, justify=UI.CENTER).pack(expand=1)

	def get_graft_data(self) -> AnyGraftData:
		raise NotImplementedError(self.__class__.__name__ + '.get_graft_data()')

	def entry_names(self) -> list[str]:
		raise NotImplementedError(self.__class__.__name__ + '.entry_names()')

	def dimmed_entries(self) -> set[int]:
		# Indexes in `entry_names()` that the main window's list shows dimmed
		return set()

	@staticmethod
	def tip(widget: UI.Widget, name: str, text: str) -> UI.Tooltip:
		return UI.Tooltip(widget, GraftTab.tip_text(name, text))

	@staticmethod
	def tip_text(name: str, text: str) -> str:
		# The field's name, followed by its wrapped description
		return f'{name}:\n{fit("  ", text, end=True)[:-1]}'

	@staticmethod
	def format_entry(entry_id: int, max_id: int, name: str) -> str:
		return f'{entry_id:>{len(str(max_id))}}  {name}'

	def select(self, index: int) -> None:
		self.selected = index
		self.load_selected()

	def refresh(self) -> None:
		# Keep the selection in range after the entries change (loading a different file, importing, ...)
		entry_count = len(self.entry_names())
		self.selected = max(0, min(self.selected, entry_count - 1))
		self.load_selected()

	def load_selected(self) -> None:
		names = self.entry_names()
		if 0 <= self.selected < len(names):
			self.placeholder.set(f'{names[self.selected].strip()}\n\n(Editor not built yet)')
		else:
			self.placeholder.set('No entries')
