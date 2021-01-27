
from DATTab import DATTab

from ..FileFormats.TBL import decompile_string
from ..FileFormats.GRP import frame_to_photo

from ..Utilities.utils import couriernew
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.FloatVar import FloatVar
from ..Utilities.DropDown import DropDown
from ..Utilities.DataCache import DATA_CACHE

from Tkinter import *

class UpgradesTab(DATTab):
	data = 'Upgrades.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		self.iconentry = IntegerVar(0, [0,389], callback=lambda n: self.selicon(n,1))
		self.icondd = IntVar()
		stattxt = [] 
		self.labelentry = IntegerVar(0,[0,len(stattxt)-1])
		self.labeldd = IntVar()
		self.item = None

		l = LabelFrame(frame, text='Upgrade Display:')
		s = Frame(l)
		ls = Frame(s)
		
		f = Frame(ls)
		Label(f, text='Icon:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.iconentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.icondd, DATA_CACHE['Icons.txt'], self.selicon, width=30).pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Upgrade Icon', 'UpgIcon')
		f.pack(fill=X)
		
		f = Frame(ls)
		Label(f, text='Label:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.labelentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.labels = DropDown(f, self.labeldd, stattxt, self.labelentry, width=30)
		self.labels.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Upgrade Label', 'UpgLabel')
		f.pack(fill=X)
		ls.pack(side=LEFT, fill=X)
		
		ls = Frame(s, relief=SUNKEN, bd=1)
		self.preview = Canvas(ls, width=34, height=34, background='#000000')
		self.preview.pack()
		ls.pack(side=RIGHT)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.baseminerals = IntegerVar(0, [0,65535])
		self.basevespene = IntegerVar(0, [0,65535])
		self.basetime = IntegerVar(24, [1,65535], callback=lambda n,b=0,i=0: self.updatetime(n,b,i))
		self.basesecs = FloatVar(1, [0.0416,2730.625], callback=lambda n,b=0,i=1: self.updatetime(n,b,i), precision=4)

		m = Frame(frame)
		l = LabelFrame(m, text='Base Cost:')
		s = Frame(l)
		
		f = Frame(s)
		Label(f, text='Minerals:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.baseminerals, font=couriernew, width=5).pack(side=LEFT)
		self.tip(f, 'Base Mineral Cost', 'UpgMinerals')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Vespene:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.basevespene, font=couriernew, width=5).pack(side=LEFT)
		self.tip(f, 'Base Vespene Cost', 'UpgVespene')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Time:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.basetime, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.basesecs, font=couriernew, width=9).pack(side=LEFT)
		Label(f, text='secs.').pack(side=LEFT)
		self.tip(f, 'Base Build Time', 'UpgTime')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X)

		self.factorminerals = IntegerVar(0, [0,65535])
		self.factorvespene = IntegerVar(0, [0,65535])
		self.factortime = IntegerVar(24, [1,65535], callback=lambda n,b=1,i=0: self.updatetime(n,b,i))
		self.factorsecs = FloatVar(1, [0.0416,2730.625], callback=lambda n,b=1,i=1: self.updatetime(n,b,i), precision=4)

		l = LabelFrame(m, text='Factor Cost:')
		s = Frame(l)
		
		f = Frame(s)
		Label(f, text='Minerals:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.factorminerals, font=couriernew, width=5).pack(side=LEFT)
		self.tip(f, 'Mineral Cost Factor', 'UpgFactorMinerals')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Vespene:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.factorvespene, font=couriernew, width=5).pack(side=LEFT)
		self.tip(f, 'Vespene Cost Factor', 'UpgFactorVespene')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Time:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.factortime, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.factorsecs, font=couriernew, width=9).pack(side=LEFT)
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

		m = Frame(frame)
		l = LabelFrame(m, text='Misc.:')
		s = Frame(l)
		
		f = Frame(s)
		Label(f, text='Max Repeats:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.maxrepeats, font=couriernew, width=3).pack(side=LEFT)
		self.tip(f, 'Max Repeats', 'UpgRepeats')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='ReqIndex:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.reqIndex, font=couriernew, width=5).pack(side=LEFT)
		self.tip(f, 'Requirements Index', 'UpgReq')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Race:', width=12, anchor=E).pack(side=LEFT)
		DropDown(f, self.race, DATA_CACHE['Races.txt'], width=10).pack(side=LEFT, fill=X, expand=1)
		self.tip(f, 'Race', 'UpgRace')
		f.pack(fill=X)
		
		self.makeCheckbox(s, self.broodwar, 'BroodWar', 'UpgIsBW').pack()
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT)
		m.pack(fill=X)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('units.dat', lambda entry: (entry.armor_upgrade, )),
			('weapons.dat', lambda entry: (entry.damage_upgrade, )),
		]
		self.setuplistbox()

	def files_updated(self):
		self.dat = self.toplevel.upgrades
		stattxt = ['None'] + [decompile_string(s) for s in self.toplevel.data_context.stat_txt.strings]
		self.labelentry.range[1] = len(stattxt)-1
		self.labels.setentries(stattxt)
		self.labelentry.editvalue()

	def selicon(self, n, t=0):
		if t:
			self.icondd.set(n)
		else:
			self.iconentry.set(n)
		self.drawpreview()

	def drawpreview(self):
		self.preview.delete(ALL)
		index = self.iconentry.get()
		image = self.toplevel.data_context.get_cmdicon(index)
		if image:
			self.preview.create_image(19-image[1]/2+(image[0].width()-image[2])/2, 19-image[3]/2+(image[0].height()-image[4])/2, image=image[0])

	def updatetime(self, num, factor, type):
		if type:
			x = [self.basetime,self.factortime][factor]
			x.check = False
			x.set(int(float(num) * 24))
		else:
			x = [self.basesecs,self.factorsecs][factor]
			x.check = False
			s = str(int(num) / 24.0)
			if s.endswith('.0'):
				s = s[:-2]
			elif len(s.split('.')[1]) > 4:
				s = s[:s.index('.')+5]
			x.set(s)

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
		if self.race.get() != entry.staredit_race:
			entry.staredit_race = self.race.get()
			self.edited = True
		if self.maxrepeats.get() != entry.max_repeats:
			entry.max_repeats = self.maxrepeats.get()
			self.edited = True
		if self.broodwar.get() != entry.broodwar_only:
			entry.broodwar_only = self.broodwar.get()
			self.edited = True
