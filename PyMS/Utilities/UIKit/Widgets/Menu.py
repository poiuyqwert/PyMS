
from __future__ import annotations

from ..TagStateManager import TagStateManager
from .. import Theme
from .Extensions import Extensions
from ..EventPattern import EventPattern

import tkinter as _Tk

from typing import Any, Callable, Sequence

class Menu(_Tk.Menu, Extensions):
	class Item(object):
		def __init__(self, menu: Menu, index: int):
			self.menu = menu
			self.index = index

		def cget(self, option: str) -> Any:
			return self.menu.entrycget(self.index, option)

		def __getitem__(self, option: str) -> Any:
			return self.cget(option)

		def config(self, **kwargs) -> None:
			self.menu.entryconfig(self.index, **kwargs)

		def __setitem__(self, option: str, value: Any) -> None:
			self.config(**{option: value})

	def __init__(self, master: _Tk.Misc | None =None, cnf={}, **kw):
		self._items = {} # type: dict[str, Menu.Item]
		self._tag_manager = TagStateManager()
		self._cascade_menus = [] # type: list[Menu]
		_Tk.Menu.__init__(self, master, cnf, **kw)
		Theme.apply_theme(self)

	def _detect_underline(self, label: str, shortcut: EventPattern | None, kwargs: dict[str, Any]) -> None:
		underline = kwargs.get('underline')
		if isinstance(underline, int):
			return
		# Remove `underline` to handle invalid values. It will be replaced if we can determine a proper value
		if 'underline' in kwargs:
			del kwargs['underline']
		find = None 
		if isinstance(underline, str):
			find = underline
		elif shortcut is not None:
			keysym = shortcut.get_keysym()
			if not keysym:
				return
			find = keysym.value
		else:
			return
		# If we are finding a single letter, do a case insensitive search for it. Otherwise find the text case sensitive and underline the first letter of the match
		if len(find) == 1:
			find = find.lower()
			label = label.lower()
		if not find in label:
			return
		kwargs['underline'] = label.index(find)

	# Extend `add_command` to:
	#  - Optionally take an `EventPattern` as a `shortcut`, which will drive the `accelerator` and bind the shortcut to the `command`
	#  - `underline` can be determined by the `shortcut`, or can be specified as a `str` or index
	#  - The binding will automatically handle not calling the `command` if the item is disabled
	#  - Return a `Menu.Item` wrapper of the command to be able to configure it
	def add_command(self, label: str, command: Callable[[], None], shortcut: EventPattern | None = None, shortcut_widget: _Tk.Misc | None = None, enabled: bool = True, tags: str | Sequence[str] | None = None, bind_shortcut: bool = True, **kwargs) -> Menu.Item: # type: ignore[override]
		if shortcut:
			kwargs['accelerator'] = shortcut.name()
		self._detect_underline(label, shortcut, kwargs)
		_Tk.Menu.add_command(self, label=label, command=command, state=_Tk.NORMAL if enabled else _Tk.DISABLED, **kwargs)
		item = Menu.Item(self, self.index(_Tk.END) or 0)
		if shortcut and bind_shortcut:
			def _command_callback(item: Menu.Item, command: Callable[[], None]) -> Callable[[_Tk.Event], None]:
				def _binding_trigger_command(event: _Tk.Event) -> None:
					if item['state'] == _Tk.DISABLED:
						return
					command()
				return _binding_trigger_command
			shortcut_widget = shortcut_widget or self.master
			shortcut_widget.bind(shortcut(), _command_callback(item, command))
		if tags:
			self._tag_manager.add_item(item, tags)
		return item

	# Extend `add_radiobutton` to:
	#  - Optionally take an `EventPattern` as a `shortcut`, which will drive the `accelerator` and bind the shortcut to set the `variable` to `value`
	#  - `underline` can be determined by the `shortcut`, or can be specified as a `str` or index
	#  - The binding will automatically handle not setting the `variable` to `value` if the item is disabled
	#  - Return a `Menu.Item` wrapper of the radiobutton to be able to configure it
	def add_radiobutton(self, label: str, variable: _Tk.Variable, value: Any, shortcut: EventPattern | None = None, shortcut_widget: _Tk.Misc | None = None, enabled: bool = True, tags: str | Sequence[str] | None = None, bind_shortcut: bool = True, **kwargs) -> Menu.Item: # type: ignore[override]
		if shortcut:
			kwargs['accelerator'] = shortcut.name()
		self._detect_underline(label, shortcut, kwargs)
		_Tk.Menu.add_radiobutton(self, label=label, variable=variable, value=value, state=_Tk.NORMAL if enabled else _Tk.DISABLED, **kwargs)
		item = Menu.Item(self, self.index(_Tk.END) or 0)
		if shortcut and bind_shortcut:
			def _callback(item: Menu.Item, variable: _Tk.Variable, value: Any) -> Callable[[_Tk.Event], None]:
				def _binding_trigger_radiobutton(e: _Tk.Event) -> None:
					if item['state'] == _Tk.DISABLED:
						return
					variable.set(value)
				return _binding_trigger_radiobutton
			shortcut_widget = shortcut_widget or self.master
			shortcut_widget.bind(shortcut(), _callback(item, variable, value))
		if tags:
			self._tag_manager.add_item(item, tags)
		return item

	# Extend `add_checkbutton` to:
	#  - Optionally take an `EventPattern` as a `shortcut`, which will drive the `accelerator` and bind the shortcut to toggle the `variable` between `onvalue` and `offvalue`
	#  - `underline` can be determined by the `shortcut`, or can be specified as a `str` or index
	#  - The binding will automatically handle not toggling the `variable` if the item is disabled
	#  - Return a `Menu.Item` wrapper of the checkbutton to be able to configure it
	def add_checkbutton(self, label: str, variable: _Tk.Variable, onvalue: Any = True, offvalue: Any = False, shortcut: EventPattern | None = None, shortcut_widget: _Tk.Misc | None = None, enabled: bool = True, tags: str | Sequence[str] | None = None, bind_shortcut: bool = True, **kwargs) -> Menu.Item: # type: ignore[override]
		if shortcut:
			kwargs['accelerator'] = shortcut.name()
		self._detect_underline(label, shortcut, kwargs)
		_Tk.Menu.add_checkbutton(self, label=label, variable=variable, onvalue=onvalue, offvalue=offvalue, state=_Tk.NORMAL if enabled else _Tk.DISABLED, **kwargs)
		item = Menu.Item(self, self.index(_Tk.END) or 0)
		if shortcut and bind_shortcut:
			def _callback(item: Menu.Item, variable: _Tk.Variable, onvalue: Any, offvalue: Any) -> Callable[[_Tk.Event], None]:
				def _binding_trigger_checkbutton(e: _Tk.Event) -> None:
					if item['state'] == _Tk.DISABLED:
						return
					variable.set(onvalue if variable.get() == offvalue else offvalue)
				return _binding_trigger_checkbutton
			shortcut_widget = shortcut_widget or self.master
			shortcut_widget.bind(shortcut(), _callback(item, variable, onvalue, offvalue))
		if tags:
			self._tag_manager.add_item(item, tags)
		return item

	# Extend `add_cascade` to:
	#  - Generate a `Menu` if none is specified and return in
	#  - Remember its children so `tag_enabled` will apply recursively
	def add_cascade(self, label: str, menu: Menu | None = None, **kwargs) -> Menu: # type: ignore[override]
		if not menu:
			menu = Menu(self, tearoff=kwargs.get('tearoff', 0))
		_Tk.Menu.add_cascade(self, label=label, menu=menu, **kwargs)
		self._cascade_menus.append(menu)
		return menu

	def tag_enabled(self, tag: str, is_enabled: bool) -> None:
		self._tag_manager.tag_enabled(tag, is_enabled)
		for menu in self._cascade_menus:
			menu.tag_enabled(tag, is_enabled)
