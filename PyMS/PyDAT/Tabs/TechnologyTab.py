
from __future__ import annotations

from .DATTab import DATTab
from ..DataID import DATID, DataID, AnyID
from ..DATRef import DATRefs, DATRef
from ..IconSelectDialog import IconSelectDialog

from ...FileFormats.DAT import DATOrder, DATWeapon, DATTechnology

from ...Utilities import UIKit as UI
from ...Utilities import Assets

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

class TechnologyTab(DATTab):
	DAT_ID = DATID.techdata

	def __init__(self, parent: UI.Misc, delegate: MainDelegate) -> None:
		DATTab.__init__(self, parent, delegate)
		scrollview = UI.ScrollView(self)

		self.iconentry = UI.IntegerVar(0, [0,389], callback=lambda n: self.selicon(n,1))
		self.icondd = UI.IntVar()

		self.labelentry = UI.IntegerVar(0,[0,0])
		self.labeldd = UI.IntVar()

		self.item = None

		l = UI.LabelFrame(scrollview.content_view, text='Technology Display:')
		s = UI.Frame(l)
		ls = UI.Frame(s)
		f = UI.Frame(ls)
		UI.Label(f, text='Icon:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.iconentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.icon_ddw = UI.DropDown(f, self.icondd, [], self.selicon, width=30)
		self.icon_ddw.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.tip(f, 'Technology Icon', 'TechIcon')
		UI.Button(f, image=Assets.get_image('find'), command=self.choose_icon, width=20, height=20).pack(side=UI.LEFT, padx=2)
		f.pack(fill=UI.X)
		f = UI.Frame(ls)
		UI.Label(f, text='Label:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.labelentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.labels = UI.DropDown(f, self.labeldd, [], self.labelentry, width=30)
		self.labels.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.tip(f, 'Technology Label', 'TechLabel')
		f.pack(fill=UI.X)
		ls.pack(side=UI.LEFT, fill=UI.X)
		ls = UI.Frame(s, relief=UI.SUNKEN, bd=1)
		self.preview = UI.Canvas(ls, width=34, height=34, background='#000000', theme_tag='preview') # type: ignore[call-arg]
		self.preview.pack()
		self.preview.bind(UI.Mouse.Click_Left(), lambda *_: self.choose_icon())
		ls.pack(side=UI.RIGHT)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(fill=UI.X)

		self.minerals = UI.IntegerVar(0, [0,65535])
		self.vespene = UI.IntegerVar(0, [0,65535])
		self.time = UI.IntegerVar(24, [0,65535])
		self.secs = UI.FloatVar(1, [0,65535/24.0], callback=lambda time: self.update_ticks(time, self.time), precision=4)
		self.time.callback = lambda ticks: self.update_time(ticks, self.secs)
		self.energy = UI.IntegerVar(0, [0,65535])

		m = UI.Frame(scrollview.content_view)
		l = UI.LabelFrame(m, text='Technology Cost:')
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='Minerals:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.minerals, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Mineral Cost', 'TechMinerals')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Vespene:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.vespene, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Vespene Cost', 'TechVespene')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Time:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.time, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.secs, font=UI.Font.fixed(), width=9).pack(side=UI.LEFT)
		UI.Label(f, text='secs.').pack(side=UI.LEFT)
		self.tip(f, 'Build Time', 'TechTime')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Energy:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.energy, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Energy Cost', 'TechVespene')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(side=UI.LEFT, fill=UI.X)

		self.researchReq = UI.IntegerVar(0, [0,65535])
		self.useReq = UI.IntegerVar(0, [0,65535])
		self.race = UI.IntVar()
		self.unused = UI.IntVar()
		self.broodwar = UI.IntVar()

		l = UI.LabelFrame(m, text='Technology Properties:')
		s = UI.Frame(l)
		f = UI.Frame(s)

		UI.Label(f, text='ResearchReq:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.researchReq, font=UI.Font.fixed(), width=10).pack(side=UI.LEFT)
		self.tip(f, 'Research Requirements', 'TechReq')
		f.pack(fill=UI.X)
		f = UI.Frame(s)

		UI.Label(f, text='UseReq:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.useReq, font=UI.Font.fixed(), width=10).pack(side=UI.LEFT)
		self.tip(f, 'Usage Requirements', 'TechUseReq')
		f.pack(fill=UI.X)
		f = UI.Frame(s)

		UI.Label(f, text='Race:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.DropDown(f, self.race, Assets.data_cache(Assets.DataReference.Races), width=10).pack(side=UI.LEFT, fill=UI.X, expand=1)
		self.tip(f, 'Race', 'TechRace')
		f.pack(fill=UI.X)
		f = UI.Frame(s)

		self.makeCheckbox(f, self.unused, 'Researched', 'TechUnused').pack(side=UI.LEFT)
		self.makeCheckbox(f, self.broodwar, 'BroodWar', 'TechBW').pack(side=UI.LEFT)

		f.pack()
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(side=UI.LEFT, fill=UI.Y)
		m.pack(fill=UI.X)
		scrollview.pack(fill=UI.BOTH, expand=1)

		self.setup_used_by((
			DATRefs(DATID.orders, lambda order: (
				DATRef('Energy', cast(DATOrder, order).technology_energy),
			)),
			DATRefs(DATID.weapons, lambda weapons: (
				DATRef('Unused', cast(DATWeapon, weapons).unused_technology),
			)),
		))

	def updated_pointer_entries(self, ids: list[AnyID]) -> None:
		if DataID.cmdicons in ids:
			self.icon_ddw.setentries(self.delegate.data_context.cmdicons.names)
		if DataID.stat_txt in ids:
			self.labels.setentries(('None',) + self.delegate.data_context.stat_txt.strings)
			self.labelentry.range[1] = len(self.delegate.data_context.stat_txt.strings)

		if (DATID.orders in ids or DATID.weapons in ids) and self.delegate.active_tab() == self:
			self.check_used_by_references()

	def selicon(self, n: int, t: int = 0) -> None:
		if t:
			self.icondd.set(n)
		else:
			self.iconentry.set(n)
		self.drawpreview()

	def choose_icon(self) -> None:
		def update_icon(index: int) -> None:
			self.iconentry.set(index)
		IconSelectDialog(self, data_context=self.delegate.data_context, delegate=update_icon, selected_index=self.iconentry.get())

	def drawpreview(self) -> None:
		self.preview.delete(UI.ALL)
		index = self.iconentry.get()
		image = self.delegate.data_context.get_cmdicon(index)
		if image:
			self.preview.create_image(19-image[1]//2+(image[0].width()-image[2])//2, 19-image[3]//2+(image[0].height()-image[4])//2, image=image[0])

	def load_entry(self, entry: DATTechnology) -> None:
		self.minerals.set(entry.mineral_cost)
		self.vespene.set(entry.vespene_cost)
		self.time.set(entry.research_time)
		self.energy.set(entry.energy_required)
		self.researchReq.set(entry.research_requirements)
		self.useReq.set(entry.use_requirements)
		self.iconentry.set(entry.icon)
		self.labelentry.set(entry.label)
		self.race.set(entry.staredit_race)
		self.unused.set(entry.researched)
		self.broodwar.set(entry.broodwar_only)

		self.drawpreview()

	def save_entry(self, entry: DATTechnology) -> None:
		if self.minerals.get() != entry.mineral_cost:
			entry.mineral_cost = self.minerals.get()
			self.edited = True
		if self.vespene.get() != entry.vespene_cost:
			entry.vespene_cost = self.vespene.get()
			self.edited = True
		if self.time.get() != entry.research_time:
			entry.research_time = self.time.get()
			self.edited = True
		if self.energy.get() != entry.energy_required:
			entry.energy_required = self.energy.get()
			self.edited = True
		if self.researchReq.get() != entry.research_requirements:
			entry.research_requirements = self.researchReq.get()
			self.edited = True
		if self.useReq.get() != entry.use_requirements:
			entry.use_requirements = self.useReq.get()
			self.edited = True
		if self.iconentry.get() != entry.icon:
			entry.icon = self.iconentry.get()
			self.edited = True
		if self.labelentry.get() != entry.label:
			entry.label = self.labelentry.get()
			self.edited = True
			if self.delegate.data_context.config.settings.labels.custom:
				self.delegate.data_context.dat_data(DATID.techdata).update_names()
		if self.race.get() != entry.staredit_race:
			entry.staredit_race = self.race.get()
			self.edited = True
		if self.unused.get() != entry.researched:
			entry.researched = self.unused.get()
			self.edited = True
		if self.broodwar.get() != entry.broodwar_only:
			entry.broodwar_only = self.broodwar.get()
			self.edited = True
