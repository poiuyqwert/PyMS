
from __future__ import annotations

from .DATTab import DATTab
from ..DataID import DATID, DataID, UnitsTabID, AnyID
from ..DATRef import DATRefs, DATRef

from ...FileFormats.DAT import DATUnit, DATPortraits

from ...Utilities import UIKit as UI

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

class PortraitsTab(DATTab):
	DAT_ID = DATID.portdata

	def __init__(self, parent: UI.Misc, delegate: MainDelegate) -> None:
		DATTab.__init__(self, parent, delegate)
		scrollview = UI.ScrollView(self)

		self.idle_entry = UI.IntegerVar(0, [0,0])
		self.idle_dd = UI.IntVar()
		self.idle_change = UI.IntegerVar(0, [0,255])
		self.idle_unknown = UI.IntegerVar(0, [0,255])

		self.talking_entry = UI.IntegerVar(0, [0,0])
		self.talking_dd = UI.IntVar()
		self.talking_change = UI.IntegerVar(0, [0,255])
		self.talking_unknown = UI.IntegerVar(0, [0,255])

		l = UI.LabelFrame(scrollview.content_view, text='Idle Portrait:')
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='SMK Dir:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.idle_entry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.idle_dd_view = UI.DropDown(f, self.idle_dd, [], self.idle_entry, width=30)
		self.idle_dd_view.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.tip(f, 'SMK Dir', 'PortFile')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=(5,0))
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='SMK Change:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.idle_change, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		self.tip(f, 'SMK Change', 'PortSMKChange')
		f.pack(side=UI.LEFT)
		f = UI.Frame(s)
		UI.Label(f, text='Unknown:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.idle_unknown, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		self.tip(f, 'Unknown', 'PortUnk1')
		f.pack(side=UI.RIGHT)
		s.pack(fill=UI.BOTH, padx=5, pady=(0,5))
		l.pack(fill=UI.X)

		l = UI.LabelFrame(scrollview.content_view, text='Talking Portrait:')
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='SMK Dir:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.talking_entry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.talking_dd_view = UI.DropDown(f, self.talking_dd, [], self.talking_entry, width=30)
		self.talking_dd_view.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.tip(f, 'SMK Dir', 'PortFile')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=(5,0))
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='SMK Change:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.talking_change, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		self.tip(f, 'SMK Change', 'PortSMKChange')
		f.pack(side=UI.LEFT)
		f = UI.Frame(s)
		UI.Label(f, text='Unknown:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.talking_unknown, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		self.tip(f, 'Unknown', 'PortUnk1')
		f.pack(side=UI.RIGHT)
		s.pack(fill=UI.BOTH, padx=5, pady=(0,5))
		l.pack(fill=UI.X, pady=5)

		scrollview.pack(fill=UI.BOTH, expand=1)

		self.setup_used_by((
			DATRefs(DATID.units, lambda unit: (
				DATRef('Portrait', cast(DATUnit, unit).portrait, dat_sub_tab=UnitsTabID.graphics),
			)),
		))

	def updated_pointer_entries(self, ids: list[AnyID]) -> None:
		if DataID.portdatatbl in ids:
			portdata = ('None',) + self.delegate.data_context.portdatatbl.strings
			limit = len(self.delegate.data_context.portdatatbl.strings)
			self.idle_dd_view.setentries(portdata)
			self.idle_entry.range[1] = limit
			self.talking_dd_view.setentries(portdata)
			self.talking_entry.range[1] = limit

		if DATID.units in ids and self.delegate.active_tab() == self:
			self.check_used_by_references()

	def load_entry(self, entry: DATPortraits) -> None:
		self.idle_entry.set(entry.idle.portrait_file)
		self.idle_change.set(entry.idle.smk_change)
		self.idle_unknown.set(entry.idle.unknown)
		self.talking_entry.set(entry.talking.portrait_file)
		self.talking_change.set(entry.talking.smk_change)
		self.talking_unknown.set(entry.talking.unknown)

	def save_entry(self, entry: DATPortraits) -> None:
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
