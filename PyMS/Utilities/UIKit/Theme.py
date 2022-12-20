
from ..utils import isstr
from ..setutils import PYMS_SETTINGS

try: # Python 2
	import Tkinter as _Tk
except: # Python 3
	import tkinter as _Tk
import inspect as _inspect
import re as _re
import traceback as _traceback

class Theme(object):
	def __init__(self, name):
		self.name = name

		from .. import Assets
		import json

		try:
			with open(Assets.theme_file_path(name), 'r') as f:
				theme = json.load(f) # type: dict[str, dict[str, str | int]]
		except:
			print("Theme '%s' does not exist or has an invalid format" % name)
			print(_traceback.format_exc())
			raise

		self.author = theme.get('author', 'None')
		self.description = theme.get('description', 'None')

		self.widget_styles = [] # type: list[tuple[_Selector, dict[str, str | int]]]
		try:
			widget_styles = theme['widgets'].items()
		except:
			print("Theme '%s' missing 'widgets' or they are invalid" % name)
			print(_traceback.format_exc())
			raise
		if not widget_styles:
			print("Theme '%s' has an empty set of 'widgets'" % name)
		for selector,styles in widget_styles:
			try:
				selector = _Selector(selector)
				self.widget_styles.append((selector, styles))
			except:
				continue
		self.widget_styles.sort(key=lambda item: item[0].priority())

_THEME = None # type: Theme | None
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
		matches = isinstance(widget, self.widget_type)
		if matches and self.tag_name:
			if hasattr(widget, 'theme_tag'):
				matches = widget.theme_tag == self.tag_name
			else:
				matches = False
		return (matches, True)

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
				print("Theme selecter '%s' doesn't correspond to any matcher" % definition)
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

	def describe(self): # type: () -> str
		return ' '.join(repr(matcher) for matcher in self.matchers)

	def __repr__(self):
		return "<Theme.Selector '%s'>" % self.describe()

def load_theme(name, main_window): # type: (str, _Tk.Tk) -> None
	if not name:
		name = PYMS_SETTINGS.get('theme')
	if not name:
		return
	global _THEME

	try:
		_THEME = Theme(name)
	except:
		return

	apply_theme(main_window)

_INVALID_STYLES = []
_INVALID_SETTINGS = []
_INVALID_VALUES = {}
def apply_theme(widget): # type: (_Tk.Misc) -> None
	if not _THEME:
		return
	for selector,styles in _THEME.widget_styles:
		if selector.matches(widget):
			try:
				styles = styles.items()
			except:
				if not selector.describe() in _INVALID_SETTINGS:
					print("Theme '%s' selector '%s' has invalid settings" % (_THEME.name, selector.describe()))
					_INVALID_SETTINGS.append(selector.describe())
				continue
			for key,value in styles:
				key_type = _ALLOWED_SETTINGS.get(key)
				if not key_type:
					global _INVALID_SETTINGS
					if not key in _INVALID_SETTINGS:
						print("Theme '%s' setting '%s' invalid" % (_THEME.name, key))
						_INVALID_SETTINGS.append(key)
					continue
				if not key_type(value):
					global _INVALID_VALUES
					if not key_type in _INVALID_VALUES:
						_INVALID_VALUES[key_type] = []
					if not value in _INVALID_VALUES[key_type]:
						print("Theme '%s' value '%s' for setting '%s' invalid" % (_THEME.name, value, key))
						_INVALID_VALUES[key_type].append(value)
					continue
				if not key in widget.keys():
					continue
				widget.config({key: value})

def get_tag(kwargs): # type: (dict[str, Any]) -> tuple[dict[str, Any], str | None]
	theme_tag = kwargs.get('theme_tag')
	if 'theme_tag' in kwargs:
		del kwargs['theme_tag']
	return (kwargs, theme_tag)
