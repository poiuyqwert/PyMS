
from DATTab import DATTab
from BasicUnitsTab import BasicUnitsTab
from AdvancedUnitsTab import AdvancedUnitsTab
from SoundsUnitsTab import SoundsUnitsTab
from GraphicsUnitsTab import GraphicsUnitsTab
from StarEditUnitsTab import StarEditUnitsTab
from AIActionsUnitsTab import AIActionsUnitsTab
from DataID import DATID, UnitsTabID
from DATRef import DATRefs, DATRef

from ..Utilities.Notebook import Notebook

from Tkinter import *

class UnitsTab(DATTab):
	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
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
			self.dattabs.add_tab(tab(self.dattabs, toplevel, self), name)
		self.dattabs.pack(fill=BOTH, expand=1)

		self.setup_used_by((
			DATRefs(DATID.units, lambda unit: (
				DATRef('Subunit 1', unit.subunit1, dat_sub_tab=UnitsTabID.advanced),
				DATRef('Subunit 2', unit.subunit2, dat_sub_tab=UnitsTabID.advanced),
				DATRef('Infestation', unit.infestation, dat_sub_tab=UnitsTabID.advanced)
			)),
		))

	def get_dat_data(self):
		return self.toplevel.data_context.units

	def change_sub_tab(self, sub_tab_id):
		self.dattabs.display(sub_tab_id.id)

	def updated_data_files(self, dataids):
		for tab,_ in self.dattabs.pages.values():
			tab.updated_data_files(dataids)

	def updated_entry_names(self, datids):
		for tab,_ in self.dattabs.pages.values():
			tab.updated_entry_names(datids)

	def updated_entry_counts(self, datids):
		for tab,_ in self.dattabs.pages.values():
			tab.updated_entry_counts(datids)

	def load_data(self, id=None):
		if not self.toplevel.data_context.units.dat:
			return
		if id != None:
			self.id = id
		entry = self.toplevel.data_context.units.dat.get_entry(self.id)
		self.dattabs.active.load_data(entry)
		self.check_used_by_references()

	def save_data(self):
		if not self.toplevel.data_context.units.dat:
			return
		entry = self.toplevel.data_context.units.dat.get_entry(self.id)
		if self.dattabs.active.save_data(entry):
			self.edited = True
			self.toplevel.update_status_bar()
			self.check_used_by_references()

	def save(self, key=None):
		DATTab.save(self)
		if not self.edited:
			for tab,_ in self.dattabs.pages.values():
				tab.edited = False
