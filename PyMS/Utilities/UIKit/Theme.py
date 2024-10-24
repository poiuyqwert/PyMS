
from __future__ import annotations

import tkinter as _Tk
import inspect as _inspect
import re as _re
import traceback as _traceback

from typing import Any, Callable, Type

class Theme(object):
	def __init__(self, name: str) -> None:
		self.name = name

		from .. import Assets
		import json

		try:
			with open(Assets.theme_file_path(name), 'r') as f:
				theme: dict[str, str | dict[str, dict[str, str | int]]] = json.load(f)
		except:
			print(("Theme '%s' does not exist or has an invalid format" % name))
			print((_traceback.format_exc()))
			raise

		self.author = str(theme.get('author', 'None'))
		self.description = str(theme.get('description', 'None'))

		self.widget_styles: list[tuple[_Selector, dict[str, str | int]]] = []
		try:
			widgets = theme['widgets']
			if not isinstance(widgets, dict):
				raise Exception()
			widget_styles = list(widgets.items())
		except:
			print(("Theme '%s' missing 'widgets' or it is invalid" % name))
			print((_traceback.format_exc()))
			raise
		if not widget_styles:
			print(("Theme '%s' has an empty set of 'widgets'" % name))
		for selector_def,styles in widget_styles:
			try:
				selector = _Selector(selector_def)
				self.widget_styles.append((selector, styles))
			except:
				continue
		self.widget_styles.sort(key=lambda item: item[0].priority())
		
		colors = theme.get('colors')
		self.colors = None
		if isinstance(colors, dict):
			self.colors = colors
		elif colors:
			print(("Theme '%s' has invalid 'colors'" % name))

_THEME: Theme | None = None
_WIDGET_TYPES: dict[str, Type[_Tk.Misc]] | None = None

class _SettingType(object):
	@staticmethod
	def integer(value: Any) -> bool:
		return isinstance(value, int)

	RE_COLOR = _re.compile(r'#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})')
	@staticmethod
	def color(value):
		# TODO: Support color names?
		if not isinstance(value, str):
			return False
		return not not _SettingType.RE_COLOR.match(value)

	@staticmethod
	def relief(value):
		return value in ('raised', 'sunken', 'flat', 'ridge', 'solid', 'groove')

	@staticmethod
	def anchor(value):
		return value in ('n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center')

	@staticmethod
	def active_style(value):
		return value in ('dotbox', 'none', 'underline')

_ALLOWED_SETTINGS: dict[str, Callable[[Any], bool]] = {
	'activebackground': _SettingType.color,
	'activeborderwidth': _SettingType.integer,
	'activeforeground': _SettingType.color,
	'activestyle': _SettingType.active_style,
	'background': _SettingType.color,
	'borderwidth': _SettingType.integer,
	'disabledbackground': _SettingType.color,
	'disabledforeground': _SettingType.color,
	'foreground': _SettingType.color,
	'highlightbackground': _SettingType.color,
	'highlightcolor': _SettingType.color,
	'highlightthickness': _SettingType.integer,
	'inactiveselectbackground': _SettingType.color,
	'insertbackground': _SettingType.color,
	'insertborderwidth': _SettingType.integer,
	'insertofftime': _SettingType.integer,
	'insertontime': _SettingType.integer,
	'insertwidth': _SettingType.integer,
	# 'labelanchor': _SettingType.anchor,
	'offrelief': _SettingType.relief,
	'overrelief': _SettingType.relief,
	'readonlybackground': _SettingType.color,
	'relief': _SettingType.relief,
	'selectbackground': _SettingType.color,
	'selectborderwidth': _SettingType.integer,
	'selectcolor': _SettingType.color,
	'selectforeground': _SettingType.color,
	'troughcolor': _SettingType.color,
}

