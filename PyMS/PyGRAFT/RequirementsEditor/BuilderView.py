
from ...Utilities import UIKit as UI

# The Builder mode of the requirements editor (not built yet)
class ReqBuilderView(UI.NotebookTab):
	def __init__(self, parent: UI.Misc) -> None:
		super().__init__(parent)
		UI.Label(self, text='The Builder is not built yet, use the Script editor.', justify=UI.CENTER).pack(expand=1)

	def load(self, entry_id: int | None, entry_name: str) -> None:
		pass

	def confirm_leave(self) -> bool:
		return True

	def confirm_apply_before_save(self) -> bool:
		return True
