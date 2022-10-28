
try: # Python 2
	import Tkinter as _tk
except: # Python 3
	import tkinter as _tk
import inspect as _inspect

_THEME = [] # type: list[tuple[_Selector, dict[str, str | int]]]
_WIDGET_TYPES = None

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

class _Selector(object):
	def __init__(self, definition): # type: (str) -> _Selector
		global _WIDGET_TYPES
		if _WIDGET_TYPES == None:
			_resolve_widget_types()
		self.components = []
		for component in definition.split(' '):
			if not component in '**':
				component = _WIDGET_TYPES[component]
			self.components.insert(0, component)

	def is_default(self):
		return len(self.components) == 1 and self.components[0] == '*'

	def priority(self):
		if self.is_default():
			return 0
		priority = 0
		for component in self.components:
			if isinstance(component, str):
				continue
			priority += len(_inspect.getmro(component))
		return priority + 100 * len(self.components)

	def matches(self, widget): # type: (_tk.Misc) -> bool
		if self.is_default():
			return True
		component_index = 0
		wildcard = False
		while component_index < len(self.components):
			component = self.components[component_index]
			if component == '*':
				widget = widget.master
				component_index += 1
			elif component == '**':
				wildcard = True
				component_index += 1
			else:
				if isinstance(widget, component):
					widget = widget.master
					component_index += 1
					wildcard = False
				elif wildcard:
					widget = widget.master
				else:
					return False
		return True

def load_theme(name, main_window): # type: (str, _tk.Tk) -> None
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

def apply_theme(widget): # type: (_tk.Misc) -> None
	for selector,styles in _THEME:
		if selector.matches(widget):
			for key,value in styles.items():
				if not key in widget.keys():
					continue
				widget.config({key: value})
