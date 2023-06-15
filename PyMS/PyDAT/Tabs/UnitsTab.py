
from .DATTab import DATTab
from .UnitTabs import *
from ..DataID import DATID, UnitsTabID, AnyID
from ..DATRef import DATRefs, DATRef

from ...FileFormats.DAT import DATUnit

from ...Utilities.UIKit import *

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

class UnitsTab(DATTab):
	DAT_ID = DATID.units

	def __init__(self, parent, delegate): # type: (Misc, MainDelegate) -> None
		DATTab.__init__(self, parent, delegate)
		self.dattabs = Notebook(self, FLAT)
		tabs = [
			('Basic', BasicUnitsTab),
			('Advanced', AdvancedUnitsTab),
			('Sounds', SoundsUnitsTab),
			('Graphics', GraphicsUnitsTab),
			('StarEdit', StarEditUnitsTab),
			('AI Actions', AIActionsUnitsTab),
		]
		for name,tab in tabs:
			self.dattabs.add_tab(tab(self.dattabs, delegate, self), name)
		self.dattabs.pack(fill=BOTH, expand=1)

		self.setup_used_by((
			DATRefs(DATID.units, lambda unit: (
				DATRef('Subunit 1', cast(DATUnit, unit).subunit1, dat_sub_tab=UnitsTabID.advanced),
				DATRef('Subunit 2', cast(DATUnit, unit).subunit2, dat_sub_tab=UnitsTabID.advanced),
				DATRef('Infestation', cast(DATUnit, unit).infestation, dat_sub_tab=UnitsTabID.advanced)
			)),
		))

	def active_tab(self): # type: () -> DATUnitsTab
		return cast(DATUnitsTab, self.dattabs.active)

	def copy_subtab(self): # type: () -> None
		self.active_tab().copy()

	def change_sub_tab(self, sub_tab_id): # type: (UnitsTabID) -> None
		self.dattabs.display(sub_tab_id.tab_name)

	def updated_pointer_entries(self, ids): # type: (list[AnyID]) -> None
		for tab,_ in list(self.dattabs.pages.values()):
			tab.updated_pointer_entries(ids)

	def load_data(self, id=None): # type: (int | None) -> None
		if not self.delegate.data_context.units.dat:
			return
		if id is not None:
			self.id = id
		entry = self.delegate.data_context.units.dat.get_entry(self.id)
		self.active_tab().load_data(entry)
		self.check_used_by_references()

	def save_data(self): # type: () -> None
		if not self.delegate.data_context.units.dat:
			return
		entry = self.delegate.data_context.units.dat.get_entry(self.id)
		if self.active_tab().save_data(entry):
			self.edited = True
			self.delegate.update_status_bar()
			self.check_used_by_references()

	def save(self, key=None): # type: (Event | None) -> None
		DATTab.save(self)
		if not self.edited:
			for tab,_ in list(self.dattabs.pages.values()):
				tab.edited = False