
from __future__ import annotations

from .DATTab import DATTab
from ..DataID import DATID, DataID, UnitsTabID, AnyID
from ..DATRef import DATRefs, DATRef
from ..IconSelectDialog import IconSelectDialog

from ...FileFormats.DAT import DATUnit, DATOrder

from ...Utilities import UIKit as UI
from ...Utilities import Assets

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

class OrdersTab(DATTab):
	DAT_ID = DATID.orders

	def __init__(self, parent: UI.Misc, delegate: MainDelegate) -> None:
		DATTab.__init__(self, parent, delegate)
		scrollview = UI.ScrollView(self)

		self.targetingentry = UI.IntegerVar(0,[0,130])
		self.targeting = UI.IntVar()
		self.energyentry = UI.IntegerVar(0,[0,44])
		self.energy = UI.IntVar()
		self.obscuredentry = UI.IntegerVar(0,[0,189])
		self.obscured = UI.IntVar()
		self.labelentry = UI.IntegerVar(0,[0,0])
		self.label = UI.IntVar()
		self.animationentry = UI.IntegerVar(0,[0,28])
		self.animation = UI.IntVar()
		self.highlightentry = UI.IntegerVar(0, [0,65535])
		self.highlightdd = UI.IntVar()
		self.requirements = UI.IntegerVar(0, [0,65535])

		l = UI.LabelFrame(scrollview.content_view, text='Order Properties:')
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='Targeting:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.targetingentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT, padx=2)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.targeting_ddw = UI.DropDown(f, self.targeting, [], self.targetingentry, width=25)
		self.targeting_ddw.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		UI.Button(f, text='Jump ->', command=lambda: self.jump(DATID.weapons, self.targeting.get())).pack(side=UI.LEFT, padx=2)
		self.tip(f, 'Targeting', 'OrdTargeting')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Energy:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.energyentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT, padx=2)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.energy_ddw = UI.DropDown(f, self.energy, [], self.energyentry, width=25)
		self.energy_ddw.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		UI.Button(f, text='Jump ->', command=lambda: self.jump(DATID.techdata, self.energy.get())).pack(side=UI.LEFT, padx=2)
		self.tip(f, 'Energy', 'OrdEnergy')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Obscured:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.obscuredentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT, padx=2)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.obscured_ddw = UI.DropDown(f, self.obscured, [], self.obscuredentry, width=25)
		self.obscured_ddw.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		UI.Button(f, text='Jump ->', command=lambda: self.jump(DATID.orders, self.obscured.get())).pack(side=UI.LEFT, padx=2)
		self.tip(f, 'Obscured', 'OrdObscured')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Label:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.labelentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT, padx=2)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.labels = UI.DropDown(f, self.label, [], self.labelentry, width=25)
		self.labels.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.tip(f, 'Label', 'OrdLabel')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Animation:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.animationentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT, padx=2)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		UI.DropDown(f, self.animation, Assets.data_cache(Assets.DataReference.Animations), self.animationentry, width=25).pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.tip(f, 'Animation', 'OrdAnimation')
		f.pack(fill=UI.X)
		m = UI.Frame(s)
		ls = UI.Frame(m)
		f = UI.Frame(ls)
		UI.Label(f, text='Highlight:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.highlightentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT, padx=2)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.highlight_ddw = UI.DropDown(f, self.highlightdd, [], self.highlightentry, width=25, none_value=65535)
		self.highlight_ddw.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.tip(f, 'Highlight', 'OrdHighlight')
		UI.Button(f, image=Assets.get_image('find'), command=self.choose_icon, width=20, height=20).pack(side=UI.LEFT, padx=2)
		f.pack(fill=UI.X)
		f = UI.Frame(ls)
		UI.Label(f, text='ReqIndex:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.requirements, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT, padx=2)
		self.tip(f, 'ReqIndex', 'OrdReq')
		f.pack(fill=UI.X)
		ls.pack(side=UI.LEFT, fill=UI.X)
		ls = UI.Frame(m, relief=UI.SUNKEN, bd=1)
		self.preview = UI.Canvas(ls, width=34, height=34, background='#000000', theme_tag='preview') # type: ignore[call-arg]
		self.preview.pack()
		self.preview.bind(UI.Mouse.Click_Left(), lambda *_: self.choose_icon())
		ls.pack(side=UI.RIGHT)
		m.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(fill=UI.X)

		self.weapontargeting = UI.IntVar()
		self.is_secondary = UI.IntVar()
		self.allow_non_subunits = UI.IntVar()
		self.changes_subunit_order = UI.IntVar()
		self.allow_subunits = UI.IntVar()
		self.interruptable = UI.IntVar()
		self.waypoints_slowdown = UI.IntVar()
		self.queueable = UI.IntVar()
		self.disabled_maintain_unit_target = UI.IntVar()
		self.obstructable = UI.IntVar()
		self.flee_unreturnable_damage = UI.IntVar()
		self.requires_movable_unit = UI.IntVar()

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
		l = UI.LabelFrame(scrollview.content_view, text='Flags:')
		s = UI.Frame(l)
		for c in flags:
			cc = UI.Frame(s, width=20)
			for t,v,h in c:
				f = UI.Frame(cc)
				UI.Checkbutton(f, text=t, variable=v).pack(side=UI.LEFT)
				self.tip(f, t, h)
				f.pack(fill=UI.X)
			cc.pack(side=UI.LEFT, fill=UI.Y)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(fill=UI.X)

		scrollview.pack(fill=UI.BOTH, expand=1)

		self.setup_used_by((
			DATRefs(DATID.units, lambda unit: (
				DATRef('Computer Idle', cast(DATUnit, unit).comp_ai_idle, dat_sub_tab=UnitsTabID.ai_actions),
				DATRef('Human Idle', cast(DATUnit, unit).human_ai_idle, dat_sub_tab=UnitsTabID.ai_actions),
				DATRef('Return to Idle', cast(DATUnit, unit).return_to_idle, dat_sub_tab=UnitsTabID.ai_actions),
				DATRef('Attach Unit', cast(DATUnit, unit).attack_unit, dat_sub_tab=UnitsTabID.ai_actions),
				DATRef('Attack Move', cast(DATUnit, unit).attack_move, dat_sub_tab=UnitsTabID.ai_actions)
			)),
		))

		self.highlightentry.trace_add('write', lambda *_: self.drawpreview())

	def updated_pointer_entries(self, ids: list[AnyID]) -> None:
		if DataID.stat_txt in ids:
			self.labels.setentries(('None',) + self.delegate.data_context.stat_txt.strings)
			self.labelentry.range[1] = len(self.delegate.data_context.stat_txt.strings)
		if DataID.cmdicons in ids:
			self.highlight_ddw.setentries(self.delegate.data_context.cmdicons.names + ('None',))
			# TODO: Limit-1 while supporting none_value
			# self.highlightentry.range[1] = self.delegate.data_context.cmdicons.frame_count()

		if DATID.units in ids and self.delegate.active_tab() == self:
			self.check_used_by_references()
		if DATID.weapons in ids:
			self.targeting_ddw.setentries(self.delegate.data_context.weapons.names + ('None',))
		if DATID.techdata in ids:
			self.energy_ddw.setentries(self.delegate.data_context.technology.names + ('None',))
		if DATID.orders in ids:
			self.obscured_ddw.setentries(self.delegate.data_context.orders.names + ('None',))

		if self.delegate.data_context.config.settings.reference_limits.value:
			if DATID.weapons in ids:
				self.targetingentry.range[1] = self.delegate.data_context.weapons.entry_count()
			if DATID.techdata in ids:
				self.energyentry.range[1] = self.delegate.data_context.technology.entry_count()
			if DATID.orders in ids:
				self.obscuredentry.range[1] = self.delegate.data_context.orders.entry_count()
		else:
			self.targetingentry.range[1] = 255
			self.energyentry.range[1] = 255
			self.obscuredentry.range[1] = 255

	def choose_icon(self) -> None:
		def update_icon(index: int) -> None:
			self.highlightentry.set(index)
		IconSelectDialog(self, data_context=self.delegate.data_context, delegate=update_icon, selected_index=self.highlightentry.get(), none_index=65535)

	def drawpreview(self) -> None:
		self.preview.delete(UI.ALL)
		index = self.highlightentry.get()
		image = self.delegate.data_context.get_cmdicon(index)
		if image:
			self.preview.create_image(19-image[1]//2+(image[0].width()-image[2])//2, 19-image[3]//2+(image[0].height()-image[4])//2, image=image[0])

	def load_entry(self, entry: DATOrder) -> None:
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

	def save_entry(self, entry: DATOrder) -> None:
		if self.label.get() != entry.label:
			entry.label = self.label.get()
			self.edited = True
			if self.delegate.data_context.config.settings.labels.custom.value:
				self.delegate.data_context.dat_data(DATID.orders).update_names()
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
