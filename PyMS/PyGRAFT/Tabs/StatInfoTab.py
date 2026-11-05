
from __future__ import annotations

from .GraftTab import GraftTab
from ..GraftData import ButtonsGraftData

from ...Utilities import UIKit as UI

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

# Tab for the unit stat info of Buttons.graft (one per unit)
class StatInfoTab(GraftTab):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, graft_data: ButtonsGraftData) -> None:
		self.graft_data = graft_data
		super().__init__(parent, delegate)

	def get_graft_data(self) -> ButtonsGraftData:
		return self.graft_data

	def entry_names(self) -> list[str]:
		max_id = len(self.graft_data.graft.stat_info) - 1
		return [GraftTab.format_entry(unit_id, max_id, self.delegate.data_context.unit_display_name(unit_id) or f'Unit {unit_id}') for unit_id in range(len(self.graft_data.graft.stat_info))]
