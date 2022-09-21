
from .DATTab import DATTab
from .DataID import DATID, DataID, UnitsTabID
from .DATRef import DATRefs, DATRef

from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.UIKit import *
from ..Utilities.ScrollView import ScrollView

class PortraitsTab(DATTab):
	DAT_ID = DATID.portdata

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		scrollview = ScrollView(self)

		self.idle_entry = IntegerVar(0, [0,0])
		self.idle_dd = IntVar()
		self.idle_change = IntegerVar(0, [0,255])
		self.idle_unknown = IntegerVar(0, [0,255])

		self.talking_entry = IntegerVar(0, [0,0])
		self.talking_dd = IntVar()
		self.talking_change = IntegerVar(0, [0,255])
		self.talking_unknown = IntegerVar(0, [0,255])

		l = LabelFrame(scrollview.content_view, text='Idle Portrait:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='SMK Dir:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.idle_entry, font=Font.fixed(), width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.idle_dd_view = DropDown(f, self.idle_dd, [], self.idle_entry, width=30)
		self.idle_dd_view.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'SMK Dir', 'PortFile')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=(5,0))
		s = Frame(l)
		f = Frame(s)
		Label(f, text='SMK Change:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.idle_change, font=Font.fixed(), width=3).pack(side=LEFT)
		self.tip(f, 'SMK Change', 'PortSMKChange')
		f.pack(side=LEFT)
		f = Frame(s)
		Label(f, text='Unknown:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.idle_unknown, font=Font.fixed(), width=3).pack(side=LEFT)
		self.tip(f, 'Unknown', 'PortUnk1')
		f.pack(side=RIGHT)
		s.pack(fill=BOTH, padx=5, pady=(0,5))
		l.pack(fill=X)

		l = LabelFrame(scrollview.content_view, text='Talking Portrait:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='SMK Dir:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.talking_entry, font=Font.fixed(), width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.talking_dd_view = DropDown(f, self.talking_dd, [], self.talking_entry, width=30)
		self.talking_dd_view.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'SMK Dir', 'PortFile')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=(5,0))
		s = Frame(l)
		f = Frame(s)
		Label(f, text='SMK Change:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.talking_change, font=Font.fixed(), width=3).pack(side=LEFT)
		self.tip(f, 'SMK Change', 'PortSMKChange')
		f.pack(side=LEFT)
		f = Frame(s)
		Label(f, text='Unknown:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.talking_unknown, font=Font.fixed(), width=3).pack(side=LEFT)
		self.tip(f, 'Unknown', 'PortUnk1')
		f.pack(side=RIGHT)
		s.pack(fill=BOTH, padx=5, pady=(0,5))
		l.pack(fill=X, pady=5)

		scrollview.pack(fill=BOTH, expand=1)

		self.setup_used_by((
			DATRefs(DATID.units, lambda unit: (
				DATRef('Portrait', unit.portrait, dat_sub_tab=UnitsTabID.graphics),
			)),
		))

	def updated_pointer_entries(self, ids):
		if DataID.portdatatbl in ids:
			portdata = ('None',) + self.toplevel.data_context.portdatatbl.strings
			limit = len(self.toplevel.data_context.portdatatbl.strings)
			self.idle_dd_view.setentries(portdata)
			self.idle_entry.range[1] = limit
			self.talking_dd_view.setentries(portdata)
			self.talking_entry.range[1] = limit

		if DATID.units in ids and self.toplevel.dattabs.active == self:
			self.check_used_by_references()

	def load_entry(self, entry):
		self.idle_entry.set(entry.idle.portrait_file)
		self.idle_change.set(entry.idle.smk_change)
		self.idle_unknown.set(entry.idle.unknown)
		self.talking_entry.set(entry.talking.portrait_file)
		self.talking_change.set(entry.talking.smk_change)
		self.talking_unknown.set(entry.talking.unknown)

	def save_entry(self, entry):
		if self.idle_entry.get() != entry.idle.portrait_file:
			entry.idle.portrait_file = self.idle_entry.get()
			self.edited = True
		if self.idle_change.get() != entry.idle.smk_change:
			entry.idle.smk_change = self.idle_change.get()
			self.edited = True
		if self.idle_unknown.get() != entry.idle.unknown:
			entry.idle.unknown = self.idle_unknown.get()
			self.edited = True
		if self.talking_entry.get() != entry.talking.portrait_file:
			entry.talking.portrait_file = self.talking_entry.get()
			self.edited = True
		if self.talking_change.get() != entry.talking.smk_change:
			entry.talking.smk_change = self.talking_change.get()
			self.edited = True
		if self.talking_unknown.get() != entry.talking.unknown:
			entry.talking.unknown = self.talking_unknown.get()
			self.edited = True
