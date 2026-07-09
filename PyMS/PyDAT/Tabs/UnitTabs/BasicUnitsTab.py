
from __future__ import annotations

from .DATUnitsTab import DATUnitsTab
from ...DataID import DATID, AnyID

from ....FileFormats.DAT.UnitsDAT import DATUnit

from ....Utilities import UIKit as UI
from ....Utilities import Assets

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ...Delegates import MainDelegate, SubDelegate

class BasicUnitsTab(DATUnitsTab):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, sub_delegate: SubDelegate) -> None:
		DATUnitsTab.__init__(self, parent, delegate, sub_delegate)
		scrollview = UI.ScrollView(self)

		self.hit_points_whole = UI.IntegerVar(0,[0,4294967295])
		self.hit_points_fraction = UI.IntegerVar(0,[0,255])
		self.shield_amount = UI.IntegerVar(0,[0,65535])
		self.shield_enabled = UI.IntVar()
		self.armor = UI.IntegerVar(0,[0,255])
		self.armor_upgrade_entry = UI.IntegerVar(0, [0,60])
		self.armor_upgrade = UI.IntVar()

		statframe = UI.Frame(scrollview.content_view)
		l = UI.LabelFrame(statframe, text='Vital Statistics')
		s = UI.Frame(l)
		r = UI.Frame(s)
		f = UI.Frame(r)
		UI.Label(f, text='Hit Points:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.hit_points_whole, font=UI.Font.fixed(), width=10).pack(side=UI.LEFT)
		self.tip(f, 'Hit Points', 'UnitHP')
		f.pack(side=UI.LEFT)
		f = UI.Frame(r)
		UI.Label(f, text='Fraction:', anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.hit_points_fraction, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		self.tip(f, 'Hit Points Fraction', 'UnitHPFraction')
		f.pack(side=UI.LEFT)
		r.pack(fill=UI.X)
		f = UI.Frame(s)
		x = UI.Frame(f)
		UI.Label(x, text='Shields:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(x, textvariable=self.shield_amount, font=UI.Font.fixed(), width=10).pack(side=UI.LEFT)
		self.tip(x, 'Shields', 'UnitSP')
		x.pack(side=UI.LEFT)
		x = UI.Frame(f)
		UI.Checkbutton(x, text='Enabled', variable=self.shield_enabled).pack(side=UI.LEFT)
		self.tip(x, 'Shields Enabled', 'UnitShieldEnable')
		x.pack(side=UI.LEFT, fill=UI.X)
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Armor:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.armor, font=UI.Font.fixed(), width=10).pack(side=UI.LEFT)
		self.tip(f, 'Armor', 'UnitArmor')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Upgrade:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.armor_upgrade_entry, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.armor_upgrade_ddw = UI.DropDown(f, self.armor_upgrade, [], self.armor_upgrade_entry, width=20)
		self.armor_upgrade_ddw.pack(side=UI.LEFT, fill=UI.X, expand=1)
		UI.Button(f, text='Jump ->', command=lambda: self.jump(DATID.upgrades, self.armor_upgrade.get())).pack(side=UI.LEFT)
		self.tip(f, 'Armor Upgrade', 'UnitArmorUpgrade')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(side=UI.LEFT, fill=UI.X, expand=1)

		self.mineral_cost = UI.IntegerVar(0, [0,65535])
		self.vespene_cost = UI.IntegerVar(0, [0,65535])
		self.build_time = UI.IntegerVar(24, [0,65535])
		self.build_time_seconds = UI.FloatVar(1, [0,65535/24.0], callback=lambda time: self.update_ticks(time, self.build_time), precision=4)
		self.build_time.callback = lambda ticks: self.update_time(ticks, self.build_time_seconds)
		self.broodwar_unit_flag = UI.IntVar()

		l = UI.LabelFrame(statframe, text='Build Cost')
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='Minerals:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.mineral_cost, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Minerals', 'UnitMinerals')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Vespene:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.vespene_cost, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Vespene', 'UnitVespene')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Time:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.build_time, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.build_time_seconds, font=UI.Font.fixed(), width=9).pack(side=UI.LEFT)
		UI.Label(f, text='secs.').pack(side=UI.LEFT)
		self.tip(f, 'Build Time', 'UnitTime')
		f.pack(fill=UI.X)
		c = UI.Checkbutton(s, text='BroodWar', variable=self.broodwar_unit_flag)
		self.tip(c, 'BroodWar', 'UnitIsBW')
		c.pack()
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(side=UI.LEFT, fill=UI.BOTH)
		statframe.pack(fill=UI.X)

		self.ground_weapon_entry = UI.IntegerVar(0, [0,130])
		self.ground_weapon_dropdown = UI.IntVar()
		self.max_ground_hits = UI.IntegerVar(0, [0,255])
		self.air_weapon_entry = UI.IntegerVar(0, [0,130])
		self.air_weapon_dropdown = UI.IntVar()
		self.max_air_hits = UI.IntegerVar(0, [0,255])

		l = UI.LabelFrame(scrollview.content_view, text='Weapons')
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='Ground:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.ground_weapon_entry, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.ground_weapon_ddw = UI.DropDown(f, self.ground_weapon_dropdown, [], self.ground_weapon_entry)
		self.ground_weapon_ddw.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		UI.Button(f, text='Jump ->', command=lambda: self.jump(DATID.weapons, self.ground_weapon_dropdown.get())).pack(side=UI.LEFT)
		self.tip(f, 'Ground Weapon', 'UnitWeaponGround')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Max Hits:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.max_ground_hits, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		self.tip(f, 'Max Ground Hits', 'UnitGroundMax')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Air:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.air_weapon_entry, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.air_weapon_ddw = UI.DropDown(f, self.air_weapon_dropdown, [], self.air_weapon_entry)
		self.air_weapon_ddw.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		UI.Button(f, text='Jump ->', command=lambda: self.jump(DATID.weapons, self.air_weapon_dropdown.get())).pack(side=UI.LEFT)
		self.tip(f, 'Air Weapon', 'UnitWeaponAir')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Max Hits:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.max_air_hits, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		self.tip(f, 'Max Air Hits', 'UnitAirMax')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(fill=UI.X)

		self.supply_required = UI.IntegerVar(0, [0,255])
		self.supply_required_half = UI.BooleanVar()
		self.supply_provided = UI.IntegerVar(0, [0,255])
		self.supply_provided_half = UI.BooleanVar()
		self.zerg = UI.IntVar()
		self.terran = UI.IntVar()
		self.protoss = UI.IntVar()

		ssframe = UI.Frame(scrollview.content_view)
		l = UI.LabelFrame(ssframe, text='Supply')
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='Required:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.supply_required, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		UI.Checkbutton(f, text='+0.5', variable=self.supply_required_half).pack(side=UI.LEFT)
		self.tip(f, 'Supply Required', 'UnitSupReq')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Provided:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.supply_provided, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		UI.Checkbutton(f, text='+0.5', variable=self.supply_provided_half).pack(side=UI.LEFT)
		self.tip(f, 'Supply Provided', 'UnitSupProv')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		c = UI.Checkbutton(f, text='Zerg', variable=self.zerg)
		self.tip(c, 'Zerg', 'UnitSEGroupZerg')
		c.pack(side=UI.LEFT)
		c = UI.Checkbutton(f, text='Terran', variable=self.terran)
		self.tip(c, 'Terran', 'UnitSEGroupTerran')
		c.pack(side=UI.LEFT)
		c = UI.Checkbutton(f, text='Protoss', variable=self.protoss)
		self.tip(c, 'Protoss', 'UnitSEGroupProtoss')
		c.pack(side=UI.LEFT)
		f.pack()
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(side=UI.LEFT, fill=UI.X, expand=1)

		self.space_required = UI.IntegerVar(0, [0,255])
		self.space_provided = UI.IntegerVar(0, [0,255])

		l = UI.LabelFrame(ssframe, text='Space')
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='Required:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.space_required, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		self.tip(f, 'Space Required', 'UnitSpaceReq')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Provided:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.space_provided, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		self.tip(f, 'Space Provided', 'UnitSpaceProv')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(side=UI.LEFT, fill=UI.BOTH, expand=1)

		self.build_score = UI.IntegerVar(0, [0,65535])
		self.destroy_score = UI.IntegerVar(0, [0,65535])

		l = UI.LabelFrame(ssframe, text='Score')
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='Build:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.build_score, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Build Score', 'UnitScoreBuild')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Destroy:', width=9, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.destroy_score, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Destroy Score', 'UnitScoreDestroy')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(side=UI.LEFT, fill=UI.BOTH, expand=1)
		ssframe.pack(fill=UI.X)

		self.unit_size = UI.IntVar()
		self.sight_range = UI.IntegerVar(0, [0,11])
		self.target_acquisition_range = UI.IntegerVar(0, [0,255])

		otherframe = UI.Frame(scrollview.content_view)
		l = UI.LabelFrame(otherframe, text='Other')
		s = UI.Frame(l)
		t = UI.Frame(s)
		UI.Label(t, text='Unit Size:', anchor=UI.E).pack(side=UI.LEFT)
		UI.DropDown(t, self.unit_size, Assets.data_cache(Assets.DataReference.UnitSize)).pack(side=UI.LEFT, fill=UI.X, expand=1)
		self.tip(t, 'Unit Size', 'UnitSize')
		t.pack(side=UI.LEFT, fill=UI.X, expand=1)
		t = UI.Frame(s)
		UI.Label(t, text='Sight:', anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(t, textvariable=self.sight_range, font=UI.Font.fixed(), width=2).pack(side=UI.LEFT)
		self.tip(t, 'Sight Range', 'UnitSight')
		t.pack(side=UI.LEFT)
		t = UI.Frame(s)
		UI.Label(t, text='Target Acquisition Range:', anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(t, textvariable=self.target_acquisition_range, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		self.tip(t, 'Target Acquisition Range', 'UnitTAR')
		t.pack(side=UI.LEFT)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(side=UI.LEFT, fill=UI.BOTH, expand=1)
		otherframe.pack(fill=UI.X)

		scrollview.pack(fill=UI.BOTH, expand=1)

	def copy(self) -> None:
		if not self.delegate.data_context.units.dat:
			return
		text = self.delegate.data_context.units.dat.export_entry(self.sub_delegate.id, export_properties=[
			DATUnit.Property.hit_points,
			DATUnit.Property.shield_amount,
			DATUnit.Property.shield_enabled,
			DATUnit.Property.armor,
			DATUnit.Property.armor_upgrade,
			DATUnit.Property.mineral_cost,
			DATUnit.Property.vespene_cost,
			DATUnit.Property.build_time,
			DATUnit.Property.broodwar_unit_flag,
			DATUnit.Property.ground_weapon,
			DATUnit.Property.max_ground_hits,
			DATUnit.Property.air_weapon,
			DATUnit.Property.max_air_hits,
			DATUnit.Property.space_required,
			DATUnit.Property.space_provided,
			DATUnit.Property.build_score,
			DATUnit.Property.destroy_score,
			DATUnit.Property.unit_size,
			DATUnit.Property.sight_range,
			DATUnit.Property.target_acquisition_range,
			DATUnit.Property.supply_required,
			DATUnit.Property.supply_provided,
			DATUnit.Property.staredit_group_flags,
		])
		self.clipboard_set(text) # type: ignore[attr-defined]

	def updated_pointer_entries(self, ids: list[AnyID]) -> None:
		if DATID.upgrades in ids:
			self.armor_upgrade_ddw.setentries(self.delegate.data_context.upgrades.names + ('None',))
		if DATID.weapons in ids:
			self.ground_weapon_ddw.setentries(self.delegate.data_context.weapons.names + ('None',))
			self.air_weapon_ddw.setentries(self.delegate.data_context.weapons.names + ('None',))

		if self.delegate.data_context.config.settings.reference_limits.value:
			if DATID.upgrades in ids:
				self.armor_upgrade_entry.range[1] = self.delegate.data_context.upgrades.entry_count() - 1
			if DATID.weapons in ids:
				self.ground_weapon_entry.range[1] = self.delegate.data_context.weapons.entry_count()
				self.air_weapon_entry.range[1] = self.delegate.data_context.weapons.entry_count()
		else:
			self.armor_upgrade_entry.range[1] = 255
			self.ground_weapon_entry.range[1] = 255
			self.air_weapon_entry.range[1] = 255

	def load_data(self, entry: DATUnit) -> None:
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
		self.zerg.set((entry.staredit_group_flags & DATUnit.StarEditGroupFlag.zerg) == DATUnit.StarEditGroupFlag.zerg)
		self.terran.set((entry.staredit_group_flags & DATUnit.StarEditGroupFlag.terran) == DATUnit.StarEditGroupFlag.terran)
		self.protoss.set((entry.staredit_group_flags & DATUnit.StarEditGroupFlag.protoss) == DATUnit.StarEditGroupFlag.protoss)

	def save_data(self, entry: DATUnit) -> bool:
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
		staredit_group_flags = entry.staredit_group_flags & DATUnit.StarEditGroupFlag.GROUP_FLAGS
		if self.zerg.get():
			staredit_group_flags |= DATUnit.StarEditGroupFlag.zerg
		if self.terran.get():
			staredit_group_flags |= DATUnit.StarEditGroupFlag.terran
		if self.protoss.get():
			staredit_group_flags |= DATUnit.StarEditGroupFlag.protoss
		if staredit_group_flags != entry.staredit_group_flags:
			entry.staredit_group_flags = staredit_group_flags
			edited = True
		return edited
