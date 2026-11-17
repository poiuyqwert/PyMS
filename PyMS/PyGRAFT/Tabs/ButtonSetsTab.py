from __future__ import annotations

from .GraftTab import GraftTab
from ..GraftData import ButtonsGraftData
from ..ButtonSetEditor import ButtonSetEditor
from ..JumpTarget import JumpTarget
from ..UsedByView import UsedByView, UsedByReference

from ...Utilities import UIKit as UI

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

# Tab for the button sets of Buttons.graft
class ButtonSetsTab(GraftTab):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, graft_data: ButtonsGraftData) -> None:
		self.graft_data = graft_data
		super().__init__(parent, delegate)

	def build_editor(self) -> None:
		# Under the editor (outside its modes), so it's shown in both
		self.used_by = UsedByView(self, self.delegate, self.delegate.config_.show_used_by)
		self.used_by.pack(side=UI.BOTTOM, fill=UI.X, padx=2, pady=2)
		self.editor = ButtonSetEditor(self, self.delegate, self.graft_data)
		self.editor.pack(fill=UI.BOTH, expand=1)

	def activate(self) -> None:
		# The code colors are shared by every script editor, and may have been changed in another tab
		self.editor.update_highlight_styles()

	def get_graft_data(self) -> ButtonsGraftData:
		return self.graft_data

	def entry_names(self) -> list[str]:
		max_id = len(self.graft_data.graft.button_sets) - 1
		return [GraftTab.format_entry(set_id, max_id, self.delegate.data_context.button_set_name(set_id) or f'Button Set {set_id}') for set_id in range(len(self.graft_data.graft.button_sets))]

	def load_selected(self) -> None:
		set_count = len(self.graft_data.graft.button_sets)
		if 0 <= self.selected < set_count:
			self.editor.load(self.selected, self.entry_names()[self.selected].strip())
			self.used_by.set_references(self.used_by_references(self.selected))
		else:
			self.editor.load(None, '')
			self.used_by.set_references([])

	def used_by_references(self, set_id: int) -> list[UsedByReference]:
		# The button cards that show the button set
		references: list[UsedByReference] = []
		for card_id in self.graft_data.graft.button_cards_using_button_set(set_id):
			text = f'Button Card {card_id}'
			if name := self.delegate.data_context.button_card_name(card_id):
				text += f': {name}'
			references.append(UsedByReference(JumpTarget.button_cards, card_id, text))
		return references

	def confirm_leave(self) -> bool:
		return self.editor.confirm_leave()

	def confirm_apply_before_save(self) -> bool:
		return self.editor.confirm_apply_before_save()
