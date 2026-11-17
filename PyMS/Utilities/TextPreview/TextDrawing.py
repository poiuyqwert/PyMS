from __future__ import annotations

from .Layout import TextLayout, TextRuns, TextStyle, GlyphItem

from ..DataContext import DataContext
from .. import UIKit as UI

# Draws a laid out text into any canvas, with the letters of the context's fonts.
# The drawing keeps its canvas items (to move or delete them) and the images they show (so they stay alive when the context's caches are cleared).
class TextDrawing:
	def __init__(self, layout: TextLayout, data_context: DataContext) -> None:
		self.layout = layout
		self.data_context = data_context
		self.canvas: UI.Canvas | None = None
		self.items: list[UI.Canvas.Item] = []
		self.images: list[UI.AnyPhotoImage] = []
		# The offset of each item from the position of the drawing
		self.offsets: list[tuple[int, int]] = []

	@classmethod
	def tooltip(cls, runs: TextRuns, data_context: DataContext) -> TextDrawing | None:
		# The text like the game draws tooltips (`None` when the font or its colors aren't loaded)
		font = data_context.font8_fnt
		colors = data_context.tfontgam_pcx
		if font is None or colors is None:
			return None
		return cls(TextLayout.from_runs(runs, TextStyle.ingame(font, colors)), data_context)

	@property
	def width(self) -> int:
		return self.layout.width

	@property
	def height(self) -> int:
		return self.layout.height

	def is_drawn(self) -> bool:
		return self.canvas is not None

	def draw(self, canvas: UI.Canvas, x: int, y: int, *, tags: str | tuple[str, ...] = ()) -> None:
		# Draws the text with its top left at `x`,`y` (replacing an earlier drawing)
		self.delete()
		self.canvas = canvas
		style = self.layout.style
		for item in self.layout.items:
			image: UI.AnyPhotoImage | None
			if isinstance(item, GlyphItem):
				image = self.data_context.text_glyph(style, item.letter_index, item.color)
				offset = (item.x, item.y)
			else:
				image = item.image.image
				offset = (item.x - item.image.x_offset, item.y)
			if image is None:
				continue
			self.images.append(image)
			self.offsets.append(offset)
			self.items.append(canvas.create_image(x + offset[0], y + offset[1], image=image, anchor=UI.NW, tags=tags))

	def move(self, x: int, y: int) -> None:
		# Moves the drawn text so its top left is at `x`,`y`
		for item, (x_offset, y_offset) in zip(self.items, self.offsets):
			item.coords(x + x_offset, y + y_offset)

	def delete(self) -> None:
		for item in self.items:
			item.delete()
		self.items = []
		self.images = []
		self.offsets = []
		self.canvas = None
