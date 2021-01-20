
from DATTab import DATTab
from ..FileFormats.TBL import decompile_string

from ..Utilities.utils import couriernew
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown

from Tkinter import *

class PortraitsTab(DATTab):
	data = 'Portdata.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		portdata = [] # ['None'] + [decompile_string(s) for s in self.toplevel.portdatatbl.strings]
		self.idle_entry = IntegerVar(0, [0,len(portdata)-1])
		self.idle_dd = IntVar()
		self.idle_change = IntegerVar(0, [0,255])
		self.idle_unknown = IntegerVar(0, [0,255])

		self.talking_entry = IntegerVar(0, [0,len(portdata)-1])
		self.talking_dd = IntVar()
		self.talking_change = IntegerVar(0, [0,255])
		self.talking_unknown = IntegerVar(0, [0,255])

		l = LabelFrame(frame, text='Idle Portrait:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='SMK Dir:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.idle_entry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.idle_dd_view = DropDown(f, self.idle_dd, portdata, self.idle_entry, width=30)
		self.idle_dd_view.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'SMK Dir', 'PortFile')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=(5,0))
		s = Frame(l)
		f = Frame(s)
		Label(f, text='SMK Change:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.idle_change, font=couriernew, width=3).pack(side=LEFT)
		self.tip(f, 'SMK Change', 'PortSMKChange')
		f.pack(side=LEFT)
		f = Frame(s)
		Label(f, text='Unknown:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.idle_unknown, font=couriernew, width=3).pack(side=LEFT)
		self.tip(f, 'Unknown', 'PortUnk1')
		f.pack(side=RIGHT)
		s.pack(fill=BOTH, padx=5, pady=(0,5))
		l.pack(fill=X)

		l = LabelFrame(frame, text='Talking Portrait:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='SMK Dir:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.talking_entry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.talking_dd_view = DropDown(f, self.talking_dd, portdata, self.talking_entry, width=30)
		self.talking_dd_view.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'SMK Dir', 'PortFile')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=(5,0))
		s = Frame(l)
		f = Frame(s)
		Label(f, text='SMK Change:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.talking_change, font=couriernew, width=3).pack(side=LEFT)
		self.tip(f, 'SMK Change', 'PortSMKChange')
		f.pack(side=LEFT)
		f = Frame(s)
		Label(f, text='Unknown:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.talking_unknown, font=couriernew, width=3).pack(side=LEFT)
		self.tip(f, 'Unknown', 'PortUnk1')
		f.pack(side=RIGHT)
		s.pack(fill=BOTH, padx=5, pady=(0,5))
		l.pack(fill=X, pady=5)

		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('units.dat', ['Portrait']),
		]
		self.setuplistbox()

	def loadsave_data(self):
		return (
			('PortraitFile','SMKChange','Unknown'),
			(
				(self.id, (self.idle_entry, self.idle_change, self.idle_unknown)),
				(self.id + self.dat.count/2, (self.talking_entry, self.talking_change, self.talking_unknown))
			)
		)
	def load_data(self, id=None):
		if not self.dat:
			return
		if id != None:
			self.id = id
		labels,values = self.loadsave_data()
		for id,variables in values:
			for label,var in zip(labels, variables):
				var.set(self.dat.get_value(id, label))
	def save_data(self):
		if not self.dat:
			return
		labels,values = self.loadsave_data()
		for id,variables in values:
			for label,var in zip(labels, variables):
				v = var.get()
				if self.dat.get_value(id, label) != v:
					self.edited = True
					self.dat.set_value(id, label, v)

	def files_updated(self):
		self.dat = self.toplevel.portraits
		portdata = ['None'] + [decompile_string(s) for s in self.toplevel.portdatatbl.strings]
		self.idle_entry.range[1] = len(portdata)-1
		self.idle_dd_view.setentries(portdata)
		self.idle_entry.editvalue()
		self.talking_entry.range[1] = len(portdata)-1
		self.talking_dd_view.setentries(portdata)
		self.talking_entry.editvalue()
