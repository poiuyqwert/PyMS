
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

		grps = []
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
		# TODO: Update check_used_by_references
		Button(f, text='Check', command=lambda v=self.grpdd,c=[('images.dat',['GRPFile'])]: self.check_used_by_references(v.get(),c)).pack(side=LEFT, padx=2)
		self.tip(f, 'GRP File', 'ImgGRP')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Iscript ID:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.iscriptentry, font=couriernew, width=3).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.iscripts = DropDown(f, self.iscriptdd, iscripts, self.iscriptentry, width=30)
		self.iscripts.pack(side=LEFT, fill=X, expand=1, padx=2)
		# TODO: Update check_used_by_references
		Button(f, text='Check', command=lambda v=self.iscriptdd,c=[('images.dat',['IscriptID'])]: self.check_used_by_references(v.get(),c)).pack(side=LEFT, padx=2)
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

		self.setup_used_by_listbox()

	def get_dat_data(self):
		return self.toplevel.data_context.images

	def get_used_by_references(self):
		return [
			(self.toplevel.data_context.units.dat, lambda unit: (unit.construction_animation, )),
			(self.toplevel.data_context.sprites.dat, lambda sprite: (sprite.image_file, )),
		]

	def files_updated(self):
		entries = []
		last = -1
		for id in self.toplevel.data_context.iscriptbin.headers.keys():
			if id-last > 1:
				entries.extend(['*Unused*'] * (id-last-1))
			if id in self.toplevel.data_context.iscriptbin.extrainfo:
				n = self.toplevel.data_context.iscriptbin.extrainfo[id]
			elif id < len(DATA_CACHE['IscriptIDList.txt']):
				n = DATA_CACHE['IscriptIDList.txt'][id]
			else:
				n = 'Unnamed Custom Entry'
			entries.append(n)
			last = id
		self.iscripts.setentries(entries)
		self.iscriptentry.range[1] = len(entries)-1
		self.iscriptentry.editvalue()

		grps = ['None'] + [decompile_string(s) for s in self.toplevel.data_context.imagestbl.strings]
		for dd,entry_var in self.grpdds:
			dd.setentries(grps)
			entry_var.range[1] = len(grps)-1
			entry_var.editvalue()

	def shieldupdate(self, n):
		self.shieldentry.set([0,133,2,184][n])

	def load_entry(self, entry):
		self.grpentry.set(entry.grp_file)
		self.graphicsturns.set(entry.gfx_turns)
		self.clickable.set(entry.clickable)
		self.usefulliscript.set(entry.use_full_iscript)
		self.drawifcloaked.set(entry.draw_if_cloaked)
		self.functionentry.set(entry.draw_function)
		self.remapentry.set(entry.remapping)
		self.iscriptentry.set(entry.iscript_id)
		self.shieldentry.set(entry.shield_overlay)
		self.attackentry.set(entry.attack_overlay)
		self.damageentry.set(entry.damage_overlay)
		self.specialentry.set(entry.special_overlay)
		self.landingentry.set(entry.landing_dust_overlay)
		self.liftoffentry.set(entry.lift_off_dust_overlay)

		default_shield_overlays = (0, 133, 2, 184)
		if entry.shield_overlay in default_shield_overlays:
			self.shieldsizes.set(default_shield_overlays.index(entry.shield_overlay))

	def save_entry(self, entry):
		if self.grpentry.get() != entry.grp_file:
			entry.grp_file = self.grpentry.get()
			self.edited = True
		if self.graphicsturns.get() != entry.gfx_turns:
			entry.gfx_turns = self.graphicsturns.get()
			self.edited = True
		if self.clickable.get() != entry.clickable:
			entry.clickable = self.clickable.get()
			self.edited = True
		if self.usefulliscript.get() != entry.use_full_iscript:
			entry.use_full_iscript = self.usefulliscript.get()
			self.edited = True
		if self.drawifcloaked.get() != entry.draw_if_cloaked:
			entry.draw_if_cloaked = self.drawifcloaked.get()
			self.edited = True
		if self.functionentry.get() != entry.draw_function:
			entry.draw_function = self.functionentry.get()
			self.edited = True
		if self.remapentry.get() != entry.remapping:
			entry.remapping = self.remapentry.get()
			self.edited = True
		if self.iscriptentry.get() != entry.iscript_id:
			entry.iscript_id = self.iscriptentry.get()
			self.edited = True
		if self.shieldentry.get() != entry.shield_overlay:
			entry.shield_overlay = self.shieldentry.get()
			self.edited = True
		if self.attackentry.get() != entry.attack_overlay:
			entry.attack_overlay = self.attackentry.get()
			self.edited = True
		if self.damageentry.get() != entry.damage_overlay:
			entry.damage_overlay = self.damageentry.get()
			self.edited = True
		if self.specialentry.get() != entry.special_overlay:
			entry.special_overlay = self.specialentry.get()
			self.edited = True
		if self.landingentry.get() != entry.landing_dust_overlay:
			entry.landing_dust_overlay = self.landingentry.get()
			self.edited = True
		if self.liftoffentry.get() != entry.lift_off_dust_overlay:
			entry.lift_off_dust_overlay = self.liftoffentry.get()
			self.edited = True
