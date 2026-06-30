
from __future__ import annotations

from .DATTab import DATTab
from ..DataID import DATID, DataID, UnitsTabID, AnyID
from ..DATRef import DATRefs, DATRef
from ..IconSelectDialog import IconSelectDialog

from ...FileFormats.DAT import DATUnit, DATWeapon, DATUpgrade

from ...Utilities import UIKit as UI
from ...Utilities import Assets

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

class UpgradesTab(DATTab):
	DAT_ID = DATID.upgrades

	def __init__(self, parent: UI.Misc, delegate: MainDelegate) -> None:
		DATTab.__init__(self, parent, delegate)
		scrollview = UI.ScrollView(self)

		self.iconentry = UI.IntegerVar(0, [0,389], callback=lambda n: self.selicon(n,1))
		self.icondd = UI.IntVar()

		self.labelentry = UI.IntegerVar(0,[0,0])
		self.labeldd = UI.IntVar()
		self.item = None

		l = UI.LabelFrame(scrollview.content_view, text='Upgrade Display:')
		s = UI.Frame(l)
		ls = UI.Frame(s)

		f = UI.Frame(ls)
		UI.Label(f, text='Icon:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.iconentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.icon_ddw = UI.DropDown(f, self.icondd, [], self.selicon, width=30)
		self.icon_ddw.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.tip(f, 'Upgrade Icon', 'UpgIcon')
		UI.Button(f, image=Assets.get_image('find'), command=self.choose_icon, width=20, height=20).pack(side=UI.LEFT, padx=2)
		f.pack(fill=UI.X)

		f = UI.Frame(ls)
		UI.Label(f, text='Label:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.labelentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.labels = UI.DropDown(f, self.labeldd, [], self.labelentry, width=30)
		self.labels.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.tip(f, 'Upgrade Label', 'UpgLabel')
		f.pack(fill=UI.X)
		ls.pack(side=UI.LEFT, fill=UI.X)

		ls = UI.Frame(s, relief=UI.SUNKEN, bd=1)
		self.preview = UI.Canvas(ls, width=34, height=34, background='#000000', theme_tag='preview') # type: ignore[call-arg]
		self.preview.pack()
		self.preview.bind(UI.Mouse.Click_Left(), lambda *_: self.choose_icon())
		ls.pack(side=UI.RIGHT)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(fill=UI.X)

		self.baseminerals = UI.IntegerVar(0, [0,65535])
		self.basevespene = UI.IntegerVar(0, [0,65535])
		self.basetime = UI.IntegerVar(24, [0,65535])
		self.basesecs = UI.FloatVar(1, [0,65535/24.0], callback=lambda time: self.update_ticks(time, self.basetime), precision=4)
		self.basetime.callback = lambda ticks: self.update_time(ticks, self.basesecs)

		m = UI.Frame(scrollview.content_view)
		l = UI.LabelFrame(m, text='Base Cost:')
		s = UI.Frame(l)

		f = UI.Frame(s)
		UI.Label(f, text='Minerals:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.baseminerals, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Base Mineral Cost', 'UpgMinerals')
		f.pack(fill=UI.X)

		f = UI.Frame(s)
		UI.Label(f, text='Vespene:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.basevespene, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Base Vespene Cost', 'UpgVespene')
		f.pack(fill=UI.X)

		f = UI.Frame(s)
		UI.Label(f, text='Time:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.basetime, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.basesecs, font=UI.Font.fixed(), width=9).pack(side=UI.LEFT)
		UI.Label(f, text='secs.').pack(side=UI.LEFT)
		self.tip(f, 'Base Build Time', 'UpgTime')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(side=UI.LEFT, fill=UI.X)

		self.factorminerals = UI.IntegerVar(0, [0,65535])
		self.factorvespene = UI.IntegerVar(0, [0,65535])
		self.factortime = UI.IntegerVar(24, [0,65535])
		self.factorsecs = UI.FloatVar(1, [0,65535/24.0], callback=lambda time: self.update_ticks(time, self.factortime), precision=4)
		self.factortime.callback = lambda ticks: self.update_time(ticks, self.factorsecs)

		l = UI.LabelFrame(m, text='Factor Cost:')
		s = UI.Frame(l)

		f = UI.Frame(s)
		UI.Label(f, text='Minerals:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.factorminerals, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Mineral Cost Factor', 'UpgFactorMinerals')
		f.pack(fill=UI.X)

		f = UI.Frame(s)
		UI.Label(f, text='Vespene:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.factorvespene, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Vespene Cost Factor', 'UpgFactorVespene')
		f.pack(fill=UI.X)

		f = UI.Frame(s)
		UI.Label(f, text='Time:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.factortime, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.factorsecs, font=UI.Font.fixed(), width=9).pack(side=UI.LEFT)
		UI.Label(f, text='secs.').pack(side=UI.LEFT)
		self.tip(f, 'Build Time Factor', 'UpgFactorTime')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(side=UI.LEFT, fill=UI.X)
		m.pack(fill=UI.X)

		self.maxrepeats = UI.IntegerVar(0, [0,255])
		self.reqIndex = UI.IntegerVar(0, [0,65535])
		self.race = UI.IntVar()
		self.broodwar = UI.IntVar()

		m = UI.Frame(scrollview.content_view)
		l = UI.LabelFrame(m, text='Misc.:')
		s = UI.Frame(l)

		f = UI.Frame(s)
		UI.Label(f, text='Max Repeats:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.maxrepeats, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		self.tip(f, 'Max Repeats', 'UpgRepeats')
		f.pack(fill=UI.X)

		f = UI.Frame(s)
		UI.Label(f, text='ReqIndex:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.reqIndex, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Requirements Index', 'UpgReq')
		f.pack(fill=UI.X)

		f = UI.Frame(s)
		UI.Label(f, text='Race:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.DropDown(f, self.race, Assets.data_cache(Assets.DataReference.Races), width=10).pack(side=UI.LEFT, fill=UI.X, expand=1)
		self.tip(f, 'Race', 'UpgRace')
		f.pack(fill=UI.X)

		self.makeCheckbox(s, self.broodwar, 'BroodWar', 'UpgIsBW').pack()
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(side=UI.LEFT)
		m.pack(fill=UI.X)
		scrollview.pack(fill=UI.BOTH, expand=1)

		self.setup_used_by((
			DATRefs(DATID.units, lambda unit: (
				DATRef('Upgrade', cast(DATUnit, unit).armor_upgrade, dat_sub_tab=UnitsTabID.basic),
			)),
			DATRefs(DATID.weapons, lambda weapon: (
				DATRef('Upgrade', cast(DATWeapon, weapon).damage_upgrade),
			)),
		))

	def updated_pointer_entries(self, ids: list[AnyID]) -> None:
		if DataID.cmdicons in ids:
			self.icon_ddw.setentries(self.delegate.data_context.cmdicons.names)
		if DataID.stat_txt in ids:
			self.labels.setentries(('None',) + self.delegate.data_context.stat_txt.strings)
			self.labelentry.range[1] = len(self.delegate.data_context.stat_txt.strings)

		if (DATID.units in ids or DATID.weapons in ids) and self.delegate.active_tab() == self:
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

	def load_entry(self, entry: DATUpgrade) -> None:
		self.baseminerals.set(entry.mineral_cost_base)
		self.factorminerals.set(entry.mineral_cost_factor)
		self.basevespene.set(entry.vespene_cost_base)
		self.factorvespene.set(entry.vespene_cost_factor)
		self.basetime.set(entry.research_time_base)
		self.factortime.set(entry.research_time_factor)
		self.reqIndex.set(entry.requirements)
		self.iconentry.set(entry.icon)
		self.labelentry.set(entry.label)
		self.race.set(entry.staredit_race)
		self.maxrepeats.set(entry.max_repeats)
		self.broodwar.set(entry.broodwar_only)

		self.drawpreview()

	def save_entry(self, entry: DATUpgrade) -> None:
		if self.baseminerals.get() != entry.mineral_cost_base:
			entry.mineral_cost_base = self.baseminerals.get()
			self.edited = True
		if self.factorminerals.get() != entry.mineral_cost_factor:
			entry.mineral_cost_factor = self.factorminerals.get()
			self.edited = True
		if self.basevespene.get() != entry.vespene_cost_base:
			entry.vespene_cost_base = self.basevespene.get()
			self.edited = True
		if self.factorvespene.get() != entry.vespene_cost_factor:
			entry.vespene_cost_factor = self.factorvespene.get()
			self.edited = True
		if self.basetime.get() != entry.research_time_base:
			entry.research_time_base = self.basetime.get()
			self.edited = True
		if self.factortime.get() != entry.research_time_factor:
			entry.research_time_factor = self.factortime.get()
			self.edited = True
		if self.reqIndex.get() != entry.requirements:
			entry.requirements = self.reqIndex.get()
			self.edited = True
		if self.iconentry.get() != entry.icon:
			entry.icon = self.iconentry.get()
			self.edited = True
		if self.labelentry.get() != entry.label:
			entry.label = self.labelentry.get()
			self.edited = True
			if self.delegate.data_context.config.settings.labels.custom.value:
				self.delegate.data_context.dat_data(DATID.upgrades).update_names()
		if self.race.get() != entry.staredit_race:
			entry.staredit_race = self.race.get()
			self.edited = True
		if self.maxrepeats.get() != entry.max_repeats:
			entry.max_repeats = self.maxrepeats.get()
			self.edited = True
		if self.broodwar.get() != entry.broodwar_only:
			entry.broodwar_only = self.broodwar.get()
			self.edited = True
