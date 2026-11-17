from ...FileFormats import FNT
from ...FileFormats.PCX import PCX

from typing import cast

class StubFont:
	# Minimal stand-in for FNT.FNT: letters ' '..'Z', each `letter_width` wide (the space is 0 wide, like some game fonts)
	def __init__(self, letter_width: int = 9, height: int = 10) -> None:
		self.start = ord(' ')
		self.height = height
		count = ord('Z') - ord(' ') + 1
		self.letters = [object() for _ in range(count)]
		# Size = (width, height, xoffset, yoffset)
		self.sizes: list[tuple[int, int, int, int]] = []
		for index in range(count):
			width = 0 if index == 0 else letter_width
			self.sizes.append((width, height, 0, 0))

def stub_font(letter_width: int = 9, height: int = 10) -> FNT.FNT:
	return cast(FNT.FNT, StubFont(letter_width, height))

def letter(character: str) -> int:
	return ord(character) - ord(' ')

def stub_colors() -> PCX:
	return PCX()
