
from __future__ import annotations

from .DATUnitsTab import DATUnitsTab
from ...DataID import DATID, AnyID

from ....FileFormats.DAT.UnitsDAT import DATUnit

from ....Utilities import UIKit as UI

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ...Delegates import MainDelegate, SubDelegate

class AdvancedUnitsTab(DATUnitsTab):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, sub_delegate: SubDelegate) -> None:
		DATUnitsTab.__init__(self, parent, delegate, sub_delegate)
		scrollview = UI.ScrollView(self)

		self.flyer = UI.IntVar()
		self.hero = UI.IntVar()
		self.regenerate = UI.IntVar()
		self.spellcaster = UI.IntVar()
		self.permanent_cloak = UI.IntVar()
		self.invincible = UI.IntVar()
		self.organic = UI.IntVar()
		self.mechanical = UI.IntVar()
		self.robotic = UI.IntVar()
		self.detector = UI.IntVar()
		self.subunit = UI.IntVar()
		self.resource_containter = UI.IntVar()
		self.resource_depot = UI.IntVar()
		self.resource_miner = UI.IntVar()
		self.requires_psi = UI.IntVar()
		self.requires_creep = UI.IntVar()
		self.two_units_in_one_egg = UI.IntVar()
		self.single_entity = UI.IntVar()
		self.burrowable = UI.IntVar()
		self.cloakable = UI.IntVar()
		self.battlereactions = UI.IntVar()
		self.fullautoattack = UI.IntVar()
		self.building = UI.IntVar()
		self.addon = UI.IntVar()
		self.flying_building = UI.IntVar()
		self.use_medium_overlays = UI.IntVar()
		self.use_large_overlays = UI.IntVar()
		self.ignore_supply_check = UI.IntVar()
		self.produces_units = UI.IntVar()
		self.animated_idle = UI.IntVar()
		self.pickup_item = UI.IntVar()
		self.unused = UI.IntVar()

		flags = [
			[
				('Flyer', self.flyer, 'UnitAdvFlyer'),
				('Hero', self.hero, 'UnitAdvHero'),
				('Regenerate', self.regenerate, 'UnitAdvRegenerate'),
				('Spellcaster', self.spellcaster, 'UnitAdvSpellcaster'),
				('Permanently Cloaked', self.permanent_cloak, 'UnitAdvPermaCloak'),
				('Invincible', self.invincible, 'UnitAdvInvincible'),
				('Organic', self.organic, 'UnitAdvOrganic'),
				('Mechanical', self.mechanical, 'UnitAdvMechanical'),
				('Robotic', self.robotic, 'UnitAdvRobotic'),
				('Detector', self.detector, 'UnitAdvDetector'),
				('Subunit', self.subunit, 'UnitAdvSubunit'),
			],[
				('Resource Container', self.resource_containter, 'UnitAdvResContainer'),
				('Resource Depot', self.resource_depot, 'UnitAdvResDepot'),
				('Resource Miner', self.resource_miner, 'UnitAdvWorker'),
				('Requires Psi', self.requires_psi, 'UnitAdvReqPsi'),
				('Requires Creep', self.requires_creep, 'UnitAdvReqCreep'),
				('Two Units in One Egg', self.two_units_in_one_egg, 'UnitAdvTwoInEgg'),
				('Single Entity', self.single_entity, 'UnitAdvSingleEntity'),
				('Burrowable', self.burrowable, 'UnitAdvBurrow'),
				('Cloakable', self.cloakable, 'UnitAdvCloak'),
				('Battle Reactions', self.battlereactions, 'UnitAdvBattleReactions'),
				('Full Auto-Attack', self.fullautoattack, 'UnitAdvAutoAttack'),
			],[
				('Building', self.building, 'UnitAdvBuilding'),
				('Addon', self.addon, 'UnitAdvAddon'),
				('Flying Building', self.flying_building, 'UnitAdvFlyBuilding'),
				('Use Medium Overlays', self.use_medium_overlays, 'UnitAdvOverlayMed'),
				('Use Large Overlays', self.use_large_overlays, 'UnitAdvOverlayLarge'),
				('Ignore Supply Check', self.ignore_supply_check, 'UnitAdvIgnoreSupply'),
				('Produces Units(?)', self.produces_units, 'UnitAdvProducesUnits'),
				('Animated Overlay', self.animated_idle, 'UnitAdvAnimIdle'),
				('Carryable', self.pickup_item, 'UnitAdvPickup'),
				('Unknown', self.unused, 'UnitAdvUnused'),
			],
		]
		l = UI.LabelFrame(scrollview.content_view, text='Advanced Properties:')
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

		self.infestentry = UI.IntegerVar(0, [0,228])
		self.infestdd = UI.IntVar()
		self.subunitoneentry = UI.IntegerVar(0,[0,228])
		self.subunitone = UI.IntVar()
		self.subunittwoentry = UI.IntegerVar(0,[0,228])
		self.subunittwo = UI.IntVar()
		self.reqIndex = UI.IntegerVar(0, [0,65535])
		self.unknown1 = UI.IntVar()
		self.unknown2 = UI.IntVar()
		self.unknown4 = UI.IntVar()
		self.unknown8 = UI.IntVar()
		self.unknown10 = UI.IntVar()
		self.unknown20 = UI.IntVar()
		self.unknown40 = UI.IntVar()
		self.unknown80 = UI.IntVar()

		l = UI.LabelFrame(scrollview.content_view, text='Other Properties:')

		f = UI.Frame(l)
		UI.Label(f, text='Infestation:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		self.infestentryw = UI.Entry(f, textvariable=self.infestentry, font=UI.Font.fixed(), width=5)
		self.infestentryw.pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.infestddw = UI.DropDown(f, self.infestdd, [], self.infestentry)
		self.infestddw.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.infestbtnw = UI.Button(f, text='Jump ->', command=lambda: self.jump(DATID.units, self.infestdd.get()))
		self.infestbtnw.pack(side=UI.LEFT)
		self.tip(f, 'Infestation', 'UnitInfestation')
		f.pack(fill=UI.X)

		f = UI.Frame(l)
		UI.Label(f, text='Subunit 1:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.subunitoneentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.subunitone_ddw = UI.DropDown(f, self.subunitone, [], self.subunitoneentry)
		self.subunitone_ddw.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.subunitone_btnw = UI.Button(f, text='Jump ->', command=lambda: self.jump(DATID.units, self.subunitone.get()))
		self.subunitone_btnw.pack(side=UI.LEFT)
		self.tip(f, 'Subunit 1', 'UnitSub1')
		f.pack(fill=UI.X)

		f = UI.Frame(l)
		UI.Label(f, text='Subunit 2:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.subunittwoentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.subunittwo_ddw = UI.DropDown(f, self.subunittwo, [], self.subunittwoentry)
		self.subunittwo_ddw.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.subunittwo_btnw = UI.Button(f, text='Jump ->', command=lambda: self.jump(DATID.units, self.subunittwo.get()))
		self.subunittwo_btnw.pack(side=UI.LEFT)
		self.tip(f, 'Subunit 2', 'UnitSub2')
		f.pack(fill=UI.X)

		f = UI.Frame(l)
		r = UI.Frame(f)
		UI.Label(r, text='ReqIndex:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(r, textvariable=self.reqIndex, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(r, 'Requirements Index', 'UnitReq')
		r.pack(side=UI.LEFT)

		unknowns = UI.Frame(f)
		self.makeCheckbox(unknowns, self.unknown1, '0x01', 'UnitMov01').grid(column=0,row=0)
		self.makeCheckbox(unknowns, self.unknown2, '0x02', 'UnitMov02').grid(column=1,row=0)
		self.makeCheckbox(unknowns, self.unknown4, '0x04', 'UnitMov04').grid(column=2,row=0)
		self.makeCheckbox(unknowns, self.unknown8, '0x08', 'UnitMov08').grid(column=3,row=0)
		self.makeCheckbox(unknowns, self.unknown10, '0x10', 'UnitMov10').grid(column=0,row=1)
		self.makeCheckbox(unknowns, self.unknown20, '0x20', 'UnitMov20').grid(column=1,row=1)
		self.makeCheckbox(unknowns, self.unknown40, '0x40', 'UnitMov40').grid(column=2,row=1)
		self.makeCheckbox(unknowns, self.unknown80, '0x80', 'UnitMov80').grid(column=3,row=1)
		unknowns.pack(side=UI.RIGHT)
		f.pack(fill=UI.X)

		l.pack(fill=UI.X, expand=1)

		scrollview.pack(fill=UI.BOTH, expand=1)

	def copy(self) -> None:
		if not self.delegate.data_context.units.dat:
			return
		text = self.delegate.data_context.units.dat.export_entry(self.sub_delegate.id, export_properties=[
			DATUnit.Property.subunit1,
			DATUnit.Property.subunit2,
			DATUnit.Property.unknown_flags,
			DATUnit.Property.special_ability_flags,
			DATUnit.Property.infestation,
			DATUnit.Property.requirements,
		])
		self.clipboard_set(text) # type: ignore[attr-defined]

	def updated_pointer_entries(self, ids: list[AnyID]) -> None:
		if not DATID.units in ids:
			return

		names = list(self.delegate.data_context.units.names)
		if self.delegate.data_context.units.is_expanded():
			names[self.delegate.data_context.units.dat_type.FORMAT.entries] = 'None'
		else:
			names.append('None')
		self.infestddw.setentries(names)
		self.subunitone_ddw.setentries(names)
		self.subunittwo_ddw.setentries(names)

		limit = 65535
		if self.delegate.data_context.config.settings.reference_limits.value:
			limit = self.delegate.data_context.units.entry_count()
			if self.delegate.data_context.units.is_expanded():
				limit -= 1
		self.infestentry.range[1] = limit
		self.subunitoneentry.range[1] = limit
		self.subunittwoentry.range[1] = limit

	def load_data(self, entry: DATUnit) -> None:
		self.subunitone.set(entry.subunit1)
		self.subunittwo.set(entry.subunit2)

		unknown_flags_fields = (
			(self.unknown1, DATUnit.UnknownFlags.unknown0x01),
			(self.unknown2, DATUnit.UnknownFlags.unknown0x02),
			(self.unknown4, DATUnit.UnknownFlags.unknown0x04),
			(self.unknown8, DATUnit.UnknownFlags.unknown0x08),
			(self.unknown10, DATUnit.UnknownFlags.unknown0x10),
			(self.unknown20, DATUnit.UnknownFlags.unknown0x20),
			(self.unknown40, DATUnit.UnknownFlags.unknown0x40),
			(self.unknown80, DATUnit.UnknownFlags.unknown0x80)
		)
		for (variable, flag) in unknown_flags_fields:
			variable.set(entry.unknown_flags & flag == flag)

		special_ability_flags_fields = (
			(self.building, DATUnit.SpecialAbilityFlag.building),
			(self.addon, DATUnit.SpecialAbilityFlag.addon),
			(self.flyer, DATUnit.SpecialAbilityFlag.flyer),
			(self.resource_miner, DATUnit.SpecialAbilityFlag.resource_miner),
			(self.subunit, DATUnit.SpecialAbilityFlag.subunit),
			(self.flying_building, DATUnit.SpecialAbilityFlag.flying_building),
			(self.hero, DATUnit.SpecialAbilityFlag.hero),
			(self.regenerate, DATUnit.SpecialAbilityFlag.regenerate),
			(self.animated_idle, DATUnit.SpecialAbilityFlag.animated_idle),
			(self.cloakable, DATUnit.SpecialAbilityFlag.cloakable),
			(self.two_units_in_one_egg, DATUnit.SpecialAbilityFlag.two_units_in_one_egg),
			(self.single_entity, DATUnit.SpecialAbilityFlag.single_entity),
			(self.resource_depot, DATUnit.SpecialAbilityFlag.resource_depot),
			(self.resource_containter, DATUnit.SpecialAbilityFlag.resource_container),
			(self.robotic, DATUnit.SpecialAbilityFlag.robotic),
			(self.detector, DATUnit.SpecialAbilityFlag.detector),
			(self.organic, DATUnit.SpecialAbilityFlag.organic),
			(self.requires_creep, DATUnit.SpecialAbilityFlag.requires_creep),
			(self.unused, DATUnit.SpecialAbilityFlag.unused),
			(self.requires_psi, DATUnit.SpecialAbilityFlag.requires_psi),
			(self.burrowable, DATUnit.SpecialAbilityFlag.burrowable),
			(self.spellcaster, DATUnit.SpecialAbilityFlag.spellcaster),
			(self.permanent_cloak, DATUnit.SpecialAbilityFlag.permanent_cloak),
			(self.pickup_item, DATUnit.SpecialAbilityFlag.pickup_item),
			(self.ignore_supply_check, DATUnit.SpecialAbilityFlag.ignores_supply_check),
			(self.use_medium_overlays, DATUnit.SpecialAbilityFlag.use_medium_overlays),
			(self.use_large_overlays, DATUnit.SpecialAbilityFlag.use_large_overlays),
			(self.battlereactions, DATUnit.SpecialAbilityFlag.battle_reactions),
			(self.fullautoattack, DATUnit.SpecialAbilityFlag.full_auto_attack),
			(self.invincible, DATUnit.SpecialAbilityFlag.invincible),
			(self.mechanical, DATUnit.SpecialAbilityFlag.mechanical),
			(self.produces_units, DATUnit.SpecialAbilityFlag.produces_units)
		)
		for (variable, flag) in special_ability_flags_fields:
			variable.set(entry.special_ability_flags & flag == flag)

		infestable = (entry.infestation is not None)
		self.infestentry.set(entry.infestation if infestable else 0)
		state = (UI.DISABLED,UI.NORMAL)[infestable]
		self.infestentryw['state'] = state
		self.infestddw['state'] = state
		self.infestbtnw['state'] = state

		self.reqIndex.set(entry.requirements)

	def save_data(self, entry: DATUnit) -> bool:
		edited = False
		if self.subunitone.get() != entry.subunit1:
			entry.subunit1 = self.subunitone.get()
			edited = True
		if self.subunittwo.get() != entry.subunit2:
			entry.subunit2 = self.subunittwo.get()
			edited = True

		unknown_flags = 0
		unknown_flags_fields = (
			(self.unknown1, DATUnit.UnknownFlags.unknown0x01),
			(self.unknown2, DATUnit.UnknownFlags.unknown0x02),
			(self.unknown4, DATUnit.UnknownFlags.unknown0x04),
			(self.unknown8, DATUnit.UnknownFlags.unknown0x08),
			(self.unknown10, DATUnit.UnknownFlags.unknown0x10),
			(self.unknown20, DATUnit.UnknownFlags.unknown0x20),
			(self.unknown40, DATUnit.UnknownFlags.unknown0x40),
			(self.unknown80, DATUnit.UnknownFlags.unknown0x80)
		)
		for (variable, flag) in unknown_flags_fields:
			if variable.get():
				unknown_flags |= flag
		if unknown_flags != entry.unknown_flags:
			entry.unknown_flags = unknown_flags
			edited = True

		special_ability_flags = 0
		special_ability_flags_fields = (
			(self.building, DATUnit.SpecialAbilityFlag.building),
			(self.addon, DATUnit.SpecialAbilityFlag.addon),
			(self.flyer, DATUnit.SpecialAbilityFlag.flyer),
			(self.resource_miner, DATUnit.SpecialAbilityFlag.resource_miner),
			(self.subunit, DATUnit.SpecialAbilityFlag.subunit),
			(self.flying_building, DATUnit.SpecialAbilityFlag.flying_building),
			(self.hero, DATUnit.SpecialAbilityFlag.hero),
			(self.regenerate, DATUnit.SpecialAbilityFlag.regenerate),
			(self.animated_idle, DATUnit.SpecialAbilityFlag.animated_idle),
			(self.cloakable, DATUnit.SpecialAbilityFlag.cloakable),
			(self.two_units_in_one_egg, DATUnit.SpecialAbilityFlag.two_units_in_one_egg),
			(self.single_entity, DATUnit.SpecialAbilityFlag.single_entity),
			(self.resource_depot, DATUnit.SpecialAbilityFlag.resource_depot),
			(self.resource_containter, DATUnit.SpecialAbilityFlag.resource_container),
			(self.robotic, DATUnit.SpecialAbilityFlag.robotic),
			(self.detector, DATUnit.SpecialAbilityFlag.detector),
			(self.organic, DATUnit.SpecialAbilityFlag.organic),
			(self.requires_creep, DATUnit.SpecialAbilityFlag.requires_creep),
			(self.unused, DATUnit.SpecialAbilityFlag.unused),
			(self.requires_psi, DATUnit.SpecialAbilityFlag.requires_psi),
			(self.burrowable, DATUnit.SpecialAbilityFlag.burrowable),
			(self.spellcaster, DATUnit.SpecialAbilityFlag.spellcaster),
			(self.permanent_cloak, DATUnit.SpecialAbilityFlag.permanent_cloak),
			(self.pickup_item, DATUnit.SpecialAbilityFlag.pickup_item),
			(self.ignore_supply_check, DATUnit.SpecialAbilityFlag.ignores_supply_check),
			(self.use_medium_overlays, DATUnit.SpecialAbilityFlag.use_medium_overlays),
			(self.use_large_overlays, DATUnit.SpecialAbilityFlag.use_large_overlays),
			(self.battlereactions, DATUnit.SpecialAbilityFlag.battle_reactions),
			(self.fullautoattack, DATUnit.SpecialAbilityFlag.full_auto_attack),
			(self.invincible, DATUnit.SpecialAbilityFlag.invincible),
			(self.mechanical, DATUnit.SpecialAbilityFlag.mechanical),
			(self.produces_units, DATUnit.SpecialAbilityFlag.produces_units)
		)
		for (variable, flag) in special_ability_flags_fields:
			if variable.get():
				special_ability_flags |= flag
		if special_ability_flags != entry.special_ability_flags:
			entry.special_ability_flags = special_ability_flags
			edited = True

		if entry.infestation is not None and self.infestentry.get() != entry.infestation:
			entry.infestation = self.infestentry.get()
			edited = True
		if self.reqIndex.get() != entry.requirements:
			entry.requirements = self.reqIndex.get()
			edited = True

		return edited
