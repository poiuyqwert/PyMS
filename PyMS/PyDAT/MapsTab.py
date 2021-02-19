
from DATTab import DATTab
from DataID import DataID

from ..Utilities.utils import couriernew
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.UIKit import *

class MapsTab(DATTab):
	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		frame = Frame(self)

		self.missionentry = IntegerVar(0, [0,0])
		self.missiondd = IntVar()

		l = LabelFrame(frame, text='Campaign Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Mission Dir:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.missionentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.missions = DropDown(f, self.missiondd, [], self.missionentry, width=30)
		self.missions.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Mission Dir', 'MapFile')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		frame.pack(side=LEFT, fill=Y)

	def get_dat_data(self):
		return self.toplevel.data_context.campaign

	def updated_data_files(self, dataids):
		if DataID.mapdatatbl in dataids:
			self.missions.setentries(self.toplevel.data_context.mapdatatbl.strings + ('None',))
			self.missionentry.range[1] = len(self.toplevel.data_context.mapdatatbl.strings)

	def load_entry(self, entry):
		self.missionentry.set(entry.map_file)

	def save_entry(self, entry):
		if self.missionentry.get() != entry.map_file:
			entry.map_file = self.missionentry.get()
			self.edited = True
