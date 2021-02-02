
from ..Utilities.utils import fit
from ..Utilities.Notebook import NotebookTab
from ..Utilities.Tooltip import Tooltip
from ..Utilities.DataCache import DATA_CACHE

from Tkinter import Checkbutton

class DATUnitsTab(NotebookTab):
	def __init__(self, parent, toplevel, parent_tab):
		self.toplevel = toplevel
		self.parent_tab = parent_tab
		self.icon = self.toplevel.icon
		self.tabcopy = None
		self.edited = False
		NotebookTab.__init__(self, parent)

	def tip(self, obj, tipname, hint):
		obj.tooltip = Tooltip(obj, '%s:\n' % tipname + fit('  ', self.toplevel.data_context.hints[hint], end=True)[:-1], mouse=True)

	def makeCheckbox(self, frame, var, txt, hint):
		c = Checkbutton(frame, text=txt, variable=var)
		self.tip(c, txt, hint)
		return c

	def jump(self, type, id, o=0):
		i = id.get() + o
		if i < len(DATA_CACHE['%s.txt' % type]) - 1:
			self.toplevel.dattabs.display(type)
			self.toplevel.changeid(i=i)

	def update_entry_names(self):
		pass

	def update_entry_counts(self):
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
			self.toplevel.action_states()

	def load_data(self, id):
		pass
	def save_data(self, id):
		return False
