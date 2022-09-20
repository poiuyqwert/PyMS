
from .DATTabConveniences import DATTabConveniences

from ..Utilities.Notebook import NotebookTab

class DATUnitsTab(NotebookTab, DATTabConveniences):
	def __init__(self, parent, toplevel, parent_tab):
		self.toplevel = toplevel
		self.parent_tab = parent_tab
		self.tabcopy = None
		self.edited = False
		NotebookTab.__init__(self, parent)

	def copy(self):
		pass

	def jump(self, datid, entry_id):
		if entry_id < self.toplevel.data_context.dat_data(datid).entry_count() - 1:
			self.toplevel.dattabs.display(datid.tab_id)
			self.toplevel.changeid(entry_id)

	def updated_pointer_entries(self, ids):
		pass

	def activate(self):
		if not self.toplevel.data_context.units.dat:
			return
		entry = self.toplevel.data_context.units.dat.get_entry(self.parent_tab.id)
		self.load_data(entry)

	def deactivate(self):
		if not self.toplevel.data_context.units.dat:
			return
		entry = self.toplevel.data_context.units.dat.get_entry(self.parent_tab.id)
		edited = self.save_data(entry)
		if edited:
			self.parent_tab.edited = edited
			self.toplevel.update_status_bar()

	def load_data(self, id):
		pass
	def save_data(self, id):
		return False
