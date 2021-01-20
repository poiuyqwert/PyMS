
from DATTab import DATTab
from ..FileFormats.TBL import decompile_string

from ..Utilities.utils import couriernew
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.DataCache import DATA_CACHE

from Tkinter import *

class OrdersTab(DATTab):
	data = 'Orders.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		stattxt = [] # ['None'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings]
		self.targetingentry = IntegerVar(0,[0,130])
		self.targeting = IntVar()
		self.energyentry = IntegerVar(0,[0,44])
		self.energy = IntVar()
		self.obscuredentry = IntegerVar(0,[0,189])
		self.obscured = IntVar()
		self.labelentry = IntegerVar(0,[0,len(stattxt)-1])
		self.label = IntVar()
		self.animationentry = IntegerVar(0,[0,28])
		self.animation = IntVar()
		self.highlightentry = IntegerVar(0, [0,65535])
		self.highlightdd = IntVar()
		self.unknown = IntegerVar(0, [0,65535])

		l = LabelFrame(frame, text='Order Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Targeting:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.targetingentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.targeting, DATA_CACHE['Weapons.txt'], self.targetingentry, width=25).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Weapons',i=self.targeting: self.jump(t,i)).pack(side=LEFT, padx=2)
		self.tip(f, 'Targeting', 'OrdTargeting')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Energy:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.energyentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.energy, DATA_CACHE['Techdata.txt'], self.energyentry, width=25).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Techdata',i=self.energy: self.jump(t,i)).pack(side=LEFT, padx=2)
		self.tip(f, 'Energy', 'OrdEnergy')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Obscured:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.obscuredentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.obscured, DATA_CACHE['Orders.txt'], self.obscuredentry, width=25).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Orders',i=self.obscured: self.jump(t,i)).pack(side=LEFT, padx=2)
		self.tip(f, 'Obscured', 'OrdObscured')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Label:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.labelentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.labels = DropDown(f, self.label, stattxt, self.labelentry, width=25)
		self.labels.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Label', 'OrdLabel')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Animation:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.animationentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.animation, DATA_CACHE['Animations.txt'], self.animationentry, width=25).pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Animation', 'OrdAnimation')
		f.pack(fill=X)
		m = Frame(s)
		ls = Frame(m)
		f = Frame(ls)
		Label(f, text='Highlight:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.highlightentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.highlightdd, DATA_CACHE['Icons.txt'] + ['None'], self.highlightentry, width=25, none_value=65535).pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Highlight', 'OrdHighlight')
		f.pack(fill=X)
		f = Frame(ls)
		Label(f, text='Unknown:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.unknown, font=couriernew, width=5).pack(side=LEFT, padx=2)
		self.tip(f, 'Unknown', 'OrdUnk13')
		f.pack(fill=X)
		ls.pack(side=LEFT, fill=X)
		ls = Frame(m, relief=SUNKEN, bd=1)
		self.preview = Canvas(ls, width=34, height=34, background='#000000')
		self.preview.pack()
		ls.pack(side=RIGHT)
		m.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.weapontargeting = IntVar()
		self.unknown2 = IntVar()
		self.unknown3 = IntVar()
		self.unknown4 = IntVar()
		self.unknown5 = IntVar()
		self.interruptable = IntVar()
		self.unknown7 = IntVar()
		self.queueable = IntVar()
		self.unknown9 = IntVar()
		self.unknown10 = IntVar()
		self.unknown11 = IntVar()
		self.unknown12 = IntVar()

		flags = [
			[
				('Use Weapon Targeting', self.weapontargeting, 'OrdWeapTarg'),
				('Secondary Order', self.unknown2, 'OrdUnk2'),
				('Unknown3', self.unknown3, 'OrdUnk3'),
				('Unknown4', self.unknown4, 'OrdUnk4'),
			],[
				('Unknown5', self.unknown5, 'OrdUnk5'),
				('Can be Interrupted', self.interruptable, 'OrdInterrupt'),
				('Unknown7', self.unknown7, 'OrdUnk7'),
				('Can be Queued', self.queueable, 'OrdQueue'),
			],[
				('Unknown9', self.unknown9, 'OrdUnk9'),
				('Unknown10', self.unknown10, 'OrdUnk10'),
				('Unknown11', self.unknown11, 'OrdUnk11'),
				('Unknown12', self.unknown12, 'OrdUnk12'),
			],
		]
		l = LabelFrame(frame, text='Flags:')
		s = Frame(l)
		for c in flags:
			cc = Frame(s, width=20)
			for t,v,h in c:
				f = Frame(cc)
				Checkbutton(f, text=t, variable=v).pack(side=LEFT)
				self.tip(f, t, h)
				f.pack(fill=X)
			cc.pack(side=LEFT, fill=Y)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('units.dat', ['CompAIIdle','HumanAIIdle','ReturntoIdle','AttackUnit','AttackMove']),
		]
		self.setuplistbox()

		self.values = {
			'Label':self.label,
			'UseWeaponTargeting':self.weapontargeting,
			'Unknown1':self.unknown2,
			'MainOrSecondary':self.unknown3,
			'Unknown3':self.unknown4,
			'Unknown4':self.unknown5,
			'Interruptable':self.interruptable,
			'Unknown5':self.unknown7,
			'Queueable':self.queueable,
			'Unknown6':self.unknown9,
			'Unknown7':self.unknown10,
			'Unknown8':self.unknown11,
			'Unknown9':self.unknown12,
			'Targeting':self.targeting,
			'Energy':self.energy,
			'Animation':self.animation,
			'Highlight':self.highlightentry,
			'Unknown10':self.unknown,
			'ObscuredOrder':self.obscured,
		}

		self.highlightentry.trace('w', lambda *_: self.drawpreview())

	def files_updated(self):
		self.dat = self.toplevel.orders
		stattxt = ['None'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings]
		self.labelentry.range[1] = len(stattxt)-1
		self.labels.setentries(stattxt)
		self.labelentry.editvalue()

	def drawpreview(self):
		self.preview.delete(ALL)
		if 'Icons' in PALETTES and self.toplevel.cmdicon:
			i = self.highlightentry.get()
			if i < self.toplevel.cmdicon.frames:
				if not i in ICON_CACHE:
					image = frame_to_photo(PALETTES['Icons'], self.toplevel.cmdicon, i, True)
					ICON_CACHE[i] = image
				else:
					image = ICON_CACHE[i]
				self.preview.create_image(19-image[1]/2+(image[0].width()-image[2])/2, 19-image[3]/2+(image[0].height()-image[4])/2, image=image[0])

	def load_data(self, id=None):
		DATTab.load_data(self, id)
		if 'Icons' in PALETTES and self.toplevel.cmdicon:
			self.drawpreview()
