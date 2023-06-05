
from .Delegates import MegaEditorViewDelegate, TilePaletteDelegate, MiniEditorDelegate

from ..FileFormats.Tileset.Tileset import Tileset, TileType
from ..FileFormats.Tileset.VF4 import VF4Flag
from ..FileFormats.Tileset.VX4 import VX4Minitile

from ..Utilities.UIKit import *
from ..Utilities import Assets
from ..Utilities.Settings import Settings

from enum import Enum

class MegaEditorView(Frame, TilePaletteDelegate, MiniEditorDelegate):
	class Mode(Enum):
		mini          = 0
		flip          = 1
		height        = 2
		walkability   = 3
		view_blocking = 4
		ramp          = 5

	def __init__(self, parent, settings, delegate, owner=None, megatile_id=None, palette_editable=False): # type: (Misc, Settings, MegaEditorViewDelegate, Misc | None, int | None, bool) -> None
		Frame.__init__(self, parent)

		self.settings = settings
		self.delegate = delegate
		self.megatile_id = megatile_id
		self.palette_editable = palette_editable
		self.edit_mode = IntVar()
		self.edit_mode.set(self.settings.mega_edit.get('mode', MegaEditorView.Mode.mini.value))
		self.edit_mode.trace('w', self.edit_mode_updated)
		self.delegate.mega_edit_mode_updated(self.get_edit_mode())
		self.minitile_n = 0
		self.last_click = None # type: int | None
		self.toggle_on = None # type: bool | None
		self.enabled = True
		self.disable = [] # type: list[Misc]

		self.minitile = IntegerVar(0,[0,0],callback=lambda id: self.change(None, int(id)), callback_when=IntegerVar.UpdateCase.user)
		self.height = IntVar()
		self.height.set(self.settings.mega_edit.get('height', 1))
		self.height.trace('w', self.height_updated)

		self.active_tools = None # type: Widget | None

		if owner is None:
			self.owner = parent
		else:
			self.owner = owner

		frame = Frame(self)
		d = DropDown(frame, self.edit_mode, ['Minitile (m)','Flip (f)','Height (h)','Walkable (w)','Block view (b)','Ramp? (r)'], width=15)
		self.disable.append(d)
		d.pack(side=TOP, padx=5)
		def set_edit_mode(mode): # type: (MegaEditorView.Mode) -> None
			if not self.enabled:
				return
			self.edit_mode.set(mode.value)
		self.owner.bind(Key.m(), lambda _: set_edit_mode(MegaEditorView.Mode.mini)),
		self.owner.bind(Key.f(), lambda _: set_edit_mode(MegaEditorView.Mode.flip)),
		self.owner.bind(Key.h(), lambda _: set_edit_mode(MegaEditorView.Mode.height)),
		self.owner.bind(Key.w(), lambda _: set_edit_mode(MegaEditorView.Mode.walkability)),
		self.owner.bind(Key.b(), lambda _: set_edit_mode(MegaEditorView.Mode.view_blocking)),
		self.owner.bind(Key.r(), lambda _: set_edit_mode(MegaEditorView.Mode.ramp))

		self.canvas = Canvas(frame, width=96, height=96, background='#000000', theme_tag='preview') # type: ignore[call-arg]
		self.canvas_images = [] # type: list[Image]
		def mouse_to_mini(e): # type: (Event) -> (int | None)
			if e.x < 1 or e.x > 96 or e.y < 1 or e.y > 96:
				return None
			return (e.y - 1) // 24 * 4 + (e.x - 1) // 24
		def click(e): # type: (Event) -> None
			mini = mouse_to_mini(e)
			if mini is None:
				return
			self.last_click = mini
			self.click_minitile(mini)
		def move(e): # type: (Event) -> None
			mini = mouse_to_mini(e)
			if mini is None or mini == self.last_click:
				return
			self.last_click = mini
			self.click_minitile(mini)
		def release(_): # type: (Event) -> None
			self.last_click = None
			self.toggle_on = None
		def fill(e): # type: (Event) -> None
			mini = mouse_to_mini(e)
			if mini is None:
				return
			self.fill_minitiles(mini)
		self.canvas.bind(Mouse.Click_Left(), click)
		self.canvas.bind(Mouse.Drag_Left(), move)
		self.canvas.bind(ButtonRelease.Click_Left(), release)
		self.canvas.bind(Mouse.Click_Right(), fill)
		self.canvas.pack(side=TOP)
		self.mini_tools = Frame(frame)
		e = Frame(self.mini_tools)
		Label(e, text='ID:').pack(side=LEFT)
		f = Entry(e, textvariable=self.minitile, font=Font.fixed(), width=5)
		Tooltip(f, 'MiniTile ID:\nID for the selected MiniTile in the current MegaTile')
		self.disable.append(f)
		f.pack(side=LEFT, padx=2)
		b = Button(e, image=Assets.get_image('find'), width=20, height=20, command=self.choose)
		self.disable.append(b)
		Tooltip(b, 'MiniTile Palette')
		b.pack(side=LEFT, padx=2)
		b = Button(e, image=Assets.get_image('edit'), width=20, height=20, command=self.editor)
		self.disable.append(b)
		b.pack(side=LEFT, padx=2)
		e.pack(fill=X)
		self.mini_tools.pack(side=TOP, pady=(3,0))
		self.mini_tools.pack_forget()
		self.height_tools = Frame(frame)
		d = DropDown(self.height_tools, self.height, ['Low (Red)','Mid (Orange)','High (Yellow)'], width=15)
		self.disable.append(d)
		d.pack(side=LEFT, padx=5)
		self.height_tools.pack(side=TOP, pady=(3,0))
		self.height_tools.pack_forget()
		frame.pack(side=LEFT, fill=Y)

		self.update_mini_range()
		self.update_tools()
		self.load_megatile()

	def get_tileset(self): # type: () -> (Tileset | None)
		return self.delegate.get_tileset()

	def get_tile(self, id): # type: (int | VX4Minitile) -> Image
		return self.delegate.get_tile(id)

	def get_edit_mode(self): # type: () -> MegaEditorView.Mode
		return MegaEditorView.Mode(self.edit_mode.get())

	def editor(self): # type: () -> None
		tileset = self.delegate.get_tileset()
		if not tileset or self.megatile_id is None:
			return
		minitile_image_id = tileset.vx4.get_megatile(self.megatile_id).minitiles[self.minitile_n].image_id
		from .MiniEditor import MiniEditor
		MiniEditor(self.owner, minitile_image_id, self)

	def set_enabled(self, enabled): # type: (bool) -> None
		self.enabled = enabled
		state = NORMAL if enabled else DISABLED
		for w in self.disable:
			w['state'] = state

	def update_mini_range(self): # type: () -> None
		size = 0
		tileset = self.delegate.get_tileset()
		if tileset:
			size = tileset.vr4.image_count()-1
		self.minitile.setrange([0,size])

	def update_tools(self): # type: () -> None
		if self.active_tools:
			self.active_tools.pack_forget()
			self.active_tools = None
		mode = self.get_edit_mode()
		if mode == MegaEditorView.Mode.mini:
			self.mini_tools.pack()
			self.active_tools = self.mini_tools
		elif mode == MegaEditorView.Mode.height:
			self.height_tools.pack()
			self.active_tools = self.height_tools

	def edit_mode_updated(self, *_): # type: (Any) -> None
		self.update_tools()
		self.draw_edit_mode()
		mode = self.get_edit_mode()
		self.settings.mega_edit.mode = mode.value
		self.delegate.mega_edit_mode_updated(mode)

	def height_updated(self, *_): # type: (Any) -> None
		self.settings.mega_edit.height = self.height.get()

	def draw_border(self, minitile_n, color='#FFFFFF'): # type: (int, str) -> None
		x = 3 + 24 * (minitile_n % 4)
		y = 3 + 24 * (minitile_n // 4)
		self.canvas.create_rectangle(x,y, x+21,y+21, outline=color, tags='mode')

	def draw_selection(self): # type: () -> None
		self.draw_border(self.minitile_n)

	def draw_height(self): # type: () -> None
		tileset = self.delegate.get_tileset()
		if not tileset or self.megatile_id is None:
			return
		all_flags = tileset.vf4.get_flags(self.megatile_id)
		for n in range(16):
			flags = all_flags[n]
			color = '#FF0000'
			if flags & VF4Flag.mid_ground:
				color = '#FFA500'
			elif flags & VF4Flag.high_ground:
				color = '#FFFF00'
			self.draw_border(n, color)

	def draw_walkability(self): # type: () -> None
		tileset = self.delegate.get_tileset()
		if not tileset or self.megatile_id is None:
			return
		all_flags = tileset.vf4.get_flags(self.megatile_id)
		for n in range(16):
			flags = all_flags[n]
			self.draw_border(n, '#00FF00' if flags & VF4Flag.walkable else '#FF0000')

	def draw_blocking(self): # type: () -> None
		tileset = self.delegate.get_tileset()
		if not tileset or self.megatile_id is None:
			return
		all_flags = tileset.vf4.get_flags(self.megatile_id)
		for n in range(16):
			flags = all_flags[n]
			self.draw_border(n, '#FF0000' if flags & VF4Flag.blocks_view else '#00FF00')

	def draw_ramp(self): # type: () -> None
		tileset = self.delegate.get_tileset()
		if not tileset or self.megatile_id is None:
			return
		all_flags = tileset.vf4.get_flags(self.megatile_id)
		for n in range(16):
			flags = all_flags[n]
			self.draw_border(n, '#00FF00' if flags & VF4Flag.ramp else '#FF0000')

	def draw_edit_mode(self): # type: () -> None
		self.canvas.delete('mode')
		if not self.delegate.get_tileset() or self.megatile_id is None:
			return
		mode = self.get_edit_mode()
		if mode == MegaEditorView.Mode.mini:
			self.draw_selection()
		elif mode == MegaEditorView.Mode.height:
			self.draw_height()
		elif mode == MegaEditorView.Mode.walkability:
			self.draw_walkability()
		elif mode == MegaEditorView.Mode.view_blocking:
			self.draw_blocking()
		elif mode == MegaEditorView.Mode.ramp:
			self.draw_ramp()

	def click_selection(self, minitile_n): # type: (int) -> None
		tileset = self.delegate.get_tileset()
		if not tileset or self.megatile_id is None:
			return
		self.minitile_n = minitile_n
		self.minitile.set(tileset.vx4.get_megatile(self.megatile_id).minitiles[minitile_n].image_id)
		self.draw_edit_mode()

	def click_flipped(self, minitile_n): # type: (int) -> None
		tileset = self.delegate.get_tileset()
		if not tileset or self.megatile_id is None:
			return
		minitiles = list(tileset.vx4.get_megatile(self.megatile_id).minitiles)
		minitile = minitiles[minitile_n]
		minitile.flipped = not minitile.flipped
		self.redraw_delegate()
		self.draw()
		self.mark_edited()

	def click_height(self, minitile_n): # type: (int) -> None
		tileset = self.delegate.get_tileset()
		if not tileset or self.megatile_id is None:
			return
		all_flags = tileset.vf4.get_flags(self.megatile_id)
		flags = all_flags[minitile_n]
		new_flags = flags & ~(VF4Flag.mid_ground | VF4Flag.high_ground)
		new_flags |= [0,VF4Flag.mid_ground,VF4Flag.high_ground][self.height.get()]
		if new_flags != flags:
			all_flags[minitile_n] = new_flags
			self.draw_edit_mode()
			self.mark_edited()

	def click_flag(self, minitile_n, flag): # type: (int, int) -> None
		tileset = self.delegate.get_tileset()
		if not tileset or self.megatile_id is None:
			return
		flags = tileset.vf4.get_flags(self.megatile_id)
		if self.toggle_on is None:
			self.toggle_on = not (flags[minitile_n] & flag)
		if self.toggle_on:
			flags[minitile_n] |= flag
		else:
			flags[minitile_n] &= ~flag
		self.draw_edit_mode()
		self.mark_edited()

	def click_minitile(self, minitile_n): # type: (int) -> None
		if not self.delegate.get_tileset() or self.megatile_id is None:
			return
		mode = self.edit_mode.get()
		if mode == MegaEditorView.Mode.mini:
			self.click_selection(minitile_n)
		elif mode == MegaEditorView.Mode.flip:
			self.click_flipped(minitile_n)
		elif mode == MegaEditorView.Mode.height:
			self.click_height(minitile_n)
		elif mode == MegaEditorView.Mode.walkability:
			self.click_flag(minitile_n, VF4Flag.walkable)
		elif mode == MegaEditorView.Mode.view_blocking:
			self.click_flag(minitile_n, VF4Flag.blocks_view)
		elif mode == MegaEditorView.Mode.ramp:
			self.click_flag(minitile_n, VF4Flag.ramp)

	def fill_height(self): # type: () -> None
		tileset = self.delegate.get_tileset()
		if not tileset or self.megatile_id is None:
			return
		edited = False
		all_flags = tileset.vf4.get_flags(self.megatile_id)
		for n in range(16):
			flags = all_flags[n]
			new_flags = flags & ~(VF4Flag.mid_ground | VF4Flag.high_ground)
			new_flags |= [0,VF4Flag.mid_ground,VF4Flag.high_ground][self.height.get()]
			if new_flags != flags:
				all_flags[n] = new_flags
				edited = True
		if edited:
			self.draw_edit_mode()
			self.mark_edited()

	def fill_flag(self, minitile_n, flag): # type: (int, int) -> None
		tileset = self.delegate.get_tileset()
		if not tileset or self.megatile_id is None:
			return
		all_flags = tileset.vf4.get_flags(self.megatile_id)
		enable = not (all_flags[minitile_n] & flag)
		edited = False
		for n in range(16):
			flags = all_flags[n]
			if enable:
				all_flags[n] |= flag
			else:
				all_flags[n] &= ~flag
			if all_flags[n] != flags:
				edited = True
		if edited:
			self.draw_edit_mode()
			self.mark_edited()

	def fill_minitiles(self, minitile_n): # type: (int) -> None
		if not self.delegate.get_tileset() or self.megatile_id is None:
			return
		mode = self.get_edit_mode()
		if mode == MegaEditorView.Mode.height:
			self.fill_height()
		elif mode == MegaEditorView.Mode.walkability:
			self.fill_flag(minitile_n, 1)
		elif mode == MegaEditorView.Mode.view_blocking:
			self.fill_flag(minitile_n, 8)
		elif mode == MegaEditorView.Mode.ramp:
			self.fill_flag(minitile_n, 16)

	def draw_minitiles(self): # type: () -> None
		self.canvas.delete('tile')
		self.canvas_images.clear()
		tileset = self.delegate.get_tileset()
		if not tileset or self.megatile_id is None:
			return
		for n,minitile in enumerate(tileset.vx4.get_megatile(self.megatile_id).minitiles):
			self.canvas_images.append(self.delegate.get_tile(minitile.image_id))
			self.canvas.create_image(2 + 24 * (n % 4), 2 + 24 * (n / 4), anchor=NW, image=self.canvas_images[-1], tags='tile')

	def draw(self): # type: () -> None
		self.draw_minitiles()
		self.draw_edit_mode()

	def load_megatile(self): # type: () -> None
		tileset = self.delegate.get_tileset()
		if tileset is not None and self.megatile_id is not None:
			self.minitile.set(tileset.vx4.get_megatile(self.megatile_id).minitiles[self.minitile_n].image_id)
		else:
			self.minitile.set(0)
		self.draw()

	def set_megatile(self, megatile_id): # type: (int | None) -> None
		self.megatile_id = megatile_id
		self.load_megatile()

	def redraw_delegate(self): # type: () -> None
		from .TilePalette import TilePalette
		if self.megatile_id in TilePalette.TILE_CACHE:
			del TilePalette.TILE_CACHE[self.megatile_id]
		self.delegate.draw_group()

	def mark_edited(self): # type: () -> None
		self.delegate.mark_edited()

	def change(self, tiletype, minitile_id): # type: (TileType | None, int) -> None
		if tiletype == TileType.mini:
			self.minitile.set(minitile_id)
		elif tiletype is not None:
			return
		tileset = self.delegate.get_tileset()
		if not tileset or self.megatile_id is None:
			return
		megatile = tileset.vx4.get_megatile(self.megatile_id)
		minitile = megatile.minitiles[self.minitile_n]
		minitile.image_id = minitile_id
		self.redraw_delegate()
		self.draw()
		self.mark_edited()

	def choose(self): # type: () -> None
		tileset = self.delegate.get_tileset()
		if not tileset or self.megatile_id is None:
			return
		from .TilePalette import TilePalette
		TilePalette(
			self.owner,
			self.settings,
			self,
			TileType.mini,
			tileset.vx4.get_megatile(self.megatile_id).minitiles[self.minitile_n].image_id,
			editing=self.palette_editable
		)

	def set_selecting(self, selecting): # type: (bool | None) -> None
		pass

	def megaload(self): # type: () -> None
		self.redraw_delegate()
		self.draw()

	def update_ranges(self): # type: () -> None
		pass

	def draw_tiles(self, force): # type: (bool) -> None
		pass
