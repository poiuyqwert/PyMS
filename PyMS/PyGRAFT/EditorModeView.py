from __future__ import annotations

from ..Utilities import UIKit as UI

# A mode of an editor (like Builder or Script), editing the selected entry until its changes are explicitly applied.
# A mode with unapplied changes asks to apply them before the entry is left, the mode is switched, or the file is saved.
class EditorModeView(UI.NotebookTab):
	def __init__(self, parent: UI.Misc) -> None:
		super().__init__(parent)
		self.entry_id: int | None = None
		self.entry_name = ''

	def load(self, entry_id: int | None, entry_name: str) -> None:
		raise NotImplementedError(self.__class__.__name__ + '.load()')

	def is_edited(self) -> bool:
		raise NotImplementedError(self.__class__.__name__ + '.is_edited()')

	def apply(self) -> bool:
		# Stores the changes into the file, returning `False` if they couldn't be (or the user cancelled)
		raise NotImplementedError(self.__class__.__name__ + '.apply()')

	def revert(self) -> None:
		self.load(self.entry_id, self.entry_name)

	def confirm_leave(self) -> bool:
		# Asks to apply changes before leaving the editor, returning `False` to stay
		if not self.is_edited():
			return True
		apply = UI.MessageBox.askyesnocancel(parent=self, title='Apply Changes?', message=f"Apply changes to '{self.entry_name}'?", default=UI.MessageBox.YES)
		if apply is None:
			return False
		if apply:
			return self.apply()
		self.revert()
		return True

	def confirm_apply_before_save(self) -> bool:
		# Asks to apply changes before saving the file, returning `False` to cancel the save
		if not self.is_edited():
			return True
		apply = UI.MessageBox.askyesnocancel(parent=self, title='Apply Changes?', message=f"Apply changes to '{self.entry_name}' before saving?\n\nNo saves the file without them (they stay in the editor).", default=UI.MessageBox.YES)
		if apply is None:
			return False
		if apply:
			return self.apply()
		return True

	def can_deactivate(self) -> bool:
		return self.confirm_leave()
