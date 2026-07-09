
from __future__ import annotations

from .DATTab import DATTab
from ..DataID import DATID, DataID, AnyID

from ...FileFormats.DAT import DATMap

from ...Utilities import UIKit as UI

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

class MapsTab(DATTab):
	DAT_ID = DATID.mapdata

	def __init__(self, parent: UI.Misc, delegate: MainDelegate) -> None:
		DATTab.__init__(self, parent, delegate)
		scrollview = UI.ScrollView(self)

		self.missionentry = UI.IntegerVar(0, [0,0])
		self.missiondd = UI.IntVar()

		l = UI.LabelFrame(scrollview.content_view, text='Campaign Properties:')
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='Mission Dir:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.missionentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.missions = UI.DropDown(f, self.missiondd, [], self.missionentry, width=30)
		self.missions.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.tip(f, 'Mission Dir', 'MapFile')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(fill=UI.X)

		scrollview.pack(fill=UI.BOTH, expand=1)

	def updated_pointer_entries(self, ids: list[AnyID]) -> None:
		if DataID.mapdatatbl in ids:
			self.missions.setentries(('None',) + self.delegate.data_context.mapdatatbl.strings)
			self.missionentry.range[1] = len(self.delegate.data_context.mapdatatbl.strings)

	def load_entry(self, entry: DATMap) -> None:
		self.missionentry.set(entry.map_file)

	def save_entry(self, entry: DATMap) -> None:
		if self.missionentry.get() != entry.map_file:
			entry.map_file = self.missionentry.get()
			self.edited = True
			if self.delegate.data_context.config.settings.labels.custom.value:
				self.delegate.data_context.dat_data(DATID.mapdata).update_names()
