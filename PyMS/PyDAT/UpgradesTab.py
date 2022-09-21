
from .DATTab import DATTab
from .DataID import DATID, DataID, UnitsTabID
from .DATRef import DATRefs, DATRef
from .IconSelectDialog import IconSelectDialog

from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.FloatVar import FloatVar
from ..Utilities.DropDown import DropDown
from ..Utilities.UIKit import *
from ..Utilities.ScrollView import ScrollView
from ..Utilities import Assets

class UpgradesTab(DATTab):
	DAT_ID = DATID.upgrades

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		scrollview = ScrollView(self)

		self.iconentry = IntegerVar(0, [0,389], callback=lambda n: self.selicon(n,1))
		self.icondd = IntVar()

		self.labelentry = IntegerVar(0,[0,0])
		self.labeldd = IntVar()
		self.item = None

		l = LabelFrame(scrollview.content_view, text='Upgrade Display:')
		s = Frame(l)
		ls = Frame(s)
		
		f = Frame(ls)
		Label(f, text='Icon:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.iconentry, font=Font.fixed(), width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.icon_ddw = DropDown(f, self.icondd, [], self.selicon, width=30)
		self.icon_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Upgrade Icon', 'UpgIcon')
		Button(f, image=Assets.get_image('find'), command=self.choose_icon, width=20, height=20).pack(side=LEFT, padx=2)
		f.pack(fill=X)
		
		f = Frame(ls)
		Label(f, text='Label:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.labelentry, font=Font.fixed(), width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.labels = DropDown(f, self.labeldd, [], self.labelentry, width=30)
		self.labels.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Upgrade Label', 'UpgLabel')
		f.pack(fill=X)
		ls.pack(side=LEFT, fill=X)
		
		ls = Frame(s, relief=SUNKEN, bd=1)
		self.preview = Canvas(ls, width=34, height=34, background='#000000')
		self.preview.pack()
		self.preview.bind(Mouse.Click_Left, lambda *_: self.choose_icon())
		ls.pack(side=RIGHT)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.baseminerals = IntegerVar(0, [0,65535])
		self.basevespene = IntegerVar(0, [0,65535])
		self.basetime = IntegerVar(24, [0,65535], callback=lambda ticks: self.update_time(ticks, self.basesecs))
		self.basesecs = FloatVar(1, [0,65535/24.0], callback=lambda time: self.update_ticks(time, self.basetime), precision=4)

		m = Frame(scrollview.content_view)
		l = LabelFrame(m, text='Base Cost:')
		s = Frame(l)
		
		f = Frame(s)
		Label(f, text='Minerals:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.baseminerals, font=Font.fixed(), width=5).pack(side=LEFT)
		self.tip(f, 'Base Mineral Cost', 'UpgMinerals')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Vespene:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.basevespene, font=Font.fixed(), width=5).pack(side=LEFT)
		self.tip(f, 'Base Vespene Cost', 'UpgVespene')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Time:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.basetime, font=Font.fixed(), width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.basesecs, font=Font.fixed(), width=9).pack(side=LEFT)
		Label(f, text='secs.').pack(side=LEFT)
		self.tip(f, 'Base Build Time', 'UpgTime')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X)

		self.factorminerals = IntegerVar(0, [0,65535])
		self.factorvespene = IntegerVar(0, [0,65535])
		self.factortime = IntegerVar(24, [0,65535], callback=lambda ticks: self.update_time(ticks, self.factorsecs))
		self.factorsecs = FloatVar(1, [0,65535/24.0], callback=lambda time: self.update_ticks(time, self.factortime), precision=4)

		l = LabelFrame(m, text='Factor Cost:')
		s = Frame(l)
		
		f = Frame(s)
		Label(f, text='Minerals:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.factorminerals, font=Font.fixed(), width=5).pack(side=LEFT)
		self.tip(f, 'Mineral Cost Factor', 'UpgFactorMinerals')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Vespene:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.factorvespene, font=Font.fixed(), width=5).pack(side=LEFT)
		self.tip(f, 'Vespene Cost Factor', 'UpgFactorVespene')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Time:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.factortime, font=Font.fixed(), width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.factorsecs, font=Font.fixed(), width=9).pack(side=LEFT)
		Label(f, text='secs.').pack(side=LEFT)
		self.tip(f, 'Build Time Factor', 'UpgFactorTime')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X)
		m.pack(fill=X)

		self.maxrepeats = IntegerVar(0, [0,255])
		self.reqIndex = IntegerVar(0, [0,65535])
		self.race = IntVar()
		self.broodwar = IntVar()

		m = Frame(scrollview.content_view)
		l = LabelFrame(m, text='Misc.:')
		s = Frame(l)
		
		f = Frame(s)
		Label(f, text='Max Repeats:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.maxrepeats, font=Font.fixed(), width=3).pack(side=LEFT)
		self.tip(f, 'Max Repeats', 'UpgRepeats')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='ReqIndex:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.reqIndex, font=Font.fixed(), width=5).pack(side=LEFT)
		self.tip(f, 'Requirements Index', 'UpgReq')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Race:', width=12, anchor=E).pack(side=LEFT)
		DropDown(f, self.race, Assets.data_cache(Assets.DataReference.Races), width=10).pack(side=LEFT, fill=X, expand=1)
		self.tip(f, 'Race', 'UpgRace')
		f.pack(fill=X)
		
		self.makeCheckbox(s, self.broodwar, 'BroodWar', 'UpgIsBW').pack()
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT)
		m.pack(fill=X)
		scrollview.pack(fill=BOTH, expand=1)

		self.setup_used_by((
			DATRefs(DATID.units, lambda unit: (
				DATRef('Upgrade', unit.armor_upgrade, dat_sub_tab=UnitsTabID.basic),
			)),
			DATRefs(DATID.weapons, lambda weapon: (
				DATRef('Upgrade', weapon.damage_upgrade),
			)),
		))

	def updated_pointer_entries(self, ids):
		if DataID.cmdicons in ids:
			self.icon_ddw.setentries(self.toplevel.data_context.cmdicons.names)
		if DataID.stat_txt in ids:
			self.labels.setentries(('None',) + self.toplevel.data_context.stat_txt.strings)
			self.labelentry.range[1] = len(self.toplevel.data_context.stat_txt.strings)

		if (DATID.units in ids or DATID.weapons in ids) and self.toplevel.dattabs.active == self:
			self.check_used_by_references()

	def selicon(self, n, t=0):
		if t:
			self.icondd.set(n)
		else:
			self.iconentry.set(n)
		self.drawpreview()

	def choose_icon(self):
		def update_icon(index):
			self.iconentry.set(index)
		IconSelectDialog(self, self.toplevel.data_context, update_icon, self.iconentry.get())

	def drawpreview(self):
		self.preview.delete(ALL)
		index = self.iconentry.get()
		image = self.toplevel.data_context.get_cmdicon(index)
		if image:
			self.preview.create_image(19-image[1]/2+(image[0].width()-image[2])/2, 19-image[3]/2+(image[0].height()-image[4])/2, image=image[0])

	def load_entry(self, entry):
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

	def save_entry(self, entry):
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
			if self.toplevel.data_context.settings.settings.get('customlabels'):
				self.toplevel.data_context.dat_data(DATID.upgrades).update_names()
		if self.race.get() != entry.staredit_race:
			entry.staredit_race = self.race.get()
			self.edited = True
		if self.maxrepeats.get() != entry.max_repeats:
			entry.max_repeats = self.maxrepeats.get()
			self.edited = True
		if self.broodwar.get() != entry.broodwar_only:
			entry.broodwar_only = self.broodwar.get()
			self.edited = True
