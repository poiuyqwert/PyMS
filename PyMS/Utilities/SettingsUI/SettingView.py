
from __future__ import annotations

from ..EditedState import EditedState
from .. import UIKit as UI

class SettingView(UI.Frame):
	def __init__(self, parent: UI.Misc, edited_state: EditedState) -> None:
		UI.Frame.__init__(self, parent)
		self.edited_state = edited_state

	def save(self) -> None:
		pass
