
from .Tooltip import Tooltip
from ..Widgets import Button, Checkbutton, Frame, Misc, Radiobutton, Tk, Toplevel, Widget
from ..Constants import DISABLED, LEFT, NORMAL, TOP, X
from ..Variables import Variable
from ..Images import PhotoImage
from ..Event import Event
from ..TagStateManager import TagStateManager
from ..EventPattern import EventPattern, EventPropogation

from typing import Any, Callable, Sequence

class Toolbar(Frame):
	BUTTON_SIZE = 20
	RADIO_SIZE_ADJUST = -1
	CHECK_SIZE_ADJUST = -1

	# Use `bind_target=<widget>` to adjust where shortcuts are bound, otherwise `self.master` will be used
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		self._buttons: dict[str, Widget] = {}
		self._tag_manager = TagStateManager()
		bind_target: Misc | None = kwargs.pop('bind_target', None)
		Frame.__init__(self, *args, **kwargs)
		self._bind_target: Misc = self.master if bind_target is None else bind_target
		self._row: Frame
		self.add_row()

	# Shortcuts bound on a widget (not a window) break after triggering, so the class bindings of a widget they're bound on (like a Text transposing on Ctrl+T) don't also run.
	# Shortcuts bound on a window don't break, leaving the `all` bindings to run as they always have.
	def _shortcut_result(self) -> str | None:
		if isinstance(self._bind_target, (Tk, Toplevel)):
			return None
		return EventPropogation.Break

	def add_row(self) -> None:
		self._row = Frame(self)
		self._row.pack(side=TOP, fill=X, pady=(0,2))

	# Radiobutton and Checkbutton may not be the same size as a Button, so we calculate the difference to adjust the sizes to match
	def _calculate_size_adjusts(self) -> None:
		if Toolbar.RADIO_SIZE_ADJUST > -1:
			return
		from ... import Assets
		icon = Assets.get_image('open')
		if icon:
			button_size = Button(None, image=icon, width=20, height=20).winfo_reqheight()
			radio_size = Radiobutton(None, image=icon, width=20, height=20, indicatoron=False).winfo_reqheight()
			check_size = Checkbutton(None, image=icon, width=20, height=20, indicatoron=False).winfo_reqheight()
		else:
			button_size = 20
			radio_size = 20
			check_size = 20
		Toolbar.RADIO_SIZE_ADJUST = button_size - radio_size
		Toolbar.CHECK_SIZE_ADJUST = button_size - check_size

	def _add_button(self, button: Widget, tooltip: str, identifier: str | None, tags: str | Sequence[str] | None) -> None:
		Tooltip(button, tooltip)
		button.pack(side=LEFT)
		if identifier:
			self._buttons[identifier] = button
		if tags:
			self._tag_manager.add_item(button, tags)

	def add_button(self, icon: PhotoImage, callback: Callable[[], None], tooltip: str, shortcut: EventPattern | None = None, enabled: bool = True, identifier: str | None = None, tags: str | Sequence[str] | None = None, add_shortcut_to_tooltip: bool = True, bind_shortcut: bool = True) -> Button: # pylint: disable=too-many-positional-arguments
		self._calculate_size_adjusts()
		size = Toolbar.BUTTON_SIZE
		button = Button(self._row, image=icon, width=size, height=size, command=callback, state=NORMAL if enabled else DISABLED)
		setattr(button, '_image', icon)
		if shortcut:
			if bind_shortcut:
				def _callback() -> Callable[[Event], str | None]:
					def _binding_trigger_command(_: Event) -> str | None:
						if button['state'] == DISABLED or not button.winfo_viewable():
							return self._shortcut_result()
						callback()
						return self._shortcut_result()
					return _binding_trigger_command
				self._bind_target.bind(shortcut(), _callback())
			if add_shortcut_to_tooltip:
				tooltip += f' ({shortcut.description()})'
		self._add_button(button, tooltip, identifier, tags)
		return button

	def add_radiobutton(self, icon: PhotoImage, variable: Variable, value: Any, tooltip: str, shortcut: EventPattern | None = None, enabled: bool = True, identifier: str | None = None, tags: str | Sequence[str] | None = None, add_shortcut_to_tooltip: bool = True, bind_shortcut: bool = True) -> Radiobutton: # pylint: disable=too-many-positional-arguments
		self._calculate_size_adjusts()
		size = Toolbar.BUTTON_SIZE + Toolbar.RADIO_SIZE_ADJUST
		button = Radiobutton(self._row, image=icon, width=size, height=size, variable=variable, value=value, indicatoron=False, state=NORMAL if enabled else DISABLED)
		setattr(button, '_image', icon)
		if shortcut:
			if bind_shortcut:
				def _callback() -> Callable[[Event], str | None]:
					def _binding_trigger_radiobutton(_: Event) -> str | None:
						if button['state'] == DISABLED or not button.winfo_viewable():
							return self._shortcut_result()
						variable.set(value)
						return self._shortcut_result()
					return _binding_trigger_radiobutton
				self._bind_target.bind(shortcut(), _callback())
			if add_shortcut_to_tooltip:
				tooltip += f' ({shortcut.description()})'
		self._add_button(button, tooltip, identifier, tags)
		return button

	def add_checkbutton(self, icon: PhotoImage, variable: Variable, tooltip: str, shortcut: EventPattern | None = None, enabled: bool = True, identifier: str | None = None, tags: str | Sequence[str] | None = None, add_shortcut_to_tooltip: bool = True, bind_shortcut: bool = True, onvalue: Any = True, offvalue: Any = False) -> Checkbutton: # pylint: disable=too-many-positional-arguments
		self._calculate_size_adjusts()
		size = Toolbar.BUTTON_SIZE + Toolbar.CHECK_SIZE_ADJUST
		button = Checkbutton(self._row, image=icon, width=size, height=size, variable=variable, onvalue=onvalue, offvalue=offvalue, indicatoron=False, state=NORMAL if enabled else DISABLED)
		setattr(button, '_image', icon)
		if shortcut:
			if bind_shortcut:
				def _callback() -> Callable[[Event], str | None]:
					def _binding_trigger_checkbutton(_: Event) -> str | None:
						if button['state'] == DISABLED or not button.winfo_viewable():
							return self._shortcut_result()
						variable.set(onvalue if variable.get() == offvalue else offvalue)
						return self._shortcut_result()
					return _binding_trigger_checkbutton
				self._bind_target.bind(shortcut(), _callback())
			if add_shortcut_to_tooltip:
				tooltip += f' ({shortcut.description()})'
		self._add_button(button, tooltip, identifier, tags)
		return button

	def add_spacer(self, width: int, flexible: bool = False) -> None:
		return Frame(self._row, width=width).pack(side=LEFT, fill=X, expand=flexible)

	GAP_SIZE = 2
	def add_gap(self) -> None:
		return self.add_spacer(Toolbar.GAP_SIZE)

	SECTION_SIZE = 10
	def add_section(self) -> None:
		return self.add_spacer(Toolbar.SECTION_SIZE)

	def update_icon(self, identifier: str, icon: PhotoImage) -> None:
		button = self._buttons.get(identifier)
		if not button:
			return
		button['image'] = icon
		setattr(button, '_image', icon)

	def set_enabled(self, identifier: str, is_enabled: bool) -> None:
		button = self._buttons.get(identifier)
		if not button:
			return
		button['state'] = NORMAL if is_enabled else DISABLED

	def tag_enabled(self, tag: str, is_enabled: bool) -> None:
		self._tag_manager.tag_enabled(tag, is_enabled)

	def tag_is_enabled(self, tag: str) -> bool:
		return self._tag_manager.is_enabled(tag)
