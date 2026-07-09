
from __future__ import annotations

from .DATTab import DATTab
from ..DataID import DATID, DataID, UnitsTabID, AnyID
from ..DATRef import DATRefs, DATRef

from ...FileFormats.DAT import DATUnit, DATSprite, DATImage

from ...Utilities import UIKit as UI
from ...Utilities import Assets

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

class ImagesTab(DATTab[DATImage]):
	DAT_ID = DATID.images

	def __init__(self, parent: UI.Misc, delegate: MainDelegate) -> None:
		DATTab.__init__(self, parent, delegate)
		scrollview = UI.ScrollView(self)

		self.grpentry = UI.IntegerVar(0, [0, 0])
		self.grpdd = UI.IntVar()
		self.iscriptentry = UI.IntegerVar(0, [0, 0])
		self.iscriptdd = UI.IntVar()

		l = UI.LabelFrame(scrollview.content_view, text='Image:')
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='GRP:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.grpentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT, padx=2)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.grps = UI.DropDown(f, self.grpdd, [], self.grpentry, width=30)
		self.grpdds = [(self.grps,self.grpentry)]
		self.grps.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		def check_grp_ref() -> None:
			grp_id = self.grpdd.get()
			refs = (
				DATRefs(DATID.images, lambda image: (
					DATRef('GRP File', cast(DATImage, image).grp_file),
				)),
			)
			self.check_used_by_references(grp_id, refs, force_open=True)
		UI.Button(f, text='Check', command=check_grp_ref).pack(side=UI.LEFT, padx=2)
		self.tip(f, 'GRP File', 'ImgGRP')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Iscript ID:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.iscriptentry, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT, padx=2)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		self.iscripts = UI.DropDown(f, self.iscriptdd, [], self.iscriptentry, width=30)
		self.iscripts.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		def check_iscript_ref() -> None:
			iscript_id = self.iscriptdd.get()
			refs = (
				DATRefs(DATID.images, lambda image: (
					DATRef('IScript ID', cast(DATImage, image).iscript_id),
				)),
			)
			self.check_used_by_references(iscript_id, refs, force_open=True)
		UI.Button(f, text='Check', command=check_iscript_ref).pack(side=UI.LEFT, padx=2)
		self.tip(f, 'Iscript ID', 'ImgIscriptID')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(fill=UI.X)

		self.graphicsturns = UI.IntVar()
		self.drawifcloaked = UI.IntVar()
		self.clickable = UI.IntVar()
		self.usefulliscript = UI.IntVar()

		p = UI.Frame(scrollview.content_view)
		l = UI.LabelFrame(p, text='General Properties:')
		s = UI.Frame(l)
		ls = UI.Frame(s)
		f = UI.Frame(ls)
		UI.Checkbutton(f, text='Graphics Turns', variable=self.graphicsturns).pack(side=UI.LEFT)
		self.tip(f, 'Graphics Turns', 'ImgGfxTurns')
		f.pack(fill=UI.X)
		f = UI.Frame(ls)
		UI.Checkbutton(f, text='Draw If Cloaked', variable=self.drawifcloaked).pack(side=UI.LEFT)
		self.tip(f, 'Draw If Cloaked', 'ImgDrawCloaked')
		f.pack(fill=UI.X)
		ls.pack(side=UI.LEFT)
		ls = UI.Frame(s)
		f = UI.Frame(ls)
		UI.Checkbutton(f, text='Clickable', variable=self.clickable).pack(side=UI.LEFT)
		self.tip(f, 'Clickable', 'ImgClickable')
		f.pack(fill=UI.X)
		f = UI.Frame(ls)
		UI.Checkbutton(f, text='Use Full Iscript', variable=self.usefulliscript).pack(side=UI.LEFT)
		self.tip(f, 'Use Full Iscript', 'ImgUseFullIscript')
		f.pack(fill=UI.X)
		ls.pack(side=UI.LEFT)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(side=UI.LEFT, fill=UI.X)

		self.functionentry = UI.IntegerVar(0, [0,17])
		self.functiondd = UI.IntVar()
		self.remapentry = UI.IntegerVar(0, [0,9])
		self.remapdd = UI.IntVar()

		l = UI.LabelFrame(p, text='Drawing Properties:')
		s = UI.Frame(l)
		f = UI.Frame(s)
		UI.Label(f, text='Function:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.functionentry, font=UI.Font.fixed(), width=2).pack(side=UI.LEFT, padx=2)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		UI.DropDown(f, self.functiondd, Assets.data_cache(Assets.DataReference.DrawList), self.functionentry, width=15).pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.tip(f, 'Drawing Function', 'ImgDrawFunction')
		f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='Remapping:', width=12, anchor=UI.E).pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.remapentry, font=UI.Font.fixed(), width=2).pack(side=UI.LEFT, padx=2)
		UI.Label(f, text='=').pack(side=UI.LEFT)
		UI.DropDown(f, self.remapdd, Assets.data_cache(Assets.DataReference.Remapping), self.remapentry, width=15).pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
		self.tip(f, 'Remapping', 'ImgRemap')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(side=UI.LEFT, fill=UI.X)
		p.pack(fill=UI.X)

		self.attackentry = UI.IntegerVar(0, [0, 929])
		self.attackdd = UI.IntVar()
		self.damageentry = UI.IntegerVar(0, [0, 929])
		self.damagedd = UI.IntVar()
		self.specialentry = UI.IntegerVar(0, [0, 929])
		self.specialdd = UI.IntVar()
		self.landingentry = UI.IntegerVar(0, [0, 929])
		self.landingdd = UI.IntVar()
		self.liftoffentry = UI.IntegerVar(0, [0, 929])
		self.liftoffdd = UI.IntVar()
		self.shieldentry = UI.IntegerVar(0, [0, 929])
		self.shielddd = UI.IntVar()
		self.shieldsizes = UI.IntVar()

		ols = [
			('Attack', self.attackentry, self.attackdd, 'OL1'),
			('Damage', self.damageentry, self.damagedd, 'OL2'),
			('Special', self.specialentry, self.specialdd, 'OL3'),
			('Landing Dust', self.landingentry, self.landingdd, 'OL4'),
			('Lift-Off Dust', self.liftoffentry, self.liftoffdd, 'OL5'),
			('Shield', self.shieldentry, self.shielddd, 'Shield'),
		]
		l = UI.LabelFrame(scrollview.content_view, text='Extra Overlay Placements:')
		s = UI.Frame(l)
		for t,e,d,h in ols:
			f = UI.Frame(s)
			UI.Label(f, text=t + ':', width=12, anchor=UI.E).pack(side=UI.LEFT)
			UI.Entry(f, textvariable=e, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT, padx=2)
			UI.Label(f, text='=').pack(side=UI.LEFT)
			dd = UI.DropDown(f, d, [], e, width=15)
			dd.pack(side=UI.LEFT, fill=UI.X, expand=1, padx=2)
			self.grpdds.append((dd,e))
			self.tip(f, t + ' Overlay', 'Img' + h)
			f.pack(fill=UI.X)
		f = UI.Frame(s)
		UI.Label(f, text='', width=12).pack(side=UI.LEFT)
		self.sizedd = UI.DropDown(f, self.shieldsizes, Assets.data_cache(Assets.DataReference.ShieldSize), self.shieldupdate, width=6)
		self.sizedd.pack(side=UI.LEFT, padx=2)
		self.tip(f, 'Shield Overlay', 'ImgShield')
		f.pack(fill=UI.X)
		s.pack(fill=UI.BOTH, padx=5, pady=5)
		l.pack(fill=UI.X)

		self.previewing: int | None = None
		self.showpreview = UI.BooleanVar()
		self.showpreview.set(self.delegate.data_context.config.preview.image.show.value)

		x = UI.Frame(scrollview.content_view)
		l = UI.LabelFrame(x, text='Preview:')
		s = UI.Frame(l)
		self.preview = UI.Canvas(s, width=257, height=257, background='#000000', theme_tag='preview') # type: ignore[call-arg]
		self.preview.pack()
		UI.Checkbutton(s, text='Show Preview', variable=self.showpreview, command=self.drawpreview).pack()
		s.pack()
		l.pack(side=UI.LEFT)
		x.pack(fill=UI.X)
		scrollview.pack(fill=UI.BOTH, expand=1)

		self.setup_used_by((
			DATRefs(DATID.units, lambda unit: (
				DATRef('Construction', cast(DATUnit, unit).construction_animation, dat_sub_tab=UnitsTabID.graphics),
			)),
			DATRefs(DATID.sprites, lambda sprite: (
				DATRef('Image', cast(DATSprite, sprite).image),
			)),
		))

	def updated_pointer_entries(self, ids: list[AnyID]) -> None:
		if DataID.imagestbl in ids:
			image_names = ('None',) + self.delegate.data_context.imagestbl.strings
			for dropdown,entry_var in self.grpdds:
				dropdown.setentries(image_names)
				entry_var.range[1] = len(self.delegate.data_context.imagestbl.strings)
		if DataID.iscriptbin in ids:
			iscript_names = []
			last_id = -1
			for script in self.delegate.data_context.iscriptbin.list_scripts():
				script_id = script.id
				if script_id-last_id > 1:
					iscript_names.extend(['*Unused*'] * (script_id-last_id-1))
				if script_id < len(Assets.data_cache(Assets.DataReference.IscriptIDList)):
					n = Assets.data_cache(Assets.DataReference.IscriptIDList)[script_id]
				else:
					n = 'Unnamed Custom Entry'
				iscript_names.append(n)
				last_id = script_id
			self.iscripts.setentries(iscript_names)
			self.iscriptentry.range[1] = len(iscript_names)-1

		if (DATID.units in ids or DATID.sprites in ids) and self.delegate.active_tab() == self:
			self.check_used_by_references()

	def shieldupdate(self, n: int) -> None:
		self.shieldentry.set([0,133,2,184][n])

	def drawpreview(self, _event: UI.Event | None = None) -> None:
		if self.previewing != self.id or (self.previewing is not None and not self.showpreview.get()) or (self.previewing is None and self.showpreview.get()):
			self.preview.delete(UI.ALL)
			if self.showpreview.get():
				frame = self.delegate.data_context.get_image_frame(self.id)
				if frame:
					self.preview.create_image(130, 130, image=frame[0])
				self.previewing = self.id
			else:
				self.previewing = None

	def load_entry(self, entry: DATImage) -> None:
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

		self.drawpreview()

	def save_entry(self, entry: DATImage) -> None:
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

		self.delegate.data_context.config.preview.image.show.value = self.showpreview.get()
