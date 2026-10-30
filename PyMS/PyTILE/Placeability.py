
from .Config import PyTILEConfig
from .Delegates import MainDelegate, TilePaletteDelegate

from ..FileFormats.Tileset.Tileset import Tileset, megatile_to_photo, TileType
from ..FileFormats.Tileset.VX4 import VX4Minitile

from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.PyMSError import PyMSError

from typing import Callable

class Placeability(PyMSDialog, TilePaletteDelegate):
	def __init__(self, parent: UI.Misc, config: PyTILEConfig, delegate: MainDelegate, doodad_id: int = 0) -> None:
		self.config_ = config
		self.delegate = delegate
		self.id = doodad_id
		self.canvass: list[UI.Canvas] = []
		self.canvas_images: list[list[UI.AnyPhotoImage]] = []
		self.groups: list[list[UI.IntegerVar]] = []
		self.selecting: tuple[int, int] | None = None
		tileset = delegate.get_tileset()
		assert tileset is not None
		self.start_group_id, self.width, self.height = Placeability.doodad_layout(tileset, doodad_id)
		PyMSDialog.__init__(self, parent, f'Doodad Placeability [{doodad_id}]', resizable=(False,False))

	@staticmethod
	def doodad_layout(tileset: Tileset, doodad_id: int) -> tuple[int, int, int]:
		start_group_id: int | None = None
		for group_id in range(tileset.cv5.group_count()):
			if tileset.cv5.get_group(group_id).doodad_dddata_id == doodad_id:
				start_group_id = group_id
				break
		if start_group_id is None:
			raise PyMSError('Doodad', f'There are no MegaTile Groups with Doodad ID {doodad_id}')
		if doodad_id >= tileset.dddata.doodad_count():
			raise PyMSError('Doodad', f'Doodad ID {doodad_id} has no placeability data (must be less than {tileset.dddata.doodad_count()})')
		group = tileset.cv5.get_group(start_group_id)
		width = group.doodad_width
		height = group.doodad_height
		if not 1 <= width <= 16 or not 1 <= height <= 16:
			raise PyMSError('Doodad', f'Doodad {doodad_id} has an invalid size ({width}x{height})')
		if start_group_id + height > tileset.cv5.group_count():
			raise PyMSError('Doodad', f'Doodad {doodad_id} requires {height} MegaTile Groups but only {tileset.cv5.group_count() - start_group_id} remain')
		for y in range(height):
			if tileset.cv5.get_group(start_group_id + y).doodad_dddata_id != doodad_id:
				raise PyMSError('Doodad', f'Doodad {doodad_id} requires {height} contiguous MegaTile Groups with Doodad ID {doodad_id}')
		return (start_group_id, width, height)

	def widgetize(self) -> UI.Widget | None:
		tileset = self.delegate.get_tileset()
		assert tileset is not None
		f = UI.Frame(self)
		def select_callback(pos: tuple[int, int]) -> Callable[[UI.Event], None]:
			def select(_: UI.Event) -> None:
				self.select(pos)
			return select
		doodad = tileset.dddata.get_doodad(self.id)
		for y in range(self.height):
			group = tileset.cv5.get_group(self.start_group_id + y)
			self.groups.append([])
			self.canvass.append(UI.Canvas(f, width=self.width * 33-1, height=32))
			self.canvass[-1].grid(sticky=UI.E+UI.W, column=0, row=y*2, columnspan=self.width)
			self.canvas_images.append([])
			for x in range(self.width):
				t = f'tile{x},{y}'
				self.canvas_images[-1].append(megatile_to_photo(tileset, group.megatile_ids[x]))
				self.canvass[-1].create_image(x * 33 + 18, 18, image=self.canvas_images[-1][-1], tags=t)
				self.canvass[-1].tag_bind(t, UI.Double.Click_Left(), select_callback((x,y)))
				self.groups[-1].append(UI.IntegerVar(doodad[x + y * self.width], [0,tileset.cv5.group_count()]))
				UI.Entry(f, textvariable=self.groups[-1][-1], width=1, font=UI.Font.fixed(), bd=0).grid(sticky=UI.E+UI.W, column=x, row=y*2+1, padx=x%2)
		f.pack(padx=5,pady=5)
		return None

	def select(self, pos: tuple[int, int]) -> None:
		self.selecting = pos
		from .TilePalette import TilePalette
		TilePalette(parent=self, config=self.config_, delegate=self, tiletype=TileType.group, select=self.groups[pos[1]][pos[0]].get())

	def change(self, _: TileType, doodad_id: int) -> None:
		if self.selecting is None:
			return
		self.groups[self.selecting[1]][self.selecting[0]].set(doodad_id)
		self.selecting = None

	def cancel(self, _event: UI.Event | None = None) -> None:
		self.ok()

	def ok(self, _event: UI.Event | None = None) -> None:
		tileset = self.delegate.get_tileset()
		if not tileset:
			PyMSDialog.ok(self)
			return
		edited = False
		for y,l in enumerate(self.groups):
			for x,g in enumerate(l):
				n = x + y * self.width
				value = g.get()
				old_value = tileset.dddata.get_doodad(self.id)[n]
				if value != old_value:
					tileset.dddata.get_doodad(self.id)[n] = value
					edited = True
		if edited:
			self.delegate.mark_edited()
		PyMSDialog.ok(self)

	def get_tileset(self) -> Tileset | None:
		return self.delegate.get_tileset()

	def get_tile(self, tile_id: int | VX4Minitile) -> UI.AnyPhotoImage:
		return self.delegate.get_tile(tile_id)

	def megaload(self) -> None:
		pass

	def mark_edited(self) -> None:
		pass

	def update_ranges(self) -> None:
		pass