def _resolve_widget_types() -> None:
	global _WIDGET_TYPES
	from . import Widgets
	_WIDGET_TYPES = {
		'Tk': Widgets.Tk,
		'Toplevel': Widgets.Toplevel,
		'Frame': Widgets.Frame,
		'Button': Widgets.Button,
		'Checkbutton': Widgets.Checkbutton,
		'Radiobutton': Widgets.Radiobutton,
		'Label': Widgets.Label,
		'Text': Widgets.Text,
		'Entry': Widgets.Entry,
		'Canvas': Widgets.Canvas,
		'Listbox': Widgets.Listbox,
		'Menu': Widgets.Menu,
		'Scrollbar': Widgets.Scrollbar,
		'LabelFrame': Widgets.LabelFrame,
		'PanedWindow': Widgets.PanedWindow,
	}
	from . import Components
	_WIDGET_TYPES.update({
		'AutohideScrollbar': Components.AutohideScrollbar,
		'CodeText': Components.CodeText,
		'CollapseView': Components.CollapseView,
		'DropDown': Components.DropDown,
		'EntryDropDown': Components.EntryDropDown,
		'FlowView': Components.FlowView,
		'Hotlink': Components.Hotlink,
		'MainWindow': Components.MainWindow,
		'MaskedCheckbutton': Components.MaskedCheckbutton,
		'MaskedRadiobutton': Components.MaskedRadiobutton,
		'NotebookTab': Components.NotebookTab,
		'Notebook': Components.Notebook,
		'ReportList': Components.ReportList,
		'RichList': Components.RichList,
		'ScrolledCanvas': Components.ScrolledCanvas,
		'ScrolledListbox': Components.ScrolledListbox,
		'ScrollView': Components.ScrollView,
		'StatusBar': Components.StatusBar,
		'TextDropDown': Components.TextDropDown,
		# 'TextTooltip': Components.TextTooltip,
		# 'TextDynamicTooltip': Components.TextDynamicTooltip,
		'Toolbar': Components.Toolbar,
		'Tooltip': Components.TooltipWindow,
		'TreeList': Components.TreeList,
	})

class _Priority:
	program_specific = 1000
	tag_specific = 10
	depth_specific = 100

class _Matcher(object):
	class Result(object):
		def __init__(self, success: bool, consume_widget: bool) -> None:
			self.success = success
			self.consume_widget = consume_widget

	@classmethod
	def parse(cls, token: str) -> _Matcher | None:
		matcher_types: list[Type[_Matcher]] = [_ProgramMatcher, _WidgetMatcher, _WildcardMatcher]
		for matcher_type in matcher_types:
			matcher = matcher_type.parse(token)
			if matcher:
				return matcher
		return None

	def priority(self) -> int:
		raise NotImplementedError(self.__class__.__name__ + '.priority()')

	def matches(self, widget: _Tk.Misc) -> _Matcher.Result:
		raise NotImplementedError(self.__class__.__name__ + '.matches()')

	def __repr__(self) -> str:
		raise NotImplementedError(self.__class__.__name__ + '.__repr__()')

class _ProgramMatcher(_Matcher):
	PARSE_RE = _re.compile(r'\[(\w+)\]')
	@classmethod
	def parse(cls, token: str) -> _ProgramMatcher | None:
		match = _ProgramMatcher.PARSE_RE.match(token)
		if not match:
			return None
		return _ProgramMatcher(match.group(1))

	def __init__(self, program_name: str) -> None:
		self.program_name = program_name

	def priority(self) -> int:
		return _Priority.program_specific

	def matches(self, widget: _Tk.Misc) -> _Matcher.Result:
		return _Matcher.Result(True, False)

	def __repr__(self) -> str:
		return '[%s]' % self.program_name

class _WidgetMatcher(_Matcher):
	PARSE_RE = _re.compile(r'(\w+)(?:\.(\w+))?')
	@classmethod
	def parse(cls, token: str) -> _WidgetMatcher | None:
		match = _WidgetMatcher.PARSE_RE.match(token)
		if not match or not _WIDGET_TYPES:
			return None
		widget_type = _WIDGET_TYPES.get(match.group(1))
		if not widget_type:
			return None
		return _WidgetMatcher(widget_type, match.group(2))

	def __init__(self, widget_type: Type[_Tk.Misc], tag_name: str | None) -> None:
		self.widget_type = widget_type
		self.tag_name = tag_name

	def priority(self) -> int:
		priority = len(_inspect.getmro(self.widget_type))
		if self.tag_name:
			priority += _Priority.tag_specific
		return priority

	def matches(self, widget: _Tk.Misc) -> _Matcher.Result:
		matches = isinstance(widget, self.widget_type)
		if matches and self.tag_name:
			if hasattr(widget, 'theme_tag'):
				matches = widget.theme_tag == self.tag_name
			else:
				matches = False
		return _Matcher.Result(matches, True)

	def __repr__(self) -> str:
		return self.widget_type.__name__ + ('.%s' % self.tag_name if self.tag_name else '')

class _WildcardMatcher(_Matcher):
	@classmethod
	def parse(cls, token: str) -> _WildcardMatcher | None:
		if not token in '**':
			return None
		return _WildcardMatcher(token == '**')

	def __init__(self, many: bool) -> None:
		self.many = many

	def priority(self) -> int:
		return 0

	def matches(self, widget: _Tk.Misc) -> _Matcher.Result:
		return _Matcher.Result(True, True)

	def __repr__(self):
		return '*' + ('*' if self.many else '')

