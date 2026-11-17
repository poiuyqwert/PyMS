from __future__ import annotations

from .ButtonRow import draw_icon

from ...FileFormats.Graft import Button

from ...Utilities import UIKit as UI
from ...Utilities.IconSelectDialog import ImageWithBounds
from ...Utilities.TextPreview.TextDrawing import TextDrawing
from ...Utilities.TextPreview.TextPreviewTooltip import TextPreviewTooltip

from typing import Protocol

class PreviewGridDelegate(Protocol):
	def select_button(self, index: int) -> None:
		...

	def button_icon(self, icon: int) -> ImageWithBounds | None:
		...

	def button_tooltip(self, button: Button, *, enabled: bool = True) -> TextDrawing | None:
		...

# A preview of the button set like the game's command card: a slot for each position, showing the icon of a button at that position.
# When several buttons are at the same position, the slot shows which of them it's showing (`x/y`), and clicking it again selects the next one.
# Hovering over a slot shows the tooltip of its button like the game does.
class PreviewGrid(UI.Frame):
	def __init__(self, parent: UI.Misc, delegate: PreviewGridDelegate) -> None:
		super().__init__(parent)
		self.delegate = delegate
		self.font = UI.Font.fixed().sized(6)
		# The indexes (in the button set) of the buttons at each position, in their order in the set
		self.slot_buttons: dict[int, list[int]] = {}
		# The index of the button each position shows
		self.shown_buttons: dict[int, int] = {}
		self.selected: int | None = None
		self.slots: dict[int, UI.Canvas] = {}
		# The buttons the slots show
		self.slot_shown: dict[int, Button] = {}
		self.tooltips: dict[int, TextPreviewTooltip] = {}
		# A slot for each of the 9 positions, in 3 columns
		for position in range(1, 10):
			# Larger than an icon, so the labels in its corners overlap the (centered) icon less
			canvas = UI.Canvas(self, width=44, height=44, background='#000000', highlightthickness=0, borderwidth=0, theme_tag='preview') # type: ignore[call-arg]
			row, column = divmod(position - 1, 3)
			canvas.grid(row=row, column=column, padx=1, pady=1)
			canvas.bind(UI.Mouse.Click_Left(), lambda _, position=position: self.slot_clicked(position)) # type: ignore[misc]
			self.slots[position] = canvas
			self.tooltips[position] = TextPreviewTooltip(canvas, lambda position=position: self.slot_tooltip(position)) # type: ignore[misc]

	def update_buttons(self, buttons: list[Button], selected: int | None) -> None:
		self.selected = selected
		self.slot_buttons = {position: [] for position in self.slots}
		for index, button in enumerate(buttons):
			if button.position in self.slot_buttons:
				self.slot_buttons[button.position].append(index)
		for position, indexes in self.slot_buttons.items():
			# A slot shows the selected button when it's at its position, otherwise it keeps showing the same button (or its first)
			shown = self.shown_buttons.get(position)
			if selected in indexes:
				shown = selected
			elif shown not in indexes:
				shown = indexes[0] if indexes else None
			if shown is None:
				self.shown_buttons.pop(position, None)
			else:
				self.shown_buttons[position] = shown
			self.draw_slot(position, buttons[shown] if shown is not None else None)

	def draw_slot(self, position: int, button: Button | None) -> None:
		canvas = self.slots[position]
		if button is None:
			self.slot_shown.pop(position, None)
		else:
			self.slot_shown[position] = button
		width = int(canvas.cget('width'))
		height = int(canvas.cget('height'))
		canvas.delete(UI.ALL)
		indexes = self.slot_buttons[position]
		draw_icon(canvas, self.delegate.button_icon(button.icon) if button else None)
		self.draw_label(canvas, 2, 0, str(position), anchor=UI.NW, tag='number')
		if len(indexes) > 1:
			shown = self.shown_buttons[position]
			self.draw_label(canvas, width - 2, height - 1, f'{indexes.index(shown) + 1}/{len(indexes)}', anchor=UI.SE, tag='count')
		if self.selected in indexes:
			canvas.create_rectangle(0, 0, width - 1, height - 1, outline=UI.Style().lookup('.', 'selectbackground'), tags='selection')

	def draw_label(self, canvas: UI.Canvas, x: int, y: int, text: str, *, anchor: str, tag: str) -> None:
		# The labels are drawn over the icons, which are mostly bright (yellow) on black.
		# A 1 pixel black shadow behind the label (invisible on the black) keeps it readable over the bright icons.
		canvas.create_text(x + 1, y + 1, text=text, anchor=anchor, fill='#000000', font=self.font, tags=f'{tag}_shadow')
		canvas.create_text(x, y, text=text, anchor=anchor, fill='#7C8DD4', font=self.font, tags=tag)

	def slot_tooltip(self, position: int) -> TextDrawing | None:
		# The enabled string of the slot's button (the string shown when it can be used)
		button = self.slot_shown.get(position)
		if button is None:
			return None
		return self.delegate.button_tooltip(button)

	def slot_clicked(self, position: int) -> None:
		indexes = self.slot_buttons.get(position)
		if not indexes:
			return
		if self.selected in indexes:
			if len(indexes) == 1:
				return
			# Clicking the slot of the selected button selects the next button at its position
			assert self.selected is not None
			index = indexes[(indexes.index(self.selected) + 1) % len(indexes)]
		else:
			index = self.shown_buttons[position]
		self.delegate.select_button(index)

	# For tests and the status of the slots

	def slot_text(self, position: int, tag: str) -> str | None:
		canvas = self.slots[position]
		items = canvas.find_withtag(tag)
		if not items:
			return None
		return str(canvas.itemcget(items[0], 'text'))

	def slot_selected(self, position: int) -> bool:
		return bool(self.slots[position].find_withtag('selection'))
