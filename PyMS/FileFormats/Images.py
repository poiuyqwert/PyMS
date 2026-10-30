
from dataclasses import dataclass

Pixels = list[list[int]]

RGB = tuple[int, int, int]
RGBA = tuple[int, int, int, int]

RawPalette = list[RGB]

# x_max/y_max are exclusive (one past the last pixel)
@dataclass(frozen=True, kw_only=True)
class Bounds:
	x_min: int
	y_min: int
	x_max: int
	y_max: int

	@property
	def width(self) -> int:
		return self.x_max - self.x_min

	@property
	def height(self) -> int:
		return self.y_max - self.y_min
