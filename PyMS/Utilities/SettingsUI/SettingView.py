
from __future__ import annotations

from ..EditedState import EditedState
from ..UIKit import Frame, Misc

class SettingView(Frame):
	def __init__(self, parent: Misc, edited_state: EditedState) -> None:
		Frame.__init__(self, parent)
		self.edited_state = edited_state

	def save(self) -> None:
		pass
