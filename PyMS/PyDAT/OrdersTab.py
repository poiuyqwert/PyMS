
from DATTab import DATTab
from DataID import DATID, DataID, UnitsTabID
from DATRef import DATRefs, DATRef

from ..FileFormats.TBL import decompile_string
from ..FileFormats.GRP import frame_to_photo

from ..Utilities.utils import couriernew
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.DataCache import DATA_CACHE

from Tkinter import *

class OrdersTab(DATTab):
	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		self.targetingentry = IntegerVar(0,[0,130])
		self.targeting = IntVar()
		self.energyentry = IntegerVar(0,[0,44])
		self.energy = IntVar()
		self.obscuredentry = IntegerVar(0,[0,189])
		self.obscured = IntVar()
		self.labelentry = IntegerVar(0,[0,0])
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
		self.targeting_ddw = DropDown(f, self.targeting, [], self.targetingentry, width=25)
		self.targeting_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda: self.jump(DATID.weapons, self.targeting.get())).pack(side=LEFT, padx=2)
		self.tip(f, 'Targeting', 'OrdTargeting')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Energy:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.energyentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.energy_ddw = DropDown(f, self.energy, [], self.energyentry, width=25)
		self.energy_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda: self.jump(DATID.techdata, self.energy.get())).pack(side=LEFT, padx=2)
		self.tip(f, 'Energy', 'OrdEnergy')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Obscured:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.obscuredentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.obscured_ddw = DropDown(f, self.obscured, [], self.obscuredentry, width=25)
		self.obscured_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda: self.jump(DATID.orders, self.obscured.get())).pack(side=LEFT, padx=2)
		self.tip(f, 'Obscured', 'OrdObscured')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Label:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.labelentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.labels = DropDown(f, self.label, [], self.labelentry, width=25)
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
		self.highlight_ddw = DropDown(f, self.highlightdd, [], self.highlightentry, width=25, none_value=65535)
		self.highlight_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
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

		self.setup_used_by((
			DATRefs(DATID.units, lambda unit: (
				DATRef('Computer Idle', unit.comp_ai_idle, dat_sub_tab=UnitsTabID.ai_actions),
				DATRef('Human Idle', unit.human_ai_idle, dat_sub_tab=UnitsTabID.ai_actions),
				DATRef('Return to Idle', unit.return_to_idle, dat_sub_tab=UnitsTabID.ai_actions),
				DATRef('Attach Unit', unit.attack_unit, dat_sub_tab=UnitsTabID.ai_actions),
				DATRef('Attack Move', unit.attack_move, dat_sub_tab=UnitsTabID.ai_actions)
			)),
		))

		self.highlightentry.trace('w', lambda *_: self.drawpreview())

	def get_dat_data(self):
		return self.toplevel.data_context.orders

	def updated_data_files(self, dataids):
		if DataID.stat_txt in dataids:
			self.labels.setentries(('None',) + self.toplevel.data_context.stat_txt.strings)
			self.labelentry.range[1] = len(self.toplevel.data_context.stat_txt.strings)
		if DataID.cmdicons in dataids:
			self.highlight_ddw.setentries(self.toplevel.data_context.cmdicons.names + ('None',))
			# TODO: Limit-1 while supporting none_value
			# self.highlightentry.range[1] = self.toplevel.data_context.cmdicons.frame_count()

	def updated_entry_names(self, datids):
		if DATID.units in datids and self.toplevel.dattabs.active == self:
			self.check_used_by_references()
		if DATID.weapons in datids:
			self.targeting_ddw.setentries(self.toplevel.data_context.weapons.names + ('None',))
		if DATID.techdata in datids:
			self.energy_ddw.setentries(self.toplevel.data_context.technology.names + ('None',))
		if DATID.orders in datids:
			self.obscured_ddw.setentries(self.toplevel.data_context.orders.names + ('None',))

	def updated_entry_counts(self, datids):
		if self.toplevel.data_context.settings.settings.get('reference_limits', True):
			if DATID.weapons in datids:
				self.targetingentry.range[1] = self.toplevel.data_context.weapons.entry_count()
			if DATID.techdata in datids:
				self.energyentry.range[1] = self.toplevel.data_context.technology.entry_count()
			if DATID.orders in datids:
				self.obscuredentry.range[1] = self.toplevel.data_context.orders.entry_count()
		else:
			self.targetingentry.range[1] = None
			self.energyentry.range[1] = None
			self.obscuredentry.range[1] = None

	def drawpreview(self):
		self.preview.delete(ALL)
		index = self.highlightentry.get()
		image = self.toplevel.data_context.get_cmdicon(index)
		if image:
			self.preview.create_image(19-image[1]/2+(image[0].width()-image[2])/2, 19-image[3]/2+(image[0].height()-image[4])/2, image=image[0])

	def load_entry(self, entry):
		self.label.set(entry.label)
		self.weapontargeting.set(entry.use_weapon_targeting)
		self.unknown2.set(entry.unused_is_secondary)
		self.unknown3.set(entry.unused_allow_non_subunits)
		self.unknown4.set(entry.changes_subunit_order)
		self.unknown5.set(entry.unused_allow_subunits)
		self.interruptable.set(entry.interruptable)
		self.unknown7.set(entry.waypoint_step_slowdown)
		self.queueable.set(entry.queueable)
		self.unknown9.set(entry.disabled_maintain_air_target)
		self.unknown10.set(entry.obstructable)
		self.unknown11.set(entry.flee_unreturnable_damage)
		self.unknown12.set(entry.unused_requires_movable_unit)
		self.targeting.set(entry.weapon_targeting)
		self.energy.set(entry.technology_energy)
		self.animation.set(entry.iscript_animation)
		self.highlightentry.set(entry.highlight_icon)
		self.unknown.set(entry.unknown17)
		self.obscured.set(entry.obscured_order)
		
		self.drawpreview()

	def save_entry(self, entry):
		if self.label.get() != entry.label:
			entry.label = self.label.get()
			self.edited = True
		if self.weapontargeting.get() != entry.use_weapon_targeting:
			entry.use_weapon_targeting = self.weapontargeting.get()
			self.edited = True
		if self.unknown2.get() != entry.unused_is_secondary:
			entry.unused_is_secondary = self.unknown2.get()
			self.edited = True
		if self.unknown3.get() != entry.unused_allow_non_subunits:
			entry.unused_allow_non_subunits = self.unknown3.get()
			self.edited = True
		if self.unknown4.get() != entry.changes_subunit_order:
			entry.changes_subunit_order = self.unknown4.get()
			self.edited = True
		if self.unknown5.get() != entry.unused_allow_subunits:
			entry.unused_allow_subunits = self.unknown5.get()
			self.edited = True
		if self.interruptable.get() != entry.interruptable:
			entry.interruptable = self.interruptable.get()
			self.edited = True
		if self.unknown7.get() != entry.waypoint_step_slowdown:
			entry.waypoint_step_slowdown = self.unknown7.get()
			self.edited = True
		if self.queueable.get() != entry.queueable:
			entry.queueable = self.queueable.get()
			self.edited = True
		if self.unknown9.get() != entry.disabled_maintain_air_target:
			entry.disabled_maintain_air_target = self.unknown9.get()
			self.edited = True
		if self.unknown10.get() != entry.obstructable:
			entry.obstructable = self.unknown10.get()
			self.edited = True
		if self.unknown11.get() != entry.flee_unreturnable_damage:
			entry.flee_unreturnable_damage = self.unknown11.get()
			self.edited = True
		if self.unknown12.get() != entry.unused_requires_movable_unit:
			entry.unused_requires_movable_unit = self.unknown12.get()
			self.edited = True
		if self.targeting.get() != entry.weapon_targeting:
			entry.weapon_targeting = self.targeting.get()
			self.edited = True
		if self.energy.get() != entry.technology_energy:
			entry.technology_energy = self.energy.get()
			self.edited = True
		if self.animation.get() != entry.iscript_animation:
			entry.iscript_animation = self.animation.get()
			self.edited = True
		if self.highlightentry.get() != entry.highlight_icon:
			entry.highlight_icon = self.highlightentry.get()
			self.edited = True
		if self.unknown.get() != entry.unknown17:
			entry.unknown17 = self.unknown.get()
			self.edited = True
		if self.obscured.get() != entry.obscured_order:
			entry.obscured_order = self.obscured.get()
			self.edited = True
