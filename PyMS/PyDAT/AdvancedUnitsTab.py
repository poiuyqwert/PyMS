
from .DATUnitsTab import DATUnitsTab
from .DataID import DATID

from ..FileFormats.DAT.UnitsDAT import Unit

from ..Utilities.DropDown import DropDown
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.UIKit import *
from ..Utilities.ScrollView import ScrollView

class AdvancedUnitsTab(DATUnitsTab):
	def __init__(self, parent, toplevel, parent_tab):
		DATUnitsTab.__init__(self, parent, toplevel, parent_tab)
		self.toplevel = toplevel
		scrollview = ScrollView(self)

		self.flyer = IntVar()
		self.hero = IntVar()
		self.regenerate = IntVar()
		self.spellcaster = IntVar()
		self.permanent_cloak = IntVar()
		self.invincible = IntVar()
		self.organic = IntVar()
		self.mechanical = IntVar()
		self.robotic = IntVar()
		self.detector = IntVar()
		self.subunit = IntVar()
		self.resource_containter = IntVar()
		self.resource_depot = IntVar()
		self.resource_miner = IntVar()
		self.requires_psi = IntVar()
		self.requires_creep = IntVar()
		self.two_units_in_one_egg = IntVar()
		self.single_entity = IntVar()
		self.burrowable = IntVar()
		self.cloakable = IntVar()
		self.battlereactions = IntVar()
		self.fullautoattack = IntVar()
		self.building = IntVar()
		self.addon = IntVar()
		self.flying_building = IntVar()
		self.use_medium_overlays = IntVar()
		self.use_large_overlays = IntVar()
		self.ignore_supply_check = IntVar()
		self.produces_units = IntVar()
		self.animated_idle = IntVar()
		self.pickup_item = IntVar()
		self.unused = IntVar()

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
		l = LabelFrame(scrollview.content_view, text='Advanced Properties:')
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

		self.infestentry = IntegerVar(0, [0,228])
		self.infestdd = IntVar()
		self.subunitoneentry = IntegerVar(0,[0,228])
		self.subunitone = IntVar()
		self.subunittwoentry = IntegerVar(0,[0,228])
		self.subunittwo = IntVar()
		self.reqIndex = IntegerVar(0, [0,65535])
		self.unknown1 = IntVar()
		self.unknown2 = IntVar()
		self.unknown4 = IntVar()
		self.unknown8 = IntVar()
		self.unknown10 = IntVar()
		self.unknown20 = IntVar()
		self.unknown40 = IntVar()
		self.unknown80 = IntVar()

		l = LabelFrame(scrollview.content_view, text='Other Properties:')

		f = Frame(l)
		Label(f, text='Infestation:', width=9, anchor=E).pack(side=LEFT)
		self.infestentryw = Entry(f, textvariable=self.infestentry, font=Font.fixed(), width=5)
		self.infestentryw.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.infestddw = DropDown(f, self.infestdd, [], self.infestentry)
		self.infestddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.infestbtnw = Button(f, text='Jump ->', command=lambda: self.jump(DATID.units, self.infestdd.get()))
		self.infestbtnw.pack(side=LEFT)
		self.tip(f, 'Infestation', 'UnitInfestation')
		f.pack(fill=X)

		f = Frame(l)
		Label(f, text='Subunit 1:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.subunitoneentry, font=Font.fixed(), width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.subunitone_ddw = DropDown(f, self.subunitone, [], self.subunitoneentry)
		self.subunitone_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.subunitone_btnw = Button(f, text='Jump ->', command=lambda: self.jump(DATID.units, self.subunitone.get()))
		self.subunitone_btnw.pack(side=LEFT)
		self.tip(f, 'Subunit 1', 'UnitSub1')
		f.pack(fill=X)

		f = Frame(l)
		Label(f, text='Subunit 2:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.subunittwoentry, font=Font.fixed(), width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.subunittwo_ddw = DropDown(f, self.subunittwo, [], self.subunittwoentry)
		self.subunittwo_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.subunittwo_btnw = Button(f, text='Jump ->', command=lambda: self.jump(DATID.units, self.subunittwo.get()))
		self.subunittwo_btnw.pack(side=LEFT)
		self.tip(f, 'Subunit 2', 'UnitSub2')
		f.pack(fill=X)

		f = Frame(l)
		r = Frame(f)
		Label(r, text='ReqIndex:', width=9, anchor=E).pack(side=LEFT)
		Entry(r, textvariable=self.reqIndex, font=Font.fixed(), width=5).pack(side=LEFT)
		self.tip(r, 'Requirements Index', 'UnitReq')
		r.pack(side=LEFT)

		unknowns = Frame(f)
		self.makeCheckbox(unknowns, self.unknown1, '0x01', 'UnitMov01').grid(column=0,row=0)
		self.makeCheckbox(unknowns, self.unknown2, '0x02', 'UnitMov02').grid(column=1,row=0)
		self.makeCheckbox(unknowns, self.unknown4, '0x04', 'UnitMov04').grid(column=2,row=0)
		self.makeCheckbox(unknowns, self.unknown8, '0x08', 'UnitMov08').grid(column=3,row=0)
		self.makeCheckbox(unknowns, self.unknown10, '0x10', 'UnitMov10').grid(column=0,row=1)
		self.makeCheckbox(unknowns, self.unknown20, '0x20', 'UnitMov20').grid(column=1,row=1)
		self.makeCheckbox(unknowns, self.unknown40, '0x40', 'UnitMov40').grid(column=2,row=1)
		self.makeCheckbox(unknowns, self.unknown80, '0x80', 'UnitMov80').grid(column=3,row=1)
		# u = [
		# 	[
		# 		('01', self.unknown1),
		# 		('02', self.unknown2),
		# 		('04', self.unknown4),
		# 		('08', self.unknown8),
		# 	],[
		# 		('10', self.unknown10),
		# 		('20', self.unknown20),
		# 		('40', self.unknown40),
		# 		('80', self.unknown80),
		# 	],
		# ]
		# for c in u:
		# 	cc = Frame(unknowns)
		# 	for t,v in c:
		# 		f = Frame(cc)
		# 		self.makeCheckbox(f,v,'0x'+t,'UnitMov'+t).pack(side=LEFT)
		# 		f.pack(fill=X)
		# 	cc.pack(side=LEFT)
		unknowns.pack(side=RIGHT)
		f.pack(fill=X)

		l.pack(fill=X, expand=1)

		scrollview.pack(fill=BOTH, expand=1)

	def copy(self):
		text = self.toplevel.data_context.units.dat.export_entry(self.parent_tab.id, export_properties=[
			Unit.Property.subunit1,
			Unit.Property.subunit2,
			Unit.Property.unknown_flags,
			Unit.Property.special_ability_flags,
			Unit.Property.infestation,
			Unit.Property.requirements,
		])
		self.clipboard_set(text)

	def updated_pointer_entries(self, ids):
		if not DATID.units in ids:
			return

		names = list(self.toplevel.data_context.units.names)
		if self.toplevel.data_context.units.is_expanded():
			names[self.toplevel.data_context.units.dat_type.FORMAT.entries] = 'None'
		else:
			names.append('None')
		self.infestddw.setentries(names)
		self.subunitone_ddw.setentries(names)
		self.subunittwo_ddw.setentries(names)

		limit = 65535
		if self.toplevel.data_context.settings.settings.get('reference_limits', True):
			limit = self.toplevel.data_context.units.entry_count()
			if self.toplevel.data_context.units.is_expanded():
				limit -= 1
		self.infestentry.range[1] = limit
		self.subunitoneentry.range[1] = limit
		self.subunittwoentry.range[1] = limit

	def load_data(self, entry):
		self.subunitone.set(entry.subunit1)
		self.subunittwo.set(entry.subunit2)

		unknown_flags_fields = (
			(self.unknown1, Unit.UnknownFlags.unknown0x01),
			(self.unknown2, Unit.UnknownFlags.unknown0x02),
			(self.unknown4, Unit.UnknownFlags.unknown0x04),
			(self.unknown8, Unit.UnknownFlags.unknown0x08),
			(self.unknown10, Unit.UnknownFlags.unknown0x10),
			(self.unknown20, Unit.UnknownFlags.unknown0x20),
			(self.unknown40, Unit.UnknownFlags.unknown0x40),
			(self.unknown80, Unit.UnknownFlags.unknown0x80)
		)
		for (variable, flag) in unknown_flags_fields:
			variable.set(entry.unknown_flags & flag == flag)

		special_ability_flags_fields = (
			(self.building, Unit.SpecialAbilityFlag.building),
			(self.addon, Unit.SpecialAbilityFlag.addon),
			(self.flyer, Unit.SpecialAbilityFlag.flyer),
			(self.resource_miner, Unit.SpecialAbilityFlag.resource_miner),
			(self.subunit, Unit.SpecialAbilityFlag.subunit),
			(self.flying_building, Unit.SpecialAbilityFlag.flying_building),
			(self.hero, Unit.SpecialAbilityFlag.hero),
			(self.regenerate, Unit.SpecialAbilityFlag.regenerate),
			(self.animated_idle, Unit.SpecialAbilityFlag.animated_idle),
			(self.cloakable, Unit.SpecialAbilityFlag.cloakable),
			(self.two_units_in_one_egg, Unit.SpecialAbilityFlag.two_units_in_one_egg),
			(self.single_entity, Unit.SpecialAbilityFlag.single_entity),
			(self.resource_depot, Unit.SpecialAbilityFlag.resource_depot),
			(self.resource_containter, Unit.SpecialAbilityFlag.resource_container),
			(self.robotic, Unit.SpecialAbilityFlag.robotic),
			(self.detector, Unit.SpecialAbilityFlag.detector),
			(self.organic, Unit.SpecialAbilityFlag.organic),
			(self.requires_creep, Unit.SpecialAbilityFlag.requires_creep),
			(self.unused, Unit.SpecialAbilityFlag.unused),
			(self.requires_psi, Unit.SpecialAbilityFlag.requires_psi),
			(self.burrowable, Unit.SpecialAbilityFlag.burrowable),
			(self.spellcaster, Unit.SpecialAbilityFlag.spellcaster),
			(self.permanent_cloak, Unit.SpecialAbilityFlag.permanent_cloak),
			(self.pickup_item, Unit.SpecialAbilityFlag.pickup_item),
			(self.ignore_supply_check, Unit.SpecialAbilityFlag.ignores_supply_check),
			(self.use_medium_overlays, Unit.SpecialAbilityFlag.use_medium_overlays),
			(self.use_large_overlays, Unit.SpecialAbilityFlag.use_large_overlays),
			(self.battlereactions, Unit.SpecialAbilityFlag.battle_reactions),
			(self.fullautoattack, Unit.SpecialAbilityFlag.full_auto_attack),
			(self.invincible, Unit.SpecialAbilityFlag.invincible),
			(self.mechanical, Unit.SpecialAbilityFlag.mechanical),
			(self.produces_units, Unit.SpecialAbilityFlag.produces_units)
		)
		for (variable, flag) in special_ability_flags_fields:
			variable.set(entry.special_ability_flags & flag == flag)

		infestable = (entry.infestation != None)
		self.infestentry.set(entry.infestation if infestable else 0)
		state = (DISABLED,NORMAL)[infestable]
		self.infestentryw['state'] = state
		self.infestddw['state'] = state
		self.infestbtnw['state'] = state

		self.reqIndex.set(entry.requirements)

	def save_data(self, entry):
		edited = False
		if self.subunitone.get() != entry.subunit1:
			entry.subunit1 = self.subunitone.get()
			edited = True
		if self.subunittwo.get() != entry.subunit2:
			entry.subunit2 = self.subunittwo.get()
			edited = True

		unknown_flags = 0
		unknown_flags_fields = (
			(self.unknown1, Unit.UnknownFlags.unknown0x01),
			(self.unknown2, Unit.UnknownFlags.unknown0x02),
			(self.unknown4, Unit.UnknownFlags.unknown0x04),
			(self.unknown8, Unit.UnknownFlags.unknown0x08),
			(self.unknown10, Unit.UnknownFlags.unknown0x10),
			(self.unknown20, Unit.UnknownFlags.unknown0x20),
			(self.unknown40, Unit.UnknownFlags.unknown0x40),
			(self.unknown80, Unit.UnknownFlags.unknown0x80)
		)
		for (variable, flag) in unknown_flags_fields:
			if variable.get():
				unknown_flags |= flag
		if unknown_flags != entry.unknown_flags:
			entry.unknown_flags = unknown_flags
			edited = True

		special_ability_flags = 0
		special_ability_flags_fields = (
			(self.building, Unit.SpecialAbilityFlag.building),
			(self.addon, Unit.SpecialAbilityFlag.addon),
			(self.flyer, Unit.SpecialAbilityFlag.flyer),
			(self.resource_miner, Unit.SpecialAbilityFlag.resource_miner),
			(self.subunit, Unit.SpecialAbilityFlag.subunit),
			(self.flying_building, Unit.SpecialAbilityFlag.flying_building),
			(self.hero, Unit.SpecialAbilityFlag.hero),
			(self.regenerate, Unit.SpecialAbilityFlag.regenerate),
			(self.animated_idle, Unit.SpecialAbilityFlag.animated_idle),
			(self.cloakable, Unit.SpecialAbilityFlag.cloakable),
			(self.two_units_in_one_egg, Unit.SpecialAbilityFlag.two_units_in_one_egg),
			(self.single_entity, Unit.SpecialAbilityFlag.single_entity),
			(self.resource_depot, Unit.SpecialAbilityFlag.resource_depot),
			(self.resource_containter, Unit.SpecialAbilityFlag.resource_container),
			(self.robotic, Unit.SpecialAbilityFlag.robotic),
			(self.detector, Unit.SpecialAbilityFlag.detector),
			(self.organic, Unit.SpecialAbilityFlag.organic),
			(self.requires_creep, Unit.SpecialAbilityFlag.requires_creep),
			(self.unused, Unit.SpecialAbilityFlag.unused),
			(self.requires_psi, Unit.SpecialAbilityFlag.requires_psi),
			(self.burrowable, Unit.SpecialAbilityFlag.burrowable),
			(self.spellcaster, Unit.SpecialAbilityFlag.spellcaster),
			(self.permanent_cloak, Unit.SpecialAbilityFlag.permanent_cloak),
			(self.pickup_item, Unit.SpecialAbilityFlag.pickup_item),
			(self.ignore_supply_check, Unit.SpecialAbilityFlag.ignores_supply_check),
			(self.use_medium_overlays, Unit.SpecialAbilityFlag.use_medium_overlays),
			(self.use_large_overlays, Unit.SpecialAbilityFlag.use_large_overlays),
			(self.battlereactions, Unit.SpecialAbilityFlag.battle_reactions),
			(self.fullautoattack, Unit.SpecialAbilityFlag.full_auto_attack),
			(self.invincible, Unit.SpecialAbilityFlag.invincible),
			(self.mechanical, Unit.SpecialAbilityFlag.mechanical),
			(self.produces_units, Unit.SpecialAbilityFlag.produces_units)
		)
		for (variable, flag) in special_ability_flags_fields:
			if variable.get():
				special_ability_flags |= flag
		if special_ability_flags != entry.special_ability_flags:
			entry.special_ability_flags = special_ability_flags
			edited = True

		if entry.infestation != None and self.infestentry.get() != entry.infestation:
			entry.infestation = self.infestentry.get()
			edited = True
		if self.reqIndex.get() != entry.requirements:
			entry.requirements = self.reqIndex.get()
			edited = True

		return edited
