
from typing import overload

class Colors:
	SystemHighlight = 'SystemHighlight'

	@overload
	@staticmethod
	def to_html(r: tuple[int, int, int], g: None = None, b: None = None) -> str:
		...
	@overload
	@staticmethod
	def to_html(r: int , g: int, b: int) -> str:
		...
	@staticmethod
	def to_html(r: int | tuple[int, int, int], g: int | None = None, b: int | None = None) -> str:
		if isinstance(r, tuple):
			r,g,b = r
		return f'#{r:02X}{g:02X}{b:02X}'
