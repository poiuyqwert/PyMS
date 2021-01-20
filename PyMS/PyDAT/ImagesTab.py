
from DATTab import DATTab
from ..FileFormats.TBL import decompile_string

from ..Utilities.utils import couriernew
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.DataCache import DATA_CACHE

from Tkinter import *

class ImagesTab(DATTab):
	data = 'Images.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		grps = [] # ['None'] + [decompile_string(s) for s in self.toplevel.imagestbl.strings]
		self.grpentry = IntegerVar(0, [0, len(grps)-1])
		self.grpdd = IntVar()
		iscripts = DATA_CACHE['IscriptIDList.txt']
		self.iscriptentry = IntegerVar(0, [0, len(iscripts)-1])
		self.iscriptdd = IntVar()

		l = LabelFrame(frame, text='Image:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='GRP:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.grpentry, font=couriernew, width=3).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.grps = DropDown(f, self.grpdd, grps, self.grpentry, width=30)
		self.grpdds = [(self.grps,self.grpentry)]
		self.grps.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Check', command=lambda v=self.grpdd,c=[('images.dat',['GRPFile'])]: self.checkreference(v,c)).pack(side=LEFT, padx=2)
		self.tip(f, 'GRP File', 'ImgGRP')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Iscript ID:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.iscriptentry, font=couriernew, width=3).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.iscripts = DropDown(f, self.iscriptdd, iscripts, self.iscriptentry, width=30)
		self.iscripts.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Check', command=lambda v=self.iscriptdd,c=[('images.dat',['IscriptID'])]: self.checkreference(v,c)).pack(side=LEFT, padx=2)
		self.tip(f, 'Iscript ID', 'ImgIscriptID')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.graphicsturns = IntVar()
		self.drawifcloaked = IntVar()
		self.clickable = IntVar()
		self.usefulliscript = IntVar()

		p = Frame(frame)
		l = LabelFrame(p, text='General Properties:')
		s = Frame(l)
		ls = Frame(s)
		f = Frame(ls)
		Checkbutton(f, text='Graphics Turns', variable=self.graphicsturns).pack(side=LEFT)
		self.tip(f, 'Graphics Turns', 'ImgGfxTurns')
		f.pack(fill=X)
		f = Frame(ls)
		Checkbutton(f, text='Draw If Cloaked', variable=self.drawifcloaked).pack(side=LEFT)
		self.tip(f, 'Draw If Cloaked', 'ImgDrawCloaked')
		f.pack(fill=X)
		ls.pack(side=LEFT)
		ls = Frame(s)
		f = Frame(ls)
		Checkbutton(f, text='Clickable', variable=self.clickable).pack(side=LEFT)
		self.tip(f, 'Clickable', 'ImgClickable')
		f.pack(fill=X)
		f = Frame(ls)
		Checkbutton(f, text='Use Full Iscript', variable=self.usefulliscript).pack(side=LEFT)
		self.tip(f, 'Use Full Iscript', 'ImgUseFullIscript')
		f.pack(fill=X)
		ls.pack(side=LEFT)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X)

		self.functionentry = IntegerVar(0, [0,17])
		self.functiondd = IntVar()
		self.remapentry = IntegerVar(0, [0,9])
		self.remapdd = IntVar()

		l = LabelFrame(p, text='Drawing Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Function:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.functionentry, font=couriernew, width=2).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.functiondd, DATA_CACHE['DrawList.txt'], self.functionentry, width=15).pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Drawing Function', 'ImgDrawFunction')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Remapping:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.remapentry, font=couriernew, width=2).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.remapdd, DATA_CACHE['Remapping.txt'], self.remapentry, width=15).pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Remapping', 'ImgRemap')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X)
		p.pack(fill=X)

		self.attackentry = IntegerVar(0, [0, 929])
		self.attackdd = IntVar()
		self.damageentry = IntegerVar(0, [0, 929])
		self.damagedd = IntVar()
		self.specialentry = IntegerVar(0, [0, 929])
		self.specialdd = IntVar()
		self.landingentry = IntegerVar(0, [0, 929])
		self.landingdd = IntVar()
		self.liftoffentry = IntegerVar(0, [0, 929])
		self.liftoffdd = IntVar()
		self.shieldentry = IntegerVar(0, [0, 929])
		self.shielddd = IntVar()
		self.shieldsizes = IntVar()

		ols = [
			('Attack', self.attackentry, self.attackdd, 'OL1'),
			('Damage', self.damageentry, self.damagedd, 'OL2'),
			('Special', self.specialentry, self.specialdd, 'OL3'),
			('Landing Dust', self.landingentry, self.landingdd, 'OL4'),
			('Lift-Off Dust', self.liftoffentry, self.liftoffdd, 'OL5'),
			('Shield', self.shieldentry, self.shielddd, 'Shield'),
		]
		l = LabelFrame(frame, text='Extra Overlay Placements:')
		s = Frame(l)
		for t,e,d,h in ols:
			f = Frame(s)
			Label(f, text=t + ':', width=12, anchor=E).pack(side=LEFT)
			Entry(f, textvariable=e, font=couriernew, width=3).pack(side=LEFT, padx=2)
			Label(f, text='=').pack(side=LEFT)
			dd = DropDown(f, d, grps, e, width=15)
			dd.pack(side=LEFT, fill=X, expand=1, padx=2)
			self.grpdds.append((dd,e))
			self.tip(f, t + ' Overlay', 'Img' + h)
			f.pack(fill=X)
		f = Frame(s)
		Label(f, text='', width=12).pack(side=LEFT)
		self.sizedd = DropDown(f, self.shieldsizes, DATA_CACHE['ShieldSize.txt'], self.shieldupdate, width=6)
		self.sizedd.pack(side=LEFT, padx=2)
		self.tip(f, 'Shield Overlay', 'ImgShield')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('units.dat', ['ConstructionAnimation']),
			('sprites.dat', ['ImageFile']),
		]
		self.setuplistbox()

		self.values = {
			'GRPFile':self.grpentry,
			'GfxTurns':self.graphicsturns,
			'Clickable':self.clickable,
			'UseFullIscript':self.usefulliscript,
			'DrawIfCloaked':self.drawifcloaked,
			'DrawFunction':self.functionentry,
			'Remapping':self.remapentry,
			'IscriptID':self.iscriptentry,
			'ShieldOverlay':self.shieldentry,
			'AttackOverlay':self.attackentry,
			'DamageOverlay':self.damageentry,
			'SpecialOverlay':self.specialentry,
			'LandingDustOverlay':self.landingentry,
			'LiftOffDustOverlay':self.liftoffentry,
		}

	def files_updated(self):
		self.dat = self.toplevel.images
		entries = []
		last = -1
		for id in self.toplevel.iscriptbin.headers.keys():
			if id-last > 1:
				entries.extend(['*Unused*'] * (id-last-1))
			if id in self.toplevel.iscriptbin.extrainfo:
				n = self.toplevel.iscriptbin.extrainfo[id]
			elif id < len(DATA_CACHE['IscriptIDList.txt']):
				n = DATA_CACHE['IscriptIDList.txt'][id]
			else:
				n = 'Unnamed Custom Entry'
			entries.append(n)
			last = id
		self.iscripts.setentries(entries)
		self.iscriptentry.range[1] = len(entries)-1
		self.iscriptentry.editvalue()

		grps = ['None'] + [decompile_string(s) for s in self.toplevel.imagestbl.strings]
		for dd,entry_var in self.grpdds:
			dd.setentries(grps)
			entry_var.range[1] = len(grps)-1
			entry_var.editvalue()

	def shieldupdate(self, n):
		self.shieldentry.set([0,133,2,184][n])

	def load_data(self, id=None):
		DATTab.load_data(self, id)
		shield = self.shieldentry.get()
		sizes = [0,133,2,184]
		if shield in sizes:
			self.shieldsizes.set(sizes.index(shield))

	# def checkreferences(self, t, v):
		# self.listbox.delete(0,END)
		# val = v.get()
		# for id in range(self.dat.count):
			# if self.dat.get_value(id, ['GRPFile','IscriptID'][t]) == val:
				# self.listbox.insert(END, 'images.dat entry %s: %s' % (id,DATA_CACHE['Images.txt'][id]))
