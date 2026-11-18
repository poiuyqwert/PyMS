from __future__ import annotations

from .TextDrawing import TextDrawing

from .. import UIKit as UI

from typing import Any, Callable

# A tooltip showing a text like the game draws it (on black), from `drawing_lookup` when it's shown (no tooltip when it returns `None`)
class TextPreviewTooltip(UI.Tooltip):
	PADDING = 4

	def __init__(self, parent: UI.Misc, drawing_lookup: Callable[[], TextDrawing | None], **kwargs: Any) -> None:
		self.drawing_lookup = drawing_lookup
		self.drawing: TextDrawing | None = None
		self.canvas: UI.Canvas | None = None
		super().__init__(parent, **kwargs)

	def showtip(self) -> None:
		if self.tip:
			return
		drawing = self.drawing_lookup()
		if drawing is None:
			return
		self.tip = UI.TooltipWindow(self.parent, relief=UI.SOLID, borderwidth=1)
		self.tip.make_frameless(self.parent.winfo_toplevel())
		self.canvas = UI.Canvas(self.tip, background='#000000', highlightthickness=0, borderwidth=0, theme_tag='preview') # type: ignore[call-arg]
		self.canvas.pack()
		self._show_drawing(drawing)

	def refresh(self) -> None:
		# Shows the tip (right away) with what `drawing_lookup` returns now.
		# A shown tip is redrawn in its window: closing it and opening another makes Tk send the parent a Leave event, which would hide the new tip.
		self.unschedule()
		if not self.tip:
			self.showtip()
			return
		drawing = self.drawing_lookup()
		if drawing is None:
			self.hidetip()
			return
		if self.drawing:
			self.drawing.delete()
		self._show_drawing(drawing)

	def _show_drawing(self, drawing: TextDrawing) -> None:
		assert self.canvas is not None
		padding = TextPreviewTooltip.PADDING
		self.canvas.config(width=drawing.width + padding * 2, height=drawing.height + padding * 2)
		drawing.draw(self.canvas, padding, padding)
		self.drawing = drawing
		self.position_tip()

	def hidetip(self) -> None:
		if self.drawing:
			self.drawing.delete()
			self.drawing = None
		self.canvas = None
		super().hidetip()
