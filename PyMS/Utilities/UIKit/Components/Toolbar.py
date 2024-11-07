
from .Tooltip import Tooltip
from ..Widgets import *
from ..TagStateManager import TagStateManager
from ..EventPattern import EventPattern

from typing import Any, Callable, Sequence

class Toolbar(Frame):
	BUTTON_SIZE = 20
	RADIO_SIZE_ADJUST = -1
	CHECK_SIZE_ADJUST = -1

	# Use `bind_target=<widget>` to adjust where shortcuts are bound, otherwise `self.master` will be used
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		self._buttons: dict[str, Widget] = {}
		self._tag_manager = TagStateManager()
		self._bind_target: Misc
		if 'bind_target' in kwargs:
			self._bind_target = kwargs['bind_target']
			del kwargs['bind_target']
		Frame.__init__(self, *args, **kwargs)
		if not 'bind_target' in kwargs:
			self._bind_target = self.master
		self._row: Frame
		self.add_row()

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

	def add_button(self, icon: Image, callback: Callable[[], None], tooltip: str, shortcut: EventPattern | None = None, enabled: bool = True, identifier: str | None = None, tags: str | Sequence[str] | None = None, add_shortcut_to_tooltip: bool = True, bind_shortcut: bool = True) -> Button:
		self._calculate_size_adjusts()
		size = Toolbar.BUTTON_SIZE
		button = Button(self._row, image=icon, width=size, height=size, command=callback, state=NORMAL if enabled else DISABLED)
		setattr(button, '_image', icon)
		if shortcut:
			if bind_shortcut:
				def _callback() -> Callable[[Event], None]:
					def _binding_trigger_command(_: Event) -> None:
						if button['state'] == DISABLED or not button.winfo_viewable():
							return
						callback()
					return _binding_trigger_command
				self._bind_target.bind(shortcut(), _callback())
			if add_shortcut_to_tooltip:
				tooltip += ' (%s)' % shortcut.description()
		self._add_button(button, tooltip, identifier, tags)
		return button

	def add_radiobutton(self, icon: Image, variable: Variable, value: Any, tooltip: str, shortcut: EventPattern | None = None, enabled: bool = True, identifier: str | None = None, tags: str | Sequence[str] | None = None, add_shortcut_to_tooltip: bool = True, bind_shortcut: bool = True) -> Radiobutton:
		self._calculate_size_adjusts()
		size = Toolbar.BUTTON_SIZE + Toolbar.RADIO_SIZE_ADJUST
		button = Radiobutton(self._row, image=icon, width=size, height=size, variable=variable, value=value, indicatoron=False, state=NORMAL if enabled else DISABLED)
		setattr(button, '_image', icon)
		if shortcut:
			if bind_shortcut:
				def _callback() -> Callable[[Event], None]:
					def _binding_trigger_radiobutton(_: Event) -> None:
						if button['state'] == DISABLED or not button.winfo_viewable():
							return
						variable.set(value)
					return _binding_trigger_radiobutton
				self._bind_target.bind(shortcut(), _callback())
			if add_shortcut_to_tooltip:
				tooltip += ' (%s)' % shortcut.description()
		self._add_button(button, tooltip, identifier, tags)
		return button

	def add_checkbutton(self, icon: Image, variable: Variable, tooltip: str, shortcut: EventPattern | None = None, enabled: bool = True, identifier: str | None = None, tags: str | Sequence[str] | None = None, add_shortcut_to_tooltip: bool = True, bind_shortcut: bool = True, onvalue: Any = True, offvalue: Any = False) -> Checkbutton:
		self._calculate_size_adjusts()
		size = Toolbar.BUTTON_SIZE + Toolbar.CHECK_SIZE_ADJUST
		button = Checkbutton(self._row, image=icon, width=size, height=size, variable=variable, onvalue=onvalue, offvalue=offvalue, indicatoron=False, state=NORMAL if enabled else DISABLED)
		setattr(button, '_image', icon)
		if shortcut:
			if bind_shortcut:
				def _callback() -> Callable[[Event], None]:
					def _binding_trigger_checkbutton(_: Event) -> None:
						if button['state'] == DISABLED or not button.winfo_viewable():
							return
						variable.set(onvalue if variable.get() == offvalue else offvalue)
					return _binding_trigger_checkbutton
				self._bind_target.bind(shortcut(), _callback())
			if add_shortcut_to_tooltip:
				tooltip += ' (%s)' % shortcut.description()
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

	def update_icon(self, identifier: str, icon: Image) -> None:
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
