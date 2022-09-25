
from .DATUnitsTab import DATUnitsTab
from .DataID import DATID

from ..FileFormats.DAT.UnitsDAT import Unit

from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.FloatVar import FloatVar
from ..Utilities.DropDown import DropDown
from ..Utilities.UIKit import *
from ..Utilities.ScrollView import ScrollView
from ..Utilities import Assets

class BasicUnitsTab(DATUnitsTab):
	def __init__(self, parent, toplevel, parent_tab):
		DATUnitsTab.__init__(self, parent, toplevel, parent_tab)
		self.toplevel = toplevel
		scrollview = ScrollView(self)

		self.hit_points_whole = IntegerVar(0,[0,4294967295])
		self.hit_points_fraction = IntegerVar(0,[0,255])
		self.shield_amount = IntegerVar(0,[0,65535])
		self.shield_enabled = IntVar()
		self.armor = IntegerVar(0,[0,255])
		self.armor_upgrade_entry = IntegerVar(0, [0,60])
		self.armor_upgrade = IntVar()

		statframe = Frame(scrollview.content_view)
		l = LabelFrame(statframe, text='Vital Statistics')
		s = Frame(l)
		r = Frame(s)
		f = Frame(r)
		Label(f, text='Hit Points:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.hit_points_whole, font=Font.fixed(), width=10).pack(side=LEFT)
		self.tip(f, 'Hit Points', 'UnitHP')
		f.pack(side=LEFT)
		f = Frame(r)
		Label(f, text='Fraction:', anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.hit_points_fraction, font=Font.fixed(), width=3).pack(side=LEFT)
		self.tip(f, 'Hit Points Fraction', 'UnitHPFraction')
		f.pack(side=LEFT)
		r.pack(fill=X)
		f = Frame(s)
		x = Frame(f)
		Label(x, text='Shields:', width=9, anchor=E).pack(side=LEFT)
		Entry(x, textvariable=self.shield_amount, font=Font.fixed(), width=10).pack(side=LEFT)
		self.tip(x, 'Shields', 'UnitSP')
		x.pack(side=LEFT)
		x = Frame(f)
		Checkbutton(x, text='Enabled', variable=self.shield_enabled).pack(side=LEFT)
		self.tip(x, 'Shields Enabled', 'UnitShieldEnable')
		x.pack(side=LEFT, fill=X)
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Armor:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.armor, font=Font.fixed(), width=10).pack(side=LEFT)
		self.tip(f, 'Armor', 'UnitArmor')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Upgrade:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.armor_upgrade_entry, font=Font.fixed(), width=3).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.armor_upgrade_ddw = DropDown(f, self.armor_upgrade, [], self.armor_upgrade_entry, width=20)
		self.armor_upgrade_ddw.pack(side=LEFT, fill=X, expand=1)
		Button(f, text='Jump ->', command=lambda: self.jump(DATID.upgrades, self.armor_upgrade.get())).pack(side=LEFT)
		self.tip(f, 'Armor Upgrade', 'UnitArmorUpgrade')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X, expand=1)

		self.mineral_cost = IntegerVar(0, [0,65535])
		self.vespene_cost = IntegerVar(0, [0,65535])
		self.build_time = IntegerVar(24, [0,65535], callback=lambda ticks: self.update_time(ticks, self.build_time_seconds))
		self.build_time_seconds = FloatVar(1, [0,65535/24.0], callback=lambda time: self.update_ticks(time, self.build_time), precision=4)
		self.broodwar_unit_flag = IntVar()

		l = LabelFrame(statframe, text='Build Cost')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Minerals:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.mineral_cost, font=Font.fixed(), width=5).pack(side=LEFT)
		self.tip(f, 'Minerals', 'UnitMinerals')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Vespene:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.vespene_cost, font=Font.fixed(), width=5).pack(side=LEFT)
		self.tip(f, 'Vespene', 'UnitVespene')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Time:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.build_time, font=Font.fixed(), width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.build_time_seconds, font=Font.fixed(), width=9).pack(side=LEFT)
		Label(f, text='secs.').pack(side=LEFT)
		self.tip(f, 'Build Time', 'UnitTime')
		f.pack(fill=X)
		c = Checkbutton(s, text='BroodWar', variable=self.broodwar_unit_flag)
		self.tip(c, 'BroodWar', 'UnitIsBW')
		c.pack()
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=BOTH)
		statframe.pack(fill=X)

		self.ground_weapon_entry = IntegerVar(0, [0,130])
		self.ground_weapon_dropdown = IntVar()
		self.max_ground_hits = IntegerVar(0, [0,255])
		self.air_weapon_entry = IntegerVar(0, [0,130])
		self.air_weapon_dropdown = IntVar()
		self.max_air_hits = IntegerVar(0, [0,255])

		l = LabelFrame(scrollview.content_view, text='Weapons')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Ground:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.ground_weapon_entry, font=Font.fixed(), width=3).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.ground_weapon_ddw = DropDown(f, self.ground_weapon_dropdown, [], self.ground_weapon_entry)
		self.ground_weapon_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda: self.jump(DATID.weapons, self.ground_weapon_dropdown.get())).pack(side=LEFT)
		self.tip(f, 'Ground Weapon', 'UnitWeaponGround')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Max Hits:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.max_ground_hits, font=Font.fixed(), width=3).pack(side=LEFT)
		self.tip(f, 'Max Ground Hits', 'UnitGroundMax')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Air:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.air_weapon_entry, font=Font.fixed(), width=3).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.air_weapon_ddw = DropDown(f, self.air_weapon_dropdown, [], self.air_weapon_entry)
		self.air_weapon_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda: self.jump(DATID.weapons, self.air_weapon_dropdown.get())).pack(side=LEFT)
		self.tip(f, 'Air Weapon', 'UnitWeaponAir')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Max Hits:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.max_air_hits, font=Font.fixed(), width=3).pack(side=LEFT)
		self.tip(f, 'Max Air Hits', 'UnitAirMax')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.supply_required = IntegerVar(0, [0,255])
		self.supply_required_half = IntVar()
		self.supply_provided = IntegerVar(0, [0,255])
		self.supply_provided_half = IntVar()
		self.zerg = IntVar()
		self.terran = IntVar()
		self.protoss = IntVar()

		ssframe = Frame(scrollview.content_view)
		l = LabelFrame(ssframe, text='Supply')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Required:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.supply_required, font=Font.fixed(), width=3).pack(side=LEFT)
		Checkbutton(f, text='+0.5', variable=self.supply_required_half).pack(side=LEFT)
		self.tip(f, 'Supply Required', 'UnitSupReq')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Provided:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.supply_provided, font=Font.fixed(), width=3).pack(side=LEFT)
		Checkbutton(f, text='+0.5', variable=self.supply_provided_half).pack(side=LEFT)
		self.tip(f, 'Supply Provided', 'UnitSupProv')
		f.pack(fill=X)
		f = Frame(s)
		c = Checkbutton(f, text='Zerg', variable=self.zerg)
		self.tip(c, 'Zerg', 'UnitSEGroupZerg')
		c.pack(side=LEFT)
		c = Checkbutton(f, text='Terran', variable=self.terran)
		self.tip(c, 'Terran', 'UnitSEGroupTerran')
		c.pack(side=LEFT)
		c = Checkbutton(f, text='Protoss', variable=self.protoss)
		self.tip(c, 'Protoss', 'UnitSEGroupProtoss')
		c.pack(side=LEFT)
		f.pack()
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X, expand=1)

		self.space_required = IntegerVar(0, [0,255])
		self.space_provided = IntegerVar(0, [0,255])

		l = LabelFrame(ssframe, text='Space')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Required:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.space_required, font=Font.fixed(), width=3).pack(side=LEFT)
		self.tip(f, 'Space Required', 'UnitSpaceReq')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Provided:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.space_provided, font=Font.fixed(), width=3).pack(side=LEFT)
		self.tip(f, 'Space Provided', 'UnitSpaceProv')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=BOTH, expand=1)

		self.build_score = IntegerVar(0, [0,65535])
		self.destroy_score = IntegerVar(0, [0,65535])

		l = LabelFrame(ssframe, text='Score')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Build:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.build_score, font=Font.fixed(), width=5).pack(side=LEFT)
		self.tip(f, 'Build Score', 'UnitScoreBuild')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Destroy:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.destroy_score, font=Font.fixed(), width=5).pack(side=LEFT)
		self.tip(f, 'Destroy Score', 'UnitScoreDestroy')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=BOTH, expand=1)
		ssframe.pack(fill=X)

		self.unit_size = IntVar()
		self.sight_range = IntegerVar(0, [0,11])
		self.target_acquisition_range = IntegerVar(0, [0,255])

		otherframe = Frame(scrollview.content_view)
		l = LabelFrame(otherframe, text='Other')
		s = Frame(l)
		t = Frame(s)
		Label(t, text='Unit Size:', anchor=E).pack(side=LEFT)
		DropDown(t, self.unit_size, Assets.data_cache(Assets.DataReference.UnitSize)).pack(side=LEFT, fill=X, expand=1)
		self.tip(t, 'Unit Size', 'UnitSize')
		t.pack(side=LEFT, fill=X, expand=1)
		t = Frame(s)
		Label(t, text='Sight:', anchor=E).pack(side=LEFT)
		Entry(t, textvariable=self.sight_range, font=Font.fixed(), width=2).pack(side=LEFT)
		self.tip(t, 'Sight Range', 'UnitSight')
		t.pack(side=LEFT)
		t = Frame(s)
		Label(t, text='Target Acquisition Range:', anchor=E).pack(side=LEFT)
		Entry(t, textvariable=self.target_acquisition_range, font=Font.fixed(), width=3).pack(side=LEFT)
		self.tip(t, 'Target Acquisition Range', 'UnitTAR')
		t.pack(side=LEFT)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=BOTH, expand=1)
		otherframe.pack(fill=X)

		scrollview.pack(fill=BOTH, expand=1)

	def copy(self):
		text = self.toplevel.data_context.units.dat.export_entry(self.parent_tab.id, export_properties=[
			Unit.Property.hit_points,
			Unit.Property.shield_amount,
			Unit.Property.shield_enabled,
			Unit.Property.armor,
			Unit.Property.armor_upgrade,
			Unit.Property.mineral_cost,
			Unit.Property.vespene_cost,
			Unit.Property.build_time,
			Unit.Property.broodwar_unit_flag,
			Unit.Property.ground_weapon,
			Unit.Property.max_ground_hits,
			Unit.Property.air_weapon,
			Unit.Property.max_air_hits,
			Unit.Property.space_required,
			Unit.Property.space_provided,
			Unit.Property.build_score,
			Unit.Property.destroy_score,
			Unit.Property.unit_size,
			Unit.Property.sight_range,
			Unit.Property.target_acquisition_range,
			Unit.Property.supply_required,
			Unit.Property.supply_provided,
			Unit.Property.staredit_group_flags,
		])
		self.clipboard_set(text)

	def updated_pointer_entries(self, ids):
		if DATID.upgrades in ids:
			self.armor_upgrade_ddw.setentries(self.toplevel.data_context.upgrades.names + ('None',))
		if DATID.weapons in ids:
			self.ground_weapon_ddw.setentries(self.toplevel.data_context.weapons.names + ('None',))
			self.air_weapon_ddw.setentries(self.toplevel.data_context.weapons.names + ('None',))

		if self.toplevel.data_context.settings.settings.get('reference_limits', True):
			if DATID.upgrades in ids:
				self.armor_upgrade_entry.range[1] = self.toplevel.data_context.upgrades.entry_count() - 1
			if DATID.weapons in ids:
				self.ground_weapon_entry.range[1] = self.toplevel.data_context.weapons.entry_count()
				self.air_weapon_entry.range[1] = self.toplevel.data_context.weapons.entry_count()
		else:
			self.armor_upgrade_entry.range[1] = 255
			self.ground_weapon_entry.range[1] = 255
			self.air_weapon_entry.range[1] = 255

	def load_data(self, entry):
		self.hit_points_whole.set(entry.hit_points.whole)
		self.hit_points_fraction.set(entry.hit_points.fraction)
		self.shield_amount.set(entry.shield_amount)
		self.shield_enabled.set(entry.shield_enabled)
		self.armor.set(entry.armor)
		self.armor_upgrade.set(entry.armor_upgrade)
		self.mineral_cost.set(entry.mineral_cost)
		self.vespene_cost.set(entry.vespene_cost)
		self.build_time.set(entry.build_time)
		self.broodwar_unit_flag.set(entry.broodwar_unit_flag)
		self.ground_weapon_entry.set(entry.ground_weapon)
		self.max_ground_hits.set(entry.max_ground_hits)
		self.air_weapon_entry.set(entry.air_weapon)
		self.max_air_hits.set(entry.max_air_hits)
		self.space_required.set(entry.space_required)
		self.space_provided.set(entry.space_provided)
		self.build_score.set(entry.build_score)
		self.destroy_score.set(entry.destroy_score)
		self.unit_size.set(entry.unit_size)
		self.sight_range.set(entry.sight_range)
		self.target_acquisition_range.set(entry.target_acquisition_range)
		self.supply_required.set(entry.supply_required.whole)
		self.supply_required_half.set(entry.supply_required.half)
		self.supply_provided.set(entry.supply_provided.whole)
		self.supply_provided_half.set(entry.supply_provided.half)
		self.zerg.set((entry.staredit_group_flags & Unit.StarEditGroupFlag.zerg) == Unit.StarEditGroupFlag.zerg)
		self.terran.set((entry.staredit_group_flags & Unit.StarEditGroupFlag.terran) == Unit.StarEditGroupFlag.terran)
		self.protoss.set((entry.staredit_group_flags & Unit.StarEditGroupFlag.protoss) == Unit.StarEditGroupFlag.protoss)

	def save_data(self, entry):
		edited = False
		if self.hit_points_whole.get() != entry.hit_points.whole:
			entry.hit_points.whole = self.hit_points_whole.get()
			edited = True
		if self.hit_points_fraction.get() != entry.hit_points.fraction:
			entry.hit_points.fraction = self.hit_points_fraction.get()
			edited = True
		if self.shield_amount.get() != entry.shield_amount:
			entry.shield_amount = self.shield_amount.get()
			edited = True
		if self.shield_enabled.get() != entry.shield_enabled:
			entry.shield_enabled = self.shield_enabled.get()
			edited = True
		if self.armor.get() != entry.armor:
			entry.armor = self.armor.get()
			edited = True
		if self.armor_upgrade.get() != entry.armor_upgrade:
			entry.armor_upgrade = self.armor_upgrade.get()
			edited = True
		if self.mineral_cost.get() != entry.mineral_cost:
			entry.mineral_cost = self.mineral_cost.get()
			edited = True
		if self.vespene_cost.get() != entry.vespene_cost:
			entry.vespene_cost = self.vespene_cost.get()
			edited = True
		if self.build_time.get() != entry.build_time:
			entry.build_time = self.build_time.get()
			edited = True
		if self.broodwar_unit_flag.get() != entry.broodwar_unit_flag:
			entry.broodwar_unit_flag = self.broodwar_unit_flag.get()
			edited = True
		if self.ground_weapon_entry.get() != entry.ground_weapon:
			entry.ground_weapon = self.ground_weapon_entry.get()
			edited = True
		if self.max_ground_hits.get() != entry.max_ground_hits:
			entry.max_ground_hits = self.max_ground_hits.get()
			edited = True
		if self.air_weapon_entry.get() != entry.air_weapon:
			entry.air_weapon = self.air_weapon_entry.get()
			edited = True
		if self.max_air_hits.get() != entry.max_air_hits:
			entry.max_air_hits = self.max_air_hits.get()
			edited = True
		if self.space_required.get() != entry.space_required:
			entry.space_required = self.space_required.get()
			edited = True
		if self.space_provided.get() != entry.space_provided:
			entry.space_provided = self.space_provided.get()
			edited = True
		if self.build_score.get() != entry.build_score:
			entry.build_score = self.build_score.get()
			edited = True
		if self.destroy_score.get() != entry.destroy_score:
			entry.destroy_score = self.destroy_score.get()
			edited = True
		if self.unit_size.get() != entry.unit_size:
			entry.unit_size = self.unit_size.get()
			edited = True
		if self.sight_range.get() != entry.sight_range:
			entry.sight_range = self.sight_range.get()
			edited = True
		if self.target_acquisition_range.get() != entry.target_acquisition_range:
			entry.target_acquisition_range = self.target_acquisition_range.get()
			edited = True
		if self.supply_required.get() != entry.supply_required.whole:
			entry.supply_required.whole = self.supply_required.get()
			edited = True
		if self.supply_required_half.get() != entry.supply_required.half:
			entry.supply_required.half = self.supply_required_half.get()
			edited = True
		if self.supply_provided.get() != entry.supply_provided.whole:
			entry.supply_provided.whole = self.supply_provided.get()
			edited = True
		if self.supply_provided_half.get() != entry.supply_provided.half:
			entry.supply_provided.half = self.supply_provided_half.get()
			edited = True
		staredit_group_flags = entry.staredit_group_flags & Unit.StarEditGroupFlag.GROUP_FLAGS
		if self.zerg.get():
			staredit_group_flags |= Unit.StarEditGroupFlag.zerg
		if self.terran.get():
			staredit_group_flags |= Unit.StarEditGroupFlag.terran
		if self.protoss.get():
			staredit_group_flags |= Unit.StarEditGroupFlag.protoss
		if staredit_group_flags != entry.staredit_group_flags:
			entry.staredit_group_flags = staredit_group_flags
			edited = True
		return edited
	