class _Selector(object):
	def __init__(self, definition: str) -> None:
		if _WIDGET_TYPES is None:
			_resolve_widget_types()
		self.matchers: list[_Matcher] = []
		for component in definition.split(' '):
			matcher = _Matcher.parse(component)
			if not matcher:
				print(("Theme selecter '%s' doesn't correspond to any matcher" % definition))
				raise Exception() # TODO: Error handling
			self.matchers.append(matcher)

	def is_default(self) -> bool:
		return len(self.matchers) == 1 and isinstance(self.matchers[0], _WildcardMatcher) and not self.matchers[0].many

	def priority(self) -> int:
		priority = _Priority.depth_specific * len(self.matchers)
		for matcher in self.matchers:
			priority += matcher.priority()
		return priority

	def matches(self, _widget: _Tk.Misc) -> bool:
		if self.is_default():
			return True
		matcher_index = -1
		wildcard = False
		widget: _Tk.Misc | None = _widget
		while matcher_index >= -len(self.matchers):
			if widget is None:
				return False
			matcher = self.matchers[matcher_index]
			if isinstance(matcher, _WildcardMatcher):
				if matcher.many:
					wildcard = True
					matcher_index -= 1
				else:
					widget = widget.master
					matcher_index -= 1
			else:
				result = matcher.matches(widget)
				if result.success:
					if result.consume_widget:
						widget = widget.master
					matcher_index -= 1
					wildcard = False
				elif wildcard:
					widget = widget.master
				else:
					return False
		return True

	def describe(self) -> str:
		return ' '.join(repr(matcher) for matcher in self.matchers)

	def __repr__(self) -> str:
		return "<Theme.Selector '%s'>" % self.describe()

def load_theme(name: str | None, main_window: _Tk.Tk) -> None:
	if not name:
		from ..PyMSConfig import PYMS_CONFIG
		name = PYMS_CONFIG.theme.value
	if not name:
		return
	global _THEME

	try:
		_THEME = Theme(name)
	except:
		return

	apply_theme(main_window)

_INVALID_SETTINGS: list[str] = []
_INVALID_VALUES: dict[Callable[[Any], bool], list[str | int]] = {}
def apply_theme(widget: _Tk.Misc) -> None:
	if not _THEME:
		return
	for selector,styles_dict in _THEME.widget_styles:
		if selector.matches(widget):
			try:
				styles = list(styles_dict.items())
			except:
				if not selector.describe() in _INVALID_SETTINGS:
					print(("Theme '%s' selector '%s' has invalid settings" % (_THEME.name, selector.describe())))
					_INVALID_SETTINGS.append(selector.describe())
				continue
			for key,value in styles:
				key_type = _ALLOWED_SETTINGS.get(key)
				if not key_type:
					if not key in _INVALID_SETTINGS:
						print(("Theme '%s' setting '%s' is invalid" % (_THEME.name, key)))
						_INVALID_SETTINGS.append(key)
					continue
				if not key_type(value):
					if not key_type in _INVALID_VALUES:
						_INVALID_VALUES[key_type] = []
					if not value in _INVALID_VALUES[key_type]:
						print(("Theme '%s' value '%s' for setting '%s' is invalid" % (_THEME.name, value, key)))
						_INVALID_VALUES[key_type].append(value)
					continue
				if not key in list(widget.keys()):
					continue
				widget.configure({key: value})

def get_tag(kwargs: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
	theme_tag = kwargs.get('theme_tag')
	if 'theme_tag' in kwargs:
		del kwargs['theme_tag']
	return (kwargs, theme_tag)

_INVALID_COLORS: list[str] = []
def get_color(*keys: str, default: str = '#000000') -> str:
	if not _THEME or not _THEME.colors:
		return default
	colors: dict = _THEME.colors
	color: str
	for key in keys:
		# if not isinstance(colors, dict):
		# 	colors = None
		# 	break
		value = colors.get(key)
		if isinstance(value, str):
			color = value
			break
		elif isinstance(value, dict):
			colors = value
			continue
		else:
			return default
	if not _SettingType.color(color):
		name = '.'.join(keys)
		if not name in _INVALID_COLORS:
			print(("Theme '%s' has invalid/missing color '%s'" % (_THEME.name, name)))
			_INVALID_COLORS.append(name)
		return default
	return color
