
from ..FileFormats.Tileset.Tileset import HEIGHT_LOW, HEIGHT_MID, HEIGHT_HIGH, TILETYPE_MINI

from ..Utilities.UIKit import *
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.Tooltip import Tooltip
from ..Utilities import Assets

class MegaEditorView(Frame):
	class Mode:
		mini          = 0
		flip          = 1
		height        = 2
		walkability   = 3
		view_blocking = 4
		ramp          = 5

	def __init__(self, parent, settings, delegate, megatile_id=None, palette_editable=False):
		Frame.__init__(self, parent)

		self.settings = settings
		self.delegate = delegate
		self.megatile_id = megatile_id
		self.palette_editable = palette_editable
		self.edit_mode = IntVar()
		self.edit_mode.set(self.settings.mega_edit.get('mode', MegaEditorView.Mode.mini))
		self.edit_mode.trace('w', self.edit_mode_updated)
		if hasattr(self.delegate, 'mega_edit_mode_updated'):
			self.delegate.mega_edit_mode_updated(self.edit_mode.get())
		self.minitile_n = 0
		self.last_click = None
		self.toggle_on = None
		self.enabled = True
		self.disable = []

		self.minitile = IntegerVar(0,[0,0],callback=lambda id: self.change(None, int(id)), callback_when=IntegerVar.UpdateCase.user)
		self.height = IntVar()
		self.height.set(self.settings.mega_edit.get('height', 1))
		self.height.trace('w', self.height_updated)

		self.active_tools = None

		frame = Frame(self)
		d = DropDown(frame, self.edit_mode, ['Minitile (m)','Flip (f)','Height (h)','Walkable (w)','Block view (b)','Ramp? (r)'], width=15)
		self.disable.append(d)
		d.pack(side=TOP, padx=5)
		def set_edit_mode(mode):
			if not self.enabled:
				return
			self.edit_mode.set(mode)
		self.delegate.bind(Key.m, lambda _: set_edit_mode(MegaEditorView.Mode.mini)),
		self.delegate.bind(Key.f, lambda _: set_edit_mode(MegaEditorView.Mode.flip)),
		self.delegate.bind(Key.h, lambda _: set_edit_mode(MegaEditorView.Mode.height)),
		self.delegate.bind(Key.w, lambda _: set_edit_mode(MegaEditorView.Mode.walkability)),
		self.delegate.bind(Key.b, lambda _: set_edit_mode(MegaEditorView.Mode.view_blocking)),
		self.delegate.bind(Key.r, lambda _: set_edit_mode(MegaEditorView.Mode.ramp))

		self.canvas = Canvas(frame, width=96, height=96, background='#000000')
		def mouse_to_mini(e):
			if e.x < 1 or e.x > 96 or e.y < 1 or e.y > 96:
				return None
			return (e.y - 1) / 24 * 4 + (e.x - 1) / 24
		def click(e):
			mini = mouse_to_mini(e)
			if mini != None:
				self.last_click = mouse_to_mini(e)
				self.click_minitile(self.last_click)
		def move(e):
			mini = mouse_to_mini(e)
			if mini != None and mini != self.last_click:
				self.last_click = mini
				self.click_minitile(mini)
		def release(_):
			self.last_click = None
			self.toggle_on = None
		def fill(e):
			mini = mouse_to_mini(e)
			if mini != None:
				self.fill_minitiles(mini)
		self.canvas.bind(Mouse.Click_Left, click)
		self.canvas.bind(Mouse.Drag_Left, move)
		self.canvas.bind(ButtonRelease.Click_Left, release)
		self.canvas.bind(Mouse.Click_Right, fill)
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

	def editor(self):
		minitile_image_id = self.delegate.tileset.vx4.graphics[self.megatile_id][self.minitile_n][0]
		from .MiniEditor import MiniEditor
		MiniEditor(self.delegate, minitile_image_id)

	def set_enabled(self, enabled):
		self.enabled = enabled
		state = NORMAL if enabled else DISABLED
		for w in self.disable:
			w['state'] = state

	def update_mini_range(self):
		size = 0
		if self.delegate.tileset:
			size = len(self.delegate.tileset.vr4.images)-1
		self.minitile.setrange([0,size])

	def update_tools(self):
		if self.active_tools:
			self.active_tools.pack_forget()
			self.active_tools = None
		mode = self.edit_mode.get()
		if mode == MegaEditorView.Mode.mini:
			self.mini_tools.pack()
			self.active_tools = self.mini_tools
		elif mode == MegaEditorView.Mode.height:
			self.height_tools.pack()
			self.active_tools = self.height_tools

	def edit_mode_updated(self, *_):
		self.update_tools()
		self.draw_edit_mode()
		mode = self.edit_mode.get()
		self.settings.mega_edit.mode = mode
		if hasattr(self.delegate, 'mega_edit_mode_updated'):
			self.delegate.mega_edit_mode_updated(mode)

	def height_updated(self, *_):
		self.settings.mega_edit.height = self.height.get()

	def draw_border(self, minitile_n, color='#FFFFFF'):
		x = 3 + 24 * (minitile_n % 4)
		y = 3 + 24 * (minitile_n / 4)
		self.canvas.create_rectangle(x,y, x+21,y+21, outline=color, tags='mode')

	def draw_selection(self):
		self.draw_border(self.minitile_n)

	def draw_height(self):
		for n in range(16):
			flags = self.delegate.tileset.vf4.flags[self.megatile_id][n]
			color = '#FF0000'
			if flags & HEIGHT_MID:
				color = '#FFA500'
			elif flags & HEIGHT_HIGH:
				color = '#FFFF00'
			self.draw_border(n, color)

	def draw_walkability(self):
		for n in range(16):
			flags = self.delegate.tileset.vf4.flags[self.megatile_id][n]
			self.draw_border(n, '#00FF00' if flags & 1 else '#FF0000')

	def draw_blocking(self):
		for n in range(16):
			flags = self.delegate.tileset.vf4.flags[self.megatile_id][n]
			self.draw_border(n, '#FF0000' if flags & 8 else '#00FF00')

	def draw_ramp(self):
		for n in range(16):
			flags = self.delegate.tileset.vf4.flags[self.megatile_id][n]
			self.draw_border(n, '#00FF00' if flags & 16 else '#FF0000')

	def draw_edit_mode(self):
		self.canvas.delete('mode')
		if not self.delegate.tileset or self.megatile_id == None:
			return
		mode = self.edit_mode.get()
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

	def click_selection(self, minitile_n):
		self.minitile_n = minitile_n
		self.minitile.set(self.delegate.tileset.vx4.graphics[self.megatile_id][minitile_n][0])
		self.draw_edit_mode()

	def click_flipped(self, minitile_n):
		megatile = list(self.delegate.tileset.vx4.graphics[self.megatile_id])
		minitile = megatile[minitile_n]
		megatile[minitile_n] = (minitile[0], not minitile[1])
		self.delegate.tileset.vx4.set_tile(self.megatile_id, megatile)
		self.redraw_delegate()
		self.draw()
		self.mark_edited()

	def click_height(self, minitile_n):
		flags = self.delegate.tileset.vf4.flags[self.megatile_id][minitile_n]
		new_flags = flags & ~(HEIGHT_MID | HEIGHT_HIGH)
		new_flags |= [HEIGHT_LOW,HEIGHT_MID,HEIGHT_HIGH][self.height.get()]
		if new_flags != flags:
			self.delegate.tileset.vf4.flags[self.megatile_id][minitile_n] = new_flags
			self.draw_edit_mode()
			self.mark_edited()

	def click_flag(self, minitile_n, flag):
		if self.toggle_on == None:
			self.toggle_on = not (self.delegate.tileset.vf4.flags[self.megatile_id][minitile_n] & flag)
		if self.toggle_on:
			self.delegate.tileset.vf4.flags[self.megatile_id][minitile_n] |= flag
		else:
			self.delegate.tileset.vf4.flags[self.megatile_id][minitile_n] &= ~flag
		self.draw_edit_mode()
		self.mark_edited()

	def click_minitile(self, minitile_n):
		if not self.delegate.tileset or self.megatile_id == None:
			return
		mode = self.edit_mode.get()
		if mode == MegaEditorView.Mode.mini:
			self.click_selection(minitile_n)
		elif mode == MegaEditorView.Mode.flip:
			self.click_flipped(minitile_n)
		elif mode == MegaEditorView.Mode.height:
			self.click_height(minitile_n)
		elif mode == MegaEditorView.Mode.walkability:
			self.click_flag(minitile_n, 1)
		elif mode == MegaEditorView.Mode.view_blocking:
			self.click_flag(minitile_n, 8)
		elif mode == MegaEditorView.Mode.ramp:
			self.click_flag(minitile_n, 16)

	def fill_height(self):
		edited = False
		for n in range(16):
			flags = self.delegate.tileset.vf4.flags[self.megatile_id][n]
			new_flags = flags & ~(HEIGHT_MID | HEIGHT_HIGH)
			new_flags |= [HEIGHT_LOW,HEIGHT_MID,HEIGHT_HIGH][self.height.get()]
			if new_flags != flags:
				self.delegate.tileset.vf4.flags[self.megatile_id][n] = new_flags
				edited = True
		if edited:
			self.draw_edit_mode()
			self.mark_edited()

	def fill_flag(self, minitile_n, flag):
		enable = not (self.delegate.tileset.vf4.flags[self.megatile_id][minitile_n] & flag)
		for n in range(16):
			if enable:
				self.delegate.tileset.vf4.flags[self.megatile_id][n] |= flag
			else:
				self.delegate.tileset.vf4.flags[self.megatile_id][n] &= ~flag
		self.draw_edit_mode()
		self.mark_edited()

	def fill_minitiles(self, minitile_n):
		if not self.delegate.tileset or self.megatile_id == None:
			return
		mode = self.edit_mode.get()
		if mode == MegaEditorView.Mode.height:
			self.fill_height()
		elif mode == MegaEditorView.Mode.walkability:
			self.fill_flag(minitile_n, 1)
		elif mode == MegaEditorView.Mode.view_blocking:
			self.fill_flag(minitile_n, 8)
		elif mode == MegaEditorView.Mode.ramp:
			self.fill_flag(minitile_n, 16)

	def draw_minitiles(self):
		self.canvas.delete('tile')
		self.canvas.images = []
		if not self.delegate.tileset or self.megatile_id == None:
			return
		for n,m in enumerate(self.delegate.tileset.vx4.graphics[self.megatile_id]):
			self.canvas.images.append(self.delegate.gettile(m))
			self.canvas.create_image(2 + 24 * (n % 4), 2 + 24 * (n / 4), anchor=NW, image=self.canvas.images[-1], tags='tile')

	def draw(self):
		self.draw_minitiles()
		self.draw_edit_mode()

	def load_megatile(self):
		if self.delegate.tileset and self.megatile_id != None:
			self.minitile.set(self.delegate.tileset.vx4.graphics[self.megatile_id][self.minitile_n][0])
		else:
			self.minitile.set(0)
		self.draw()

	def set_megatile(self, megatile_id):
		self.megatile_id = megatile_id
		self.load_megatile()

	def redraw_delegate(self):
		from .TilePalette import TilePalette
		if self.megatile_id in TilePalette.TILE_CACHE:
			del TilePalette.TILE_CACHE[self.megatile_id]
		if hasattr(self.delegate, 'draw_group'):
			self.delegate.draw_group()

	def mark_edited(self):
		self.delegate.mark_edited()

	def change(self, tiletype, minitile_id):
		if tiletype == TILETYPE_MINI:
			self.minitile.set(minitile_id)
		elif tiletype != None:
			return
		megatile = list(self.delegate.tileset.vx4.graphics[self.megatile_id])
		minitile = megatile[self.minitile_n]
		megatile[self.minitile_n] = (minitile_id, minitile[1])
		self.delegate.tileset.vx4.set_tile(self.megatile_id, megatile)
		self.redraw_delegate()
		self.draw()
		self.mark_edited()

	def choose(self):
		from .TilePalette import TilePalette
		TilePalette(
			self.delegate,
			self.settings,
			TILETYPE_MINI,
			self.delegate.tileset.vx4.graphics[self.megatile_id][self.minitile_n][0],
			self,
			editing=self.palette_editable
		)
