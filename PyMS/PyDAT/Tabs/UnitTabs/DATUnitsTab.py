
from __future__ import annotations

from ...DATTabConveniences import DATTabConveniences

from ....FileFormats.DAT.UnitsDAT import DATUnit

from ....Utilities import UIKit as UI

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ...Delegates import MainDelegate, SubDelegate
	from ...DataID import DATID, AnyID

class DATUnitsTab(UI.NotebookTab, DATTabConveniences):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, sub_delegate: SubDelegate) -> None:
		self.delegate = delegate
		self.sub_delegate = sub_delegate
		self.edited = False
		UI.NotebookTab.__init__(self, parent)

	def copy(self) -> None:
		pass

	def jump(self, dat_id: DATID, entry_id: int) -> None:
		if 0 <= entry_id < self.delegate.data_context.dat_data(dat_id).entry_count():
			self.delegate.change_tab(dat_id)
			self.delegate.change_id(entry_id)

	def updated_pointer_entries(self, ids: list[AnyID]) -> None:
		pass

	def activate(self) -> None:
		if not self.delegate.data_context.units.dat:
			return
		entry = self.delegate.data_context.units.dat.get_entry(self.sub_delegate.id)
		self.load_data(entry)

	def deactivate(self) -> None:
		if not self.delegate.data_context.units.dat:
			return
		entry = self.delegate.data_context.units.dat.get_entry(self.sub_delegate.id)
		edited = self.save_data(entry)
		if edited:
			self.sub_delegate.edited = edited
			self.delegate.update_status_bar()

	def load_data(self, _entry: DATUnit) -> None:
		pass

	def save_data(self, _entry: DATUnit) -> bool:
		return False
