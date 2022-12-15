
from ..utils import isstr

try: # Python 2
	import Tkinter as _Tk
except: # Python 3
	import tkinter as _Tk
import inspect as _inspect
import re as _re

_THEME = [] # type: list[tuple[_Selector, dict[str, str | int]]]
_WIDGET_TYPES = None

class _SettingType(object):
	@staticmethod
	def integer(value):
		return isinstance(value, int)

	RE_COLOR = _re.compile(r'#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})')
	@staticmethod
	def color(value):
		# TODO: Support color names?
		if not isstr(value):
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

# TODO: Proper types for things like `relief` and `anchor` settings
_ALLOWED_SETTINGS = {
	'activeborderwidth': _SettingType.integer,
	'activeforeground': _SettingType.color,
	'activestyle': _SettingType.active_style,
	'background': _SettingType.color,
	'bg': _SettingType.color,
	'borderwidth': _SettingType.integer,
	'bd': _SettingType.integer,
	'disabledbackground': _SettingType.color,
	'disabledforeground': _SettingType.color,
	'foreground': _SettingType.color,
	'fg': _SettingType.color,
	'highlightbackground': _SettingType.color,
	'highlightcolor': _SettingType.color,
	'highlightthickness': _SettingType.integer,
	'inactiveselectbackground': _SettingType.color,
	'insertbackground': _SettingType.color,
	'insertborderwidth': _SettingType.integer,
	'insertofftime': _SettingType.integer,
	'insertontime': _SettingType.integer,
	'insertwidth': _SettingType.integer,
	'labelanchor': _SettingType.anchor,
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

def _resolve_widget_types():
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
		'TextTooltip': Components.TextTooltip,
		'TextDynamicTooltip': Components.TextDynamicTooltip,
		'Toolbar': Components.Toolbar,
		'Tooltip': Components.Tooltip,
		'TreeList': Components.TreeList,
	})

class _Priority:
	program_specific = 1000
	tag_specific = 10
	depth_specific = 100

class _Matcher(object):
	class Result(object):
		def __init__(self, success, consume_widget): # type: (bool, bool) -> _Matcher.Result
			self.success = success
			self.consume_widget = consume_widget

	@classmethod
	def parse(cls, token): # type: (str) -> (_Matcher | None)
		matcher_types = [_ProgramMatcher, _WidgetMatcher, _WildcardMatcher]
		for matcher_type in matcher_types:
			matcher = matcher_type.parse(token)
			if matcher:
				return matcher
		return None

	def priority(self): # type: () -> int
		raise NotImplementedError(self.__class__.__name__ + '.priority()')

	def matches(self, widget): # type: (_Tk.Widget) -> _Matcher.Result
		raise NotImplementedError(self.__class__.__name__ + '.matches()')

	def __repr__(self):
		raise NotImplementedError(self.__class__.__name__ + '.__repr__()')

class _ProgramMatcher(_Matcher):
	PARSE_RE = _re.compile(r'\[(\w+)\]')
	@classmethod
	def parse(cls, token): # type: (str) -> (_ProgramMatcher | None)
		match = _ProgramMatcher.PARSE_RE.match(token)
		if not match:
			return None
		return _ProgramMatcher(match.group(1))

	def __init__(self, program_name): # type: (str) -> _ProgramMatcher
		self.program_name = program_name

	def priority(self):
		return _Priority.program_specific

	def matches(self, widget): # type: (_Tk.Widget) -> _Matcher.Result
		return _Matcher.Result(True, False)

	def __repr__(self):
		return '[%s]' % self.program_name

class _WidgetMatcher(_Matcher):
	PARSE_RE = _re.compile(r'(\w+)(?:\.(\w+))?')
	@classmethod
	def parse(cls, token): # type: (str) -> (_WidgetMatcher | None)
		match = _WidgetMatcher.PARSE_RE.match(token)
		if not match:
			return None
		widget_type = _WIDGET_TYPES.get(match.group(1))
		if not widget_type:
			return None
		return _WidgetMatcher(widget_type, match.group(2))

	def __init__(self, widget_type, tag_name): # type: (Type[_Tk.Widget], str | None) -> _WidgetMatcher
		self.widget_type = widget_type
		self.tag_name = tag_name

	def priority(self):
		priority = len(_inspect.getmro(self.widget_type))
		if self.tag_name:
			priority += _Priority.tag_specific
		return priority

	def matches(self, widget): # type: (_Tk.Widget) -> _Matcher.Result
		return (isinstance(widget, self.widget_type), True)

	def __repr__(self):
		return self.widget_type.__name__ + ('.%s' % self.tag_name if self.tag_name else '')

class _WildcardMatcher(_Matcher):
	@classmethod
	def parse(cls, token): # type: (str) -> (_WildcardMatcher | None)
		if not token in '**':
			return None
		return _WildcardMatcher(token == '**')

	def __init__(self, many): # type: (bool) -> _WildcardMatcher
		self.many = many

	def priority(self):
		return 0

	def matches(self, widget): # type: (_Tk.Widget) -> _Matcher.Result
		return _Matcher.Result(True, True)

	def __repr__(self):
		return '*' + ('*' if self.many else '')

class _Selector(object):
	def __init__(self, definition): # type: (str) -> _Selector
		global _WIDGET_TYPES
		if _WIDGET_TYPES == None:
			_resolve_widget_types()
		self.matchers = [] # type: list[_Matcher]
		for component in definition.split(' '):
			matcher = _Matcher.parse(component)
			if not matcher:
				raise Exception() # TODO: Error handling
			self.matchers.append(matcher)

	def is_default(self):
		return len(self.matchers) == 1 and isinstance(self.matchers[0], _WildcardMatcher) and not self.matchers[0].many

	def priority(self):
		priority = _Priority.depth_specific * len(self.matchers)
		for matcher in self.matchers:
			priority += matcher.priority()
		return priority

	def matches(self, widget): # type: (_Tk.Widget) -> bool
		if self.is_default():
			return True
		matcher_index = -1
		wildcard = False
		while matcher_index >= -len(self.matchers):
			matcher = self.matchers[matcher_index]
			if isinstance(matcher, _WildcardMatcher):
				if matcher.many:
					wildcard = True
					matcher_index -= 1
				else:
					widget = widget.master
					matcher_index -= 1
			else:
				success,consume_widget = matcher.matches(widget)
				if success:
					if consume_widget:
						widget = widget.master
					matcher_index -= 1
					wildcard = False
				elif wildcard:
					widget = widget.master
				else:
					return False
		return True

	def __repr__(self):
		return "<Theme.Selector '%s'>" % ' '.join(repr(matcher) for matcher in self.matchers)

def load_theme(name, main_window): # type: (str, _Tk.Tk) -> None
	global _THEME
	_THEME = []

	from .. import Assets
	import json

	try:
		with open(Assets.theme_file_path(name), 'r') as f:
			theme = json.load(f) # type: dict[str, dict[str, str | int]]
	except:
		raise # TODO: Handle better?

	for selector,styles in theme.items():
		try:
			selector = _Selector(selector)
			_THEME.append((selector, styles))
		except:
			raise # TODO: Handle better?
	_THEME.sort(key=lambda item: item[0].priority())

	apply_theme(main_window)

def apply_theme(widget): # type: (_Tk.Misc) -> None
	for selector,styles in _THEME:
		if selector.matches(widget):
			for key,value in styles.items():
				key_type = _ALLOWED_SETTINGS.get(key)
				if not key_type:
					continue
				if not key_type(value):
					continue
				if not key in widget.keys():
					continue
				widget.config({key: value})
