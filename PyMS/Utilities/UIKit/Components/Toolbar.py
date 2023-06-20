
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
	def __init__(self, *args, **kwargs): # type: (Any, Any) -> None
		self._buttons = {} # type: dict[str, Widget]
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

	def add_row(self): # type: () -> None
		self._row = Frame(self)
		self._row.pack(side=TOP, fill=X, pady=(0,2))

	# Radiobutton and Checkbutton may not be the same size as a Button, so we calculate the difference to adjust the sizes to match
	def _calculate_size_adjusts(self): # type: () -> None
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

	def _add_button(self, button, tooltip, identifier, tags): # type: (Widget, str, str | None, str | Sequence[str] | None) -> None
		Tooltip(button, tooltip)
		button.pack(side=LEFT)
		if identifier:
			self._buttons[identifier] = button
		if tags:
			self._tag_manager.add_item(button, tags)

	def add_button(self, icon, callback, tooltip, shortcut=None, enabled=True, identifier=None, tags=None, add_shortcut_to_tooltip=True, bind_shortcut=True): # type: (Image, Callable[[], None], str, EventPattern | None, bool, str | None, str | Sequence[str] | None, bool, bool) -> Button
		self._calculate_size_adjusts()
		size = Toolbar.BUTTON_SIZE
		button = Button(self._row, image=icon, width=size, height=size, command=callback, state=NORMAL if enabled else DISABLED)
		setattr(button, '_image', icon)
		if shortcut:
			if bind_shortcut:
				def _callback(): # type: () -> Callable[[Event], None]
					def _binding_trigger_command(_): # type: (Event) -> None
						if button['state'] == DISABLED or not button.winfo_viewable():
							return
						callback()
					return _binding_trigger_command
				self._bind_target.bind(shortcut(), _callback())
			if add_shortcut_to_tooltip:
				tooltip += ' (%s)' % shortcut.description()
		self._add_button(button, tooltip, identifier, tags)
		return button

	def add_radiobutton(self, icon, variable, value, tooltip, shortcut=None, enabled=True, identifier=None, tags=None, add_shortcut_to_tooltip=True, bind_shortcut=True): # type: (Image, Variable, Any, str, EventPattern | None, bool, str | None, str | Sequence[str] | None, bool, bool) -> Radiobutton
		self._calculate_size_adjusts()
		size = Toolbar.BUTTON_SIZE + Toolbar.RADIO_SIZE_ADJUST
		button = Radiobutton(self._row, image=icon, width=size, height=size, variable=variable, value=value, indicatoron=False, state=NORMAL if enabled else DISABLED)
		setattr(button, '_image', icon)
		if shortcut:
			if bind_shortcut:
				def _callback(): # type: () -> Callable[[Event], None]
					def _binding_trigger_radiobutton(_): # type: (Event) -> None
						if button['state'] == DISABLED or not button.winfo_viewable():
							return
						variable.set(value)
					return _binding_trigger_radiobutton
				self._bind_target.bind(shortcut(), _callback())
			if add_shortcut_to_tooltip:
				tooltip += ' (%s)' % shortcut.description()
		self._add_button(button, tooltip, identifier, tags)
		return button

	def add_checkbutton(self, icon, variable, tooltip, shortcut=None, enabled=True, identifier=None, tags=None, add_shortcut_to_tooltip=True, bind_shortcut=True, onvalue=True, offvalue=False): # type: (Image, Variable, str, EventPattern | None, bool, str | None, str | Sequence[str] | None, bool, bool, Any, Any) -> Checkbutton
		self._calculate_size_adjusts()
		size = Toolbar.BUTTON_SIZE + Toolbar.CHECK_SIZE_ADJUST
		button = Checkbutton(self._row, image=icon, width=size, height=size, variable=variable, onvalue=onvalue, offvalue=offvalue, indicatoron=False, state=NORMAL if enabled else DISABLED)
		setattr(button, '_image', icon)
		if shortcut:
			if bind_shortcut:
				def _callback(): # type: () -> Callable[[Event], None]
					def _binding_trigger_checkbutton(_): # type: (Event) -> None
						if button['state'] == DISABLED or not button.winfo_viewable():
							return
						variable.set(onvalue if variable.get() == offvalue else offvalue)
					return _binding_trigger_checkbutton
				self._bind_target.bind(shortcut(), _callback())
			if add_shortcut_to_tooltip:
				tooltip += ' (%s)' % shortcut.description()
		self._add_button(button, tooltip, identifier, tags)
		return button

	def add_spacer(self, width, flexible=False): # type: (int, bool) -> None
		return Frame(self._row, width=width).pack(side=LEFT, fill=X, expand=flexible)

	GAP_SIZE = 2
	def add_gap(self): # type: () -> None
		return self.add_spacer(Toolbar.GAP_SIZE)

	SECTION_SIZE = 10
	def add_section(self): # type: () -> None
		return self.add_spacer(Toolbar.SECTION_SIZE)

	def update_icon(self, identifier, icon): # type: (str, Image) -> None
		button = self._buttons.get(identifier)
		if not button:
			return
		button['image'] = icon
		setattr(button, '_image', icon)

	def set_enabled(self, identifier, is_enabled): # type: (str, bool) -> None
		button = self._buttons.get(identifier)
		if not button:
			return
		button['state'] = NORMAL if is_enabled else DISABLED

	def tag_enabled(self, tag, is_enabled): # type: (str, bool) -> None
		self._tag_manager.tag_enabled(tag, is_enabled)
