
from .DATTab import DATTab
from .DataID import DATID, DataID, UnitsTabID
from .DATRef import DATRefs, DATRef
from .IconSelectDialog import IconSelectDialog

from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.UIKit import *
from ..Utilities.ScrollView import ScrollView
from ..Utilities import Assets

class OrdersTab(DATTab):
	DAT_ID = DATID.orders

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		scrollview = ScrollView(self)

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
		self.requirements = IntegerVar(0, [0,65535])

		l = LabelFrame(scrollview.content_view, text='Order Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Targeting:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.targetingentry, font=Font.fixed(), width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.targeting_ddw = DropDown(f, self.targeting, [], self.targetingentry, width=25)
		self.targeting_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda: self.jump(DATID.weapons, self.targeting.get())).pack(side=LEFT, padx=2)
		self.tip(f, 'Targeting', 'OrdTargeting')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Energy:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.energyentry, font=Font.fixed(), width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.energy_ddw = DropDown(f, self.energy, [], self.energyentry, width=25)
		self.energy_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda: self.jump(DATID.techdata, self.energy.get())).pack(side=LEFT, padx=2)
		self.tip(f, 'Energy', 'OrdEnergy')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Obscured:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.obscuredentry, font=Font.fixed(), width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.obscured_ddw = DropDown(f, self.obscured, [], self.obscuredentry, width=25)
		self.obscured_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda: self.jump(DATID.orders, self.obscured.get())).pack(side=LEFT, padx=2)
		self.tip(f, 'Obscured', 'OrdObscured')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Label:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.labelentry, font=Font.fixed(), width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.labels = DropDown(f, self.label, [], self.labelentry, width=25)
		self.labels.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Label', 'OrdLabel')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Animation:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.animationentry, font=Font.fixed(), width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.animation, Assets.data_cache(Assets.DataReference.Animations), self.animationentry, width=25).pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Animation', 'OrdAnimation')
		f.pack(fill=X)
		m = Frame(s)
		ls = Frame(m)
		f = Frame(ls)
		Label(f, text='Highlight:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.highlightentry, font=Font.fixed(), width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.highlight_ddw = DropDown(f, self.highlightdd, [], self.highlightentry, width=25, none_value=65535)
		self.highlight_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Highlight', 'OrdHighlight')
		Button(f, image=Assets.get_image('find'), command=self.choose_icon, width=20, height=20).pack(side=LEFT, padx=2)
		f.pack(fill=X)
		f = Frame(ls)
		Label(f, text='ReqIndex:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.requirements, font=Font.fixed(), width=5).pack(side=LEFT, padx=2)
		self.tip(f, 'ReqIndex', 'OrdReq')
		f.pack(fill=X)
		ls.pack(side=LEFT, fill=X)
		ls = Frame(m, relief=SUNKEN, bd=1)
		self.preview = Canvas(ls, width=34, height=34, background='#000000')
		self.preview.pack()
		self.preview.bind(Mouse.Click_Left, lambda *_: self.choose_icon())
		ls.pack(side=RIGHT)
		m.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.weapontargeting = IntVar()
		self.is_secondary = IntVar()
		self.allow_non_subunits = IntVar()
		self.changes_subunit_order = IntVar()
		self.allow_subunits = IntVar()
		self.interruptable = IntVar()
		self.waypoints_slowdown = IntVar()
		self.queueable = IntVar()
		self.disabled_maintain_unit_target = IntVar()
		self.obstructable = IntVar()
		self.flee_unreturnable_damage = IntVar()
		self.requires_movable_unit = IntVar()

		flags = [
			[
				('Use Weapon Targeting', self.weapontargeting, 'OrdWeapTarg'),
				('Secondary Order (Unused)', self.is_secondary, 'OrdSecondaryOrder'),
				('Allow Non-Subunits (Unused)', self.allow_non_subunits, 'OrdAllowNonSubunits'),
				('Changes Subunit Order', self.changes_subunit_order, 'OrdChangesSubunitOrder'),
			],[
				('Allow Subunits (Unused)', self.allow_subunits, 'OrdAllowSubunits'),
				('Can be Interrupted', self.interruptable, 'OrdInterrupt'),
				('Waypoints Slowdown', self.waypoints_slowdown, 'OrdWaypointsSlowdown'),
				('Can be Queued', self.queueable, 'OrdQueue'),
			],[
				('Disabled Maintain Unit Target', self.disabled_maintain_unit_target, 'OrdDisabledMaintainUnitTarget'),
				('Obstructable', self.obstructable, 'OrdObstructable'),
				('Flee Unreturnable Damage', self.flee_unreturnable_damage, 'OrdFleeUnreturnableDamage'),
				('Requires Movable Unit (Unused)', self.requires_movable_unit, 'OrdRequiresMovableUnit'),
			],
		]
		l = LabelFrame(scrollview.content_view, text='Flags:')
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

		scrollview.pack(fill=BOTH, expand=1)

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

	def updated_pointer_entries(self, ids):
		if DataID.stat_txt in ids:
			self.labels.setentries(('None',) + self.toplevel.data_context.stat_txt.strings)
			self.labelentry.range[1] = len(self.toplevel.data_context.stat_txt.strings)
		if DataID.cmdicons in ids:
			self.highlight_ddw.setentries(self.toplevel.data_context.cmdicons.names + ('None',))
			# TODO: Limit-1 while supporting none_value
			# self.highlightentry.range[1] = self.toplevel.data_context.cmdicons.frame_count()

		if DATID.units in ids and self.toplevel.dattabs.active == self:
			self.check_used_by_references()
		if DATID.weapons in ids:
			self.targeting_ddw.setentries(self.toplevel.data_context.weapons.names + ('None',))
		if DATID.techdata in ids:
			self.energy_ddw.setentries(self.toplevel.data_context.technology.names + ('None',))
		if DATID.orders in ids:
			self.obscured_ddw.setentries(self.toplevel.data_context.orders.names + ('None',))

		if self.toplevel.data_context.settings.settings.get('reference_limits', True):
			if DATID.weapons in ids:
				self.targetingentry.range[1] = self.toplevel.data_context.weapons.entry_count()
			if DATID.techdata in ids:
				self.energyentry.range[1] = self.toplevel.data_context.technology.entry_count()
			if DATID.orders in ids:
				self.obscuredentry.range[1] = self.toplevel.data_context.orders.entry_count()
		else:
			self.targetingentry.range[1] = 255
			self.energyentry.range[1] = 255
			self.obscuredentry.range[1] = 255


	def choose_icon(self):
		def update_icon(index):
			self.highlightentry.set(index)
		IconSelectDialog(self, self.toplevel.data_context, update_icon, self.highlightentry.get(), none_index=65535)

	def drawpreview(self):
		self.preview.delete(ALL)
		index = self.highlightentry.get()
		image = self.toplevel.data_context.get_cmdicon(index)
		if image:
			self.preview.create_image(19-image[1]/2+(image[0].width()-image[2])/2, 19-image[3]/2+(image[0].height()-image[4])/2, image=image[0])

	def load_entry(self, entry):
		self.label.set(entry.label)
		self.weapontargeting.set(entry.use_weapon_targeting)
		self.is_secondary.set(entry.unused_is_secondary)
		self.allow_non_subunits.set(entry.unused_allow_non_subunits)
		self.changes_subunit_order.set(entry.changes_subunit_order)
		self.allow_subunits.set(entry.unused_allow_subunits)
		self.interruptable.set(entry.interruptable)
		self.waypoints_slowdown.set(entry.waypoints_slowdown)
		self.queueable.set(entry.queueable)
		self.disabled_maintain_unit_target.set(entry.disabled_maintain_unit_target)
		self.obstructable.set(entry.obstructable)
		self.flee_unreturnable_damage.set(entry.flee_unreturnable_damage)
		self.requires_movable_unit.set(entry.unused_requires_movable_unit)
		self.targeting.set(entry.weapon_targeting)
		self.energy.set(entry.technology_energy)
		self.animation.set(entry.iscript_animation)
		self.highlightentry.set(entry.highlight_icon)
		self.requirements.set(entry.requirements)
		self.obscured.set(entry.obscured_order)
		
		self.drawpreview()

	def save_entry(self, entry):
		if self.label.get() != entry.label:
			entry.label = self.label.get()
			self.edited = True
			if self.toplevel.data_context.settings.settings.get('customlabels'):
				self.toplevel.data_context.dat_data(DATID.orders).update_names()
		if self.weapontargeting.get() != entry.use_weapon_targeting:
			entry.use_weapon_targeting = self.weapontargeting.get()
			self.edited = True
		if self.is_secondary.get() != entry.unused_is_secondary:
			entry.unused_is_secondary = self.is_secondary.get()
			self.edited = True
		if self.allow_non_subunits.get() != entry.unused_allow_non_subunits:
			entry.unused_allow_non_subunits = self.allow_non_subunits.get()
			self.edited = True
		if self.changes_subunit_order.get() != entry.changes_subunit_order:
			entry.changes_subunit_order = self.changes_subunit_order.get()
			self.edited = True
		if self.allow_subunits.get() != entry.unused_allow_subunits:
			entry.unused_allow_subunits = self.allow_subunits.get()
			self.edited = True
		if self.interruptable.get() != entry.interruptable:
			entry.interruptable = self.interruptable.get()
			self.edited = True
		if self.waypoints_slowdown.get() != entry.waypoints_slowdown:
			entry.waypoints_slowdown = self.waypoints_slowdown.get()
			self.edited = True
		if self.queueable.get() != entry.queueable:
			entry.queueable = self.queueable.get()
			self.edited = True
		if self.disabled_maintain_unit_target.get() != entry.disabled_maintain_unit_target:
			entry.disabled_maintain_unit_target = self.disabled_maintain_unit_target.get()
			self.edited = True
		if self.obstructable.get() != entry.obstructable:
			entry.obstructable = self.obstructable.get()
			self.edited = True
		if self.flee_unreturnable_damage.get() != entry.flee_unreturnable_damage:
			entry.flee_unreturnable_damage = self.flee_unreturnable_damage.get()
			self.edited = True
		if self.requires_movable_unit.get() != entry.unused_requires_movable_unit:
			entry.unused_requires_movable_unit = self.requires_movable_unit.get()
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
		if self.requirements.get() != entry.requirements:
			entry.requirements = self.requirements.get()
			self.edited = True
		if self.obscured.get() != entry.obscured_order:
			entry.obscured_order = self.obscured.get()
			self.edited = True
