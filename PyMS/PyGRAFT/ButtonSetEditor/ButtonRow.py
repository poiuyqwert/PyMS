from __future__ import annotations

from ...FileFormats.Graft import Button
from ...FileFormats.Graft.CodeHandlers.CodeTypes import ButtonPositionCodeType

from ...Utilities import UIKit as UI
from ...Utilities import Assets
from ...Utilities.IconSelectDialog import ImageWithBounds

from typing import Protocol

class ButtonRowDelegate(Protocol):
	def select_button(self, index: int) -> None:
		...

	def move_button(self, index: int, delta: int) -> None:
		...

	def delete_button(self, index: int) -> None:
		...

	def add_button_after(self, index: int) -> None:
		...

	def button_icon(self, icon: int) -> ImageWithBounds | None:
		...

	def string_text(self, string_id: int) -> str:
		...

# Draws an icon centered in a canvas
def draw_icon(canvas: UI.Canvas, image: ImageWithBounds | None, tag: str = 'icon') -> None:
	canvas.delete(tag)
	if image is None:
		return
	icon, bounds = image
	x = int(canvas.cget('width')) // 2 - bounds.x_min - bounds.width // 2
	y = int(canvas.cget('height')) // 2 - bounds.y_min - bounds.height // 2
	canvas.create_image(x, y, image=icon, anchor=UI.NW, tags=tag)
	canvas.tag_lower(tag)

# A row of the button set Builder, showing one button of the set: its position, its icon, its enabled string,
# and the actions on the row (only shown while hovering over the row). Clicking the row (not its actions) selects it.
class ButtonRow(UI.Frame):
	# The size of a cmdicons.grp frame
	ICON_WIDTH = 36
	ICON_HEIGHT = 34
	ROW_PADDING = 3
	# The height of a row is the height of its icon (its tallest part)
	ROW_HEIGHT = ICON_HEIGHT + ROW_PADDING * 2

	def __init__(self, parent: UI.Misc, delegate: ButtonRowDelegate) -> None:
		super().__init__(parent)
		self.delegate = delegate
		self.index = 0
		self.button = Button()
		self.selected = False
		self.background_color = self.cget('bg')
		self.foreground_color = '#000000'

		self.position_text = UI.StringVar()
		self.position_label = UI.Label(self, textvariable=self.position_text, width=3, anchor=UI.E)
		self.position_label.grid(row=0, column=0, padx=(2, 4))
		self.foreground_color = self.position_label.cget('fg')
		self.position_tooltip = UI.Tooltip(self.position_label)

		self.icon_canvas = UI.Canvas(self, width=ButtonRow.ICON_WIDTH, height=ButtonRow.ICON_HEIGHT, background='#000000', highlightthickness=0, borderwidth=0, theme_tag='preview') # type: ignore[call-arg]
		self.icon_canvas.grid(row=0, column=1, pady=ButtonRow.ROW_PADDING)

		self.string_text = UI.StringVar()
		self.string_label = UI.Label(self, textvariable=self.string_text, anchor=UI.W, justify=UI.LEFT)
		self.string_label.grid(row=0, column=2, sticky=UI.EW, padx=4)
		self.grid_columnconfigure(2, weight=1)
		self.grid_rowconfigure(0, minsize=ButtonRow.ROW_HEIGHT)

		self.actions = UI.Toolbar(self)
		self.move_up_button = self.actions.add_button(Assets.get_image('up'), lambda: self.delegate.move_button(self.index, -1), 'Move Up')
		self.move_down_button = self.actions.add_button(Assets.get_image('down'), lambda: self.delegate.move_button(self.index, 1), 'Move Down')
		self.actions.add_section()
		self.delete_button = self.actions.add_button(Assets.get_image('remove'), lambda: self.delegate.delete_button(self.index), 'Delete')
		self.add_below_button = self.actions.add_button(Assets.get_image('add'), lambda: self.delegate.add_button_after(self.index), 'Add Button Below')
		# The actions are removed from the grid while hidden, so the string can use their space. Rows fill the width of the list (and have a fixed height),
		# so showing/hiding the actions only changes how much of the string is shown, never the size of the row.
		self.actions.grid(row=0, column=3, sticky=UI.E, padx=2)
		self.actions_visible = True
		self.hide_actions()
		self.bind(UI.Cursor.Enter(), self.pointer_entered)
		self.bind(UI.Cursor.Leave(), self.pointer_left)

		for widget in (self, self.position_label, self.icon_canvas, self.string_label):
			widget.bind(UI.Mouse.Click_Left(), lambda _: self.delegate.select_button(self.index))

	def set_button(self, index: int, button: Button, *, is_last: bool) -> None:
		self.index = index
		self.button = button
		self.position_text.set(str(button.position))
		if 1 <= button.position <= len(ButtonPositionCodeType.NAMES):
			self.position_tooltip.text = ButtonPositionCodeType.NAMES[button.position - 1]
		else:
			self.position_tooltip.text = 'Invalid Position'
		draw_icon(self.icon_canvas, self.delegate.button_icon(button.icon))
		self.string_text.set(self.delegate.string_text(button.enabled_string))
		self.move_up_button['state'] = UI.DISABLED if index == 0 else UI.NORMAL
		self.move_down_button['state'] = UI.DISABLED if is_last else UI.NORMAL

	# Selection

	def set_selected(self, selected: bool) -> None:
		if selected == self.selected:
			return
		self.selected = selected
		background, foreground = self.background_color, self.foreground_color
		if selected:
			style = UI.Style()
			background, foreground = style.lookup('.', 'selectbackground'), style.lookup('.', 'selectforeground')
		self.config(bg=background)
		self.color_actions(self.actions, background)
		for label in (self.position_label, self.string_label):
			label.config(bg=background, fg=foreground)

	@staticmethod
	def color_actions(widget: UI.Misc, background: str) -> None:
		# The toolbar's rows and spacers are frames behind its buttons, so they take the row's background.
		# The buttons keep their own face, only the border around them (drawn in the background behind them) is colored.
		if isinstance(widget, UI.Button):
			widget.config(highlightbackground=background)
			return
		if isinstance(widget, UI.Frame):
			widget.config(bg=background)
		for child in widget.winfo_children():
			ButtonRow.color_actions(child, background)

	# Hovering

	def pointer_entered(self, _event: UI.Event) -> None:
		self.show_actions()

	def pointer_left(self, event: UI.Event) -> None:
		# The row also gets a Leave when the pointer moves onto one of its own widgets, so the actions stay shown while the pointer is still in the row
		path = str(self.tk.call('winfo', 'containing', '-displayof', str(self), event.x_root, event.y_root))
		row_path = str(self)
		if path == row_path or path.startswith(row_path + '.'):
			return
		self.hide_actions()

	def show_actions(self) -> None:
		if not self.actions_visible:
			self.actions_visible = True
			self.actions.grid()

	def hide_actions(self) -> None:
		if self.actions_visible:
			self.actions_visible = False
			self.actions.grid_remove()

	def actions_shown(self) -> bool:
		return self.actions_visible
