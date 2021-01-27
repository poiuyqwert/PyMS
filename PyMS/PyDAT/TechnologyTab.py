
from DATTab import DATTab

from ..FileFormats.TBL import decompile_string
from ..FileFormats.GRP import frame_to_photo

from ..Utilities.utils import couriernew
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.FloatVar import FloatVar
from ..Utilities.DropDown import DropDown
from ..Utilities.DataCache import DATA_CACHE

from Tkinter import *

class TechnologyTab(DATTab):
	data = 'Techdata.txt'

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

		l = LabelFrame(frame, text='Technology Display:')
		s = Frame(l)
		ls = Frame(s)
		f = Frame(ls)
		Label(f, text='Icon:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.iconentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.icondd, DATA_CACHE['Icons.txt'], self.selicon, width=30).pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Technology Icon', 'TechIcon')
		f.pack(fill=X)
		f = Frame(ls)
		Label(f, text='Label:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.labelentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.labels = DropDown(f, self.labeldd, stattxt, self.labelentry, width=30)
		self.labels.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Technology Label', 'TechLabel')
		f.pack(fill=X)
		ls.pack(side=LEFT, fill=X)
		ls = Frame(s, relief=SUNKEN, bd=1)
		self.preview = Canvas(ls, width=34, height=34, background='#000000')
		self.preview.pack()
		ls.pack(side=RIGHT)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.minerals = IntegerVar(0, [0,65535])
		self.vespene = IntegerVar(0, [0,65535])
		self.time = IntegerVar(24, [1,65535], callback=lambda n,i=0: self.updatetime(n,i))
		self.secs = FloatVar(1, [0.0416,2730.625], callback=lambda n,i=1: self.updatetime(n,i), precision=4)
		self.energy = IntegerVar(0, [0,65535])

		m = Frame(frame)
		l = LabelFrame(m, text='Technology Cost:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Minerals:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.minerals, font=couriernew, width=5).pack(side=LEFT)
		self.tip(f, 'Mineral Cost', 'TechMinerals')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Vespene:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.vespene, font=couriernew, width=5).pack(side=LEFT)
		self.tip(f, 'Vespene Cost', 'TechVespene')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Time:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.time, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.secs, font=couriernew, width=9).pack(side=LEFT)
		Label(f, text='secs.').pack(side=LEFT)
		self.tip(f, 'Build Time', 'TechTime')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Energy:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.energy, font=couriernew, width=5).pack(side=LEFT)
		self.tip(f, 'Energy Cost', 'TechVespene')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X)

		self.researchReq = IntegerVar(0, [0,65535])
		self.useReq = IntegerVar(0, [0,65535])
		self.race = IntVar()
		self.unused = IntVar()
		self.broodwar = IntVar()

		l = LabelFrame(m, text='Technology Properties:')
		s = Frame(l)
		f = Frame(s)
		
		Label(f, text='ResearchReq:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.researchReq, font=couriernew, width=10).pack(side=LEFT)
		self.tip(f, 'Research Requirements', 'TechReq')
		f.pack(fill=X)
		f = Frame(s)

		Label(f, text='UseReq:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.useReq, font=couriernew, width=10).pack(side=LEFT)
		self.tip(f, 'Usage Requirements', 'TechUseReq')
		f.pack(fill=X)
		f = Frame(s)

		Label(f, text='Race:', width=12, anchor=E).pack(side=LEFT)
		DropDown(f, self.race, DATA_CACHE['Races.txt'], width=10).pack(side=LEFT, fill=X, expand=1)
		self.tip(f, 'Race', 'TechRace')
		f.pack(fill=X)
		f = Frame(s)
		
		self.makeCheckbox(f, self.unused, 'Researched', 'TechUnused').pack(side=LEFT)
		self.makeCheckbox(f, self.broodwar, 'BroodWar', 'TechBW').pack(side=LEFT)

		f.pack()
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=Y)
		m.pack(fill=X)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('orders.dat', lambda entry: (entry.technology_energy, )),
			('weapons.dat', lambda entry: (entry.unused_technology, )),
		]
		self.setuplistbox()

	def files_updated(self):
		self.dat = self.toplevel.technology
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

	def updatetime(self, num, type):
		if type:
			self.time.check = False
			self.time.set(int(float(num) * 24))
		else:
			self.secs.check = False
			s = str(int(num) / 24.0)
			if s.endswith('.0'):
				s = s[:-2]
			elif len(s.split('.')[1]) > 4:
				s = s[:s.index('.')+5]
			self.secs.set(s)

	def load_entry(self, entry):
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

	def save_entry(self, entry):
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
		if self.race.get() != entry.staredit_race:
			entry.staredit_race = self.race.get()
			self.edited = True
		if self.unused.get() != entry.researched:
			entry.researched = self.unused.get()
			self.edited = True
		if self.broodwar.get() != entry.broodwar_only:
			entry.broodwar_only = self.broodwar.get()
			self.edited = True