
from __future__ import annotations

from .DATUnitsTab import DATUnitsTab
from ...DataID import DataID, AnyID

from ....FileFormats.DAT.UnitsDAT import DATUnit

from ....Utilities import UIKit as UI

from math import floor, ceil

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ...Delegates import MainDelegate, SubDelegate

class StarEditUnitsTab(DATUnitsTab):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, sub_delegate: SubDelegate) -> None:
		DATUnitsTab.__init__(self, parent, delegate, sub_delegate)
		scrollview = UI.ScrollView(self)

		self.nonneutral = UI.IntVar()
		self.unitlisting = UI.IntVar()
		self.missionbriefing = UI.IntVar()
		self.playersettings = UI.IntVar()
		self.allraces = UI.IntVar()
		self.setdoodadstate = UI.IntVar()
		self.nonlocationtriggers = UI.IntVar()
		self.unitherosettings = UI.IntVar()
		self.locationtriggers = UI.IntVar()
		self.broodwaronly = UI.IntVar()
		self.men = UI.IntVar()
		self.building = UI.IntVar()
		self.factory = UI.IntVar()
		self.independent = UI.IntVar()
		self.neutral = UI.IntVar()

		flags = [
			(
				'Availability',
				[
					[
						('Non-Neutral', self.nonneutral, 'UnitSENonNeutral'),
						('Unit Listing&Palette', self.unitlisting, 'UnitSEListing'),
						('Mission Briefing', self.missionbriefing, 'UnitSEBriefing'),
						('Player Settings', self.playersettings, 'UnitSEPlayerSet'),
						('All Races', self.allraces, 'UnitSEAllRaces'),
						('Set Doodad State', self.setdoodadstate, 'UnitSEDoodadState'),
						('Non-Location Triggers', self.nonlocationtriggers, 'UnitSENonLoc'),
						('Unit&Hero Settings', self.unitherosettings, 'UnitSEUnitHero'),
					],[
						('Location Triggers', self.locationtriggers, 'UnitSELoc'),
						('BroodWar Only', self.broodwaronly, 'UnitSEBW'),
					],
				],
			),(
				'Group',
				[
					[
						('Men', self.men, 'UnitSEGroupMen'),
						('Building', self.building, 'UnitSEGroupBuilding'),
						('Factory', self.factory, 'UnitSEGroupFactory'),
						('Independent', self.independent, 'UnitSEGroupInd'),
						('Neutral', self.neutral, 'UnitSEGroupNeutral'),
					],
				],
			)
		]
		top = UI.Frame(scrollview.content_view)
		for lt,lf in flags:
			l = UI.LabelFrame(top, text=lt + ' Flags:')
			s = UI.Frame(l)
			for c in lf:
				cc = UI.Frame(s, width=20)
				for t,v,h in c:
					f = UI.Frame(cc)
					self.makeCheckbox(f, v, t, h).pack(side=UI.LEFT)
					f.pack(fill=UI.X)
				cc.pack(side=UI.LEFT, fill=UI.Y)
			s.pack(fill=UI.BOTH, padx=5, pady=5)
			l.pack(side=UI.LEFT, fill=UI.BOTH, expand=(lt == 'Availability'))
		top.pack(fill=UI.X)

		self.rankentry = UI.IntegerVar(0, [0,0])
		self.rankdd = UI.IntVar()
		self.mapstring = UI.IntegerVar(0, [0,65535])

		l = UI.LabelFrame(scrollview.content_view, text='String Properties:')
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='Rank/Sublabel:', width=13, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.rankentry, font=UI.Font.fixed(), width=3).pack(side=UI.LEFT)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.ranks = UI.DropDown(f, self.rankdd, [], self.rankentry)
		self.ranks.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.tip(f, 'Rank/Sublabel', 'UnitRank')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Map String:', width=13, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.mapstring, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Map String', 'UnitMapString')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(fill=UI.X)

		self.width = UI.IntegerVar(0, [0,65535])
		self.height = UI.IntegerVar(0, [0,65535])
		self.showpreview = UI.BooleanVar()
		self.showpreview.set(self.delegate.data_context.config.preview.staredit.show.value)

		bottom = UI.Frame(scrollview.content_view)
		r = UI.Frame(bottom)
		l = UI.LabelFrame(r, text='Placement Box (Pixels):')
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='Width:', width=13, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.width, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Placement Width', 'UnitSEPlaceWidth')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Height:', width=13, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.height, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		self.tip(f, 'Placement Height', 'UnitSEPlaceHeight')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(side=UI.TOP)
		r.pack(side=UI.LEFT, fill=UI.Y)
		l = UI.LabelFrame(bottom, text='Preview:')
		self.preview = UI.Canvas(l, width=257, height=257, background='#000000', theme_tag='preview') # type: ignore[call-arg]
		self.preview.pack(side=UI.TOP)

		self.place_item = self.preview.create_rectangle(0, 0, 0, 0, outline='#FF0000')

		UI.Checkbutton(l, text='Show Preview', variable=self.showpreview, command=self.drawpreview).pack(side=UI.TOP)
		l.pack(side=UI.LEFT)
		bottom.pack(fill=UI.X)

		scrollview.pack(fill=UI.BOTH, expand=1)

		for var in (self.width, self.height):
			var.trace_add('write', lambda *_: self.drawpreview())

	def copy(self) -> None:
		if not self.delegate.data_context.units.dat:
			return
		text = self.delegate.data_context.units.dat.export_entry(self.sub_delegate.id, export_properties=[
			DATUnit.Property.staredit_group_flags,
			DATUnit.Property.staredit_availability_flags,
			DATUnit.Property.sublabel,
			DATUnit.Property.unit_map_string,
			DATUnit.Property.staredit_placement_size,
		])
		self.clipboard_set(text) # type: ignore[attr-defined]

	def updated_pointer_entries(self, ids: list[AnyID]) -> None:
		if DataID.stat_txt in ids:
			count = min(255,len(self.delegate.data_context.stat_txt.strings)-1302)
			ranks = ('No Sublabel',) + self.delegate.data_context.stat_txt.strings[1302:1302+count]
			self.ranks.setentries(ranks)
			self.rankentry.range[1] = count
			self.rankentry.editvalue()

	def drawboxes(self) -> None:
		if self.showpreview.get():
			w = self.width.get() // 2
			h = self.height.get() // 2
			self.place_item.coords(130-floor(w), 130-floor(h), 129+ceil(w), 129+ceil(h))
			self.place_item.tag_raise()
		else:
			self.place_item.coords(0, 0, 0, 0)

	def draw_image(self, image_id: int, tag: str, x: int = 130, y: int = 130) -> None:
		frame = self.delegate.data_context.get_image_frame(image_id)
		if frame:
			self.preview.create_image(x, y, image=frame[0], tags=tag)

	def drawpreview(self) -> None:
		if not self.delegate.data_context.units.dat or not self.delegate.data_context.flingy.dat or not self.delegate.data_context.sprites.dat:
			return
		self.preview.delete('unit')
		if self.showpreview.get():
			entry = self.delegate.data_context.units.dat.get_entry(self.sub_delegate.id)
			flingy = self.delegate.data_context.flingy.dat.get_entry(entry.graphics)
			sprite = self.delegate.data_context.sprites.dat.get_entry(flingy.sprite)
			self.draw_image(sprite.image, 'unit')
		self.drawboxes()

	def load_data(self, entry: DATUnit) -> None:
		self.men.set(entry.staredit_group_flags & DATUnit.StarEditGroupFlag.men == DATUnit.StarEditGroupFlag.men)
		self.building.set(entry.staredit_group_flags & DATUnit.StarEditGroupFlag.building == DATUnit.StarEditGroupFlag.building)
		self.factory.set(entry.staredit_group_flags & DATUnit.StarEditGroupFlag.factory == DATUnit.StarEditGroupFlag.factory)
		self.independent.set(entry.staredit_group_flags & DATUnit.StarEditGroupFlag.independent == DATUnit.StarEditGroupFlag.independent)
		self.neutral.set(entry.staredit_group_flags & DATUnit.StarEditGroupFlag.neutral == DATUnit.StarEditGroupFlag.neutral)

		self.nonneutral.set(entry.staredit_availability_flags & DATUnit.StarEditAvailabilityFlag.non_neutral == DATUnit.StarEditAvailabilityFlag.non_neutral)
		self.unitlisting.set(entry.staredit_availability_flags & DATUnit.StarEditAvailabilityFlag.unit_listing == DATUnit.StarEditAvailabilityFlag.unit_listing)
		self.missionbriefing.set(entry.staredit_availability_flags & DATUnit.StarEditAvailabilityFlag.mission_briefing == DATUnit.StarEditAvailabilityFlag.mission_briefing)
		self.playersettings.set(entry.staredit_availability_flags & DATUnit.StarEditAvailabilityFlag.player_settings == DATUnit.StarEditAvailabilityFlag.player_settings)
		self.allraces.set(entry.staredit_availability_flags & DATUnit.StarEditAvailabilityFlag.all_races == DATUnit.StarEditAvailabilityFlag.all_races)
		self.setdoodadstate.set(entry.staredit_availability_flags & DATUnit.StarEditAvailabilityFlag.set_doodad_state == DATUnit.StarEditAvailabilityFlag.set_doodad_state)
		self.nonlocationtriggers.set(entry.staredit_availability_flags & DATUnit.StarEditAvailabilityFlag.non_location_triggers == DATUnit.StarEditAvailabilityFlag.non_location_triggers)
		self.unitherosettings.set(entry.staredit_availability_flags & DATUnit.StarEditAvailabilityFlag.unit_hero_settings == DATUnit.StarEditAvailabilityFlag.unit_hero_settings)
		self.locationtriggers.set(entry.staredit_availability_flags & DATUnit.StarEditAvailabilityFlag.location_triggers == DATUnit.StarEditAvailabilityFlag.location_triggers)
		self.broodwaronly.set(entry.staredit_availability_flags & DATUnit.StarEditAvailabilityFlag.broodwar_only == DATUnit.StarEditAvailabilityFlag.broodwar_only)

		self.rankentry.set(entry.sublabel)
		self.mapstring.set(entry.unit_map_string)
		self.width.set(entry.staredit_placement_size.width)
		self.height.set(entry.staredit_placement_size.height)

		self.drawpreview()

	def save_data(self, entry: DATUnit) -> bool:
		edited = False

		staredit_group_flags = entry.staredit_group_flags & DATUnit.StarEditGroupFlag.RACE_FLAGS
		staredit_group_flags_fields = (
			(self.men, DATUnit.StarEditGroupFlag.men),
			(self.building, DATUnit.StarEditGroupFlag.building),
			(self.factory, DATUnit.StarEditGroupFlag.factory),
			(self.independent, DATUnit.StarEditGroupFlag.independent),
			(self.neutral, DATUnit.StarEditGroupFlag.neutral)
		)
		for variable,flag in staredit_group_flags_fields:
			if variable.get():
				staredit_group_flags |= flag
		if staredit_group_flags != entry.staredit_group_flags:
			entry.staredit_group_flags = staredit_group_flags
			edited = True

		staredit_availability_flags = entry.staredit_availability_flags & ~DATUnit.StarEditAvailabilityFlag.ALL_FLAGS
		staredit_availability_flags_fields = (
			(self.nonneutral, DATUnit.StarEditAvailabilityFlag.non_neutral),
			(self.unitlisting, DATUnit.StarEditAvailabilityFlag.unit_listing),
			(self.missionbriefing, DATUnit.StarEditAvailabilityFlag.mission_briefing),
			(self.playersettings, DATUnit.StarEditAvailabilityFlag.player_settings),
			(self.allraces, DATUnit.StarEditAvailabilityFlag.all_races),
			(self.setdoodadstate, DATUnit.StarEditAvailabilityFlag.set_doodad_state),
			(self.nonlocationtriggers, DATUnit.StarEditAvailabilityFlag.non_location_triggers),
			(self.unitherosettings, DATUnit.StarEditAvailabilityFlag.unit_hero_settings),
			(self.locationtriggers, DATUnit.StarEditAvailabilityFlag.location_triggers),
			(self.broodwaronly, DATUnit.StarEditAvailabilityFlag.broodwar_only),
		)
		for variable,flag in staredit_availability_flags_fields:
			if variable.get():
				staredit_availability_flags |= flag
		if staredit_availability_flags != entry.staredit_availability_flags:
			entry.staredit_availability_flags = staredit_availability_flags
			edited = True

		if self.rankentry.get() != entry.sublabel:
			entry.sublabel = self.rankentry.get()
			edited = True
		if self.mapstring.get() != entry.unit_map_string:
			entry.unit_map_string = self.mapstring.get()
			edited = True
		if self.width.get() != entry.staredit_placement_size.width:
			entry.staredit_placement_size.width = self.width.get()
			edited = True
		if self.height.get() != entry.staredit_placement_size.height:
			entry.staredit_placement_size.height = self.height.get()
			edited = True

		self.delegate.data_context.config.preview.staredit.show.value = self.showpreview.get()
		return edited
