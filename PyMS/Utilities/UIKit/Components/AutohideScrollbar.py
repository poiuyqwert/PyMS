
from ..Widgets import Misc, Scrollbar

from typing import Callable, Any

class AutohideScrollbar(Scrollbar):
	def __init__(self, parent: Misc, **kwargs: Any) -> None:
		Scrollbar.__init__(self, parent, **kwargs)
		self._hide: Callable[[], None] | None = None
		self._show: Callable[[], None] | None = None
		self._show_info: dict[str, Any] | None = None
		self._show_order: tuple[int, ...] | None = None

	def place(self, **kwargs: Any) -> None: # type: ignore[override]
		def _hide() -> None:
			self._show_info = self.place_info() # type: ignore[assignment]
			self.place_forget()
		self._hide = _hide
		def _show() -> None:
			show_info = self._show_info or {}
			Scrollbar.place(self, **show_info)
			self._show_info = None
		self._show = _show
		Scrollbar.place(self, **kwargs)

	def pack(self, **kwargs: Any) -> None: # type: ignore[override]
		def _hide() -> None:
			self._show_info = self.pack_info() # type: ignore[assignment]
			self._show_order = tuple(widget.winfo_id() for widget in self.master.pack_slaves())
			self.pack_forget()
		self._hide = _hide
		def _show() -> None:
			show_info = self._show_info or {}
			if self._show_order and self.winfo_id() in self._show_order:
				slaves = self.master.pack_slaves()
				current_order = tuple(widget.winfo_id() for widget in slaves)
				start_index = self._show_order.index(self.winfo_id())
				check_index = start_index - 1
				while check_index >= 0:
					if self._show_order[check_index] in current_order:
						show_info['after'] = slaves[current_order.index(self._show_order[check_index])]
						break
					check_index -= 1
				check_index = start_index + 1
				while check_index < len(self._show_order):
					if self._show_order[check_index] in current_order:
						show_info['before'] = slaves[current_order.index(self._show_order[check_index])]
						break
					check_index += 1
			Scrollbar.pack(self, **show_info)
			self._show_info = None
			self._show_order = None
		self._show = _show
		Scrollbar.pack(self, **kwargs)

	def grid(self, **kwargs: Any) -> None: # type: ignore[override]
		self._hide = self.grid_remove
		self._show = self.grid
		Scrollbar.grid(self, **kwargs)

	def set(self, lo: float, hi: float) -> None:  # type: ignore[override]
		if float(lo) <= 0.0 and float(hi) >= 1.0:
			if self._hide:
				self._hide()
		elif self._show:
			self._show()
		Scrollbar.set(self, lo, hi)
