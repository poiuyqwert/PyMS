
from __future__ import annotations

from .DATTab import DATTab
from ..DataID import DATID, DataID, AnyID

from ...FileFormats.DAT import DATMap

from ...Utilities.UIKit import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

class MapsTab(DATTab):
	DAT_ID = DATID.mapdata

	def __init__(self, parent, delegate): # type: (Misc, MainDelegate) -> None
		DATTab.__init__(self, parent, delegate)
		scrollview = ScrollView(self)

		self.missionentry = IntegerVar(0, [0,0])
		self.missiondd = IntVar()

		l = LabelFrame(scrollview.content_view, text='Campaign Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Mission Dir:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.missionentry, font=Font.fixed(), width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.missions = DropDown(f, self.missiondd, [], self.missionentry, width=30)
		self.missions.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Mission Dir', 'MapFile')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		scrollview.pack(fill=BOTH, expand=1)

	def updated_pointer_entries(self, ids): # type: (list[AnyID]) -> None
		if DataID.mapdatatbl in ids:
			self.missions.setentries(('None',) + self.delegate.data_context.mapdatatbl.strings)
			self.missionentry.range[1] = len(self.delegate.data_context.mapdatatbl.strings)

	def load_entry(self, entry): # type: (DATMap) -> None
		self.missionentry.set(entry.map_file)

	def save_entry(self, entry): # type: (DATMap) -> None
		if self.missionentry.get() != entry.map_file:
			entry.map_file = self.missionentry.get()
			self.edited = True
			if self.delegate.data_context.config.settings.labels.custom:
				self.delegate.data_context.dat_data(DATID.mapdata).update_names()
