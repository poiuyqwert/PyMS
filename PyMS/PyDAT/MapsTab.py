
from DATTab import DATTab
from ..FileFormats.TBL import decompile_string

from ..Utilities.utils import couriernew
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown

from Tkinter import *

class MapsTab(DATTab):
	data = 'Mapdata.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		frame = Frame(self)

		mapdata = [] # [decompile_string(s) for s in self.toplevel.mapdatatbl.strings]
		self.missionentry = IntegerVar(0, [0,len(mapdata)])
		self.missiondd = IntVar()

		l = LabelFrame(frame, text='Campaign Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Mission Dir:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.missionentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.missions = DropDown(f, self.missiondd, mapdata, self.missionentry, width=30)
		self.missions.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Mission Dir', 'MapFile')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		frame.pack(side=LEFT, fill=Y)

	def files_updated(self):
		self.dat = self.toplevel.campaigns
		mapdata = [decompile_string(s) for s in self.toplevel.mapdatatbl.strings]
		self.missions.none_value = len(mapdata)
		self.missionentry.range[1] = len(mapdata)
		self.missions.setentries(mapdata + ['None'])
		self.missionentry.editvalue()

	def load_entry(self, entry):
		self.missionentry.set(entry.map_file)

	def save_entry(self, entry):
		if self.missionentry.get() != entry.map_file:
			entry.map_file = self.missionentry.get()
			self.edited = True
