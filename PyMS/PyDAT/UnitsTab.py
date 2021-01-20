
from ..Utilities.Notebook import Notebook

from DATTab import DATTab
from BasicUnitsTab import BasicUnitsTab
from AdvancedUnitsTab import AdvancedUnitsTab
from SoundsUnitsTab import SoundsUnitsTab
from GraphicsUnitsTab import GraphicsUnitsTab
from StarEditUnitsTab import StarEditUnitsTab
from AIActionsUnitsTab import AIActionsUnitsTab

from Tkinter import *

class UnitsTab(DATTab):
	data = 'Units.txt'

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

	def files_updated(self):
		self.dat = self.toplevel.units
		for tab,_ in self.dattabs.pages.values():
			tab.files_updated()

	def load_data(self, id=None):
		if not self.dat:
			return
		if id != None:
			self.id = id
		entry = self.dat.get_entry(self.id)
		self.dattabs.active.load_data(entry)
	def save_data(self):
		if not self.dat:
			return
		entry = self.dat.get_entry(self.id)
		if self.dattabs.active.save_data(entry):
			self.edited = True
			self.toplevel.action_states()

	def save(self, key=None):
		DATTab.save(self)
		if not self.edited:
			for tab,_ in self.dattabs.pages.values():
				tab.edited = False
