
from __future__ import annotations

from .GraftTab import GraftTab
from ..GraftData import ButtonsGraftData

from ...Utilities import UIKit as UI

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

# Tab for the button cards of Buttons.graft (one per unit, followed by the special cards)
class ButtonCardsTab(GraftTab):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, graft_data: ButtonsGraftData) -> None:
		self.graft_data = graft_data
		super().__init__(parent, delegate)

	def get_graft_data(self) -> ButtonsGraftData:
		return self.graft_data

	def entry_names(self) -> list[str]:
		max_id = len(self.graft_data.graft.button_cards) - 1
		return [GraftTab.format_entry(card_id, max_id, self.delegate.data_context.button_card_name(card_id) or f'Button Card {card_id}') for card_id in range(len(self.graft_data.graft.button_cards))]
