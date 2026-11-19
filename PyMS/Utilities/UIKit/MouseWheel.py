
from __future__ import annotations

from .Event import Event
from .EventPattern import EventPropogation, Modifier, Mouse

import re
import tkinter
from time import monotonic

from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
	from .Components.DropDownChooser import DropDownChooser

# Routes every mouse wheel / trackpad scroll of a Tk root to exactly one widget:
# - the innermost scrollable widget under the pointer that can move in the scroll's direction (so nested scrollers chain outwards at their edges)
# - a gesture (events less than 0.3s apart, without the pointer moving) stays latched to the widget it started on, even as other content slides under the pointer
#   (Tk doesn't report when a trackpad gesture or its momentum ends, so the gesture is approximated from the event timing and pointer position)
# Scrollable widgets are found from their state, so nothing registers with the router:
# a `Text`/`Listbox`/`Treeview`, a `Canvas` with a `scrollregion` larger than its view, or a `Scrollbar` (which scrolls whatever it drives).
class MouseWheel:
	def __init__(self, root: tkinter.Tk) -> None:
		self.root = root
		# The open `DropDownChooser`, which closes when the wheel is used outside of it
		self.popup: DropDownChooser | None = None
		self._latched: dict[str, tuple[str | None, float]] = {}
		self._pointer: tuple[int, int] | None = None
		self._remainders: dict[str, float] = {}

		# Tk's own wheel bindings would scroll the widget under the pointer in addition to the router, so they are removed
		wheel_sequence = re.compile(r'MouseWheel|TouchpadScroll|Button-[45]>')
		for class_name in ('Text', 'Listbox', 'Treeview', 'Scrollbar', 'TScrollbar'):
			for sequence in root.bind_class(class_name):
				if wheel_sequence.search(sequence):
					root.unbind_class(class_name, sequence)
		# Value widgets only take the wheel while focused, otherwise it continues on to the router to scroll their container
		for class_name in ('TCombobox', 'TSpinbox'):
			for sequence in root.bind_class(class_name):
				if wheel_sequence.search(sequence):
					script = root.bind_class(class_name, sequence)
					root.tk.call('bind', class_name, sequence, f'if {{[focus] ne "%W"}} continue\n{script}\nbreak')

		self._bind(root.bind_all, None)

	# Scroll events on `source` scroll as if they happened over `target` (e.g. a line number gutter scrolling its text)
	def forward(self, source: tkinter.Misc, target: tkinter.Misc) -> None:
		self._bind(source.bind, target)

	def _bind(self, bind: Callable[..., object], widget: tkinter.Misc | None) -> None:
		bind(Mouse.Scroll(), lambda event: self._wheel(event, widget))
		bind(Mouse.TouchpadScroll(), lambda event: self._touchpad(event, widget))
		if tkinter.TkVersion < 9 and self.root.tk.call('tk', 'windowingsystem') == 'x11':
			bind(Mouse.Wheel_Up(), lambda event: self._route(event, widget, [(self._axis(event), -3, True)]))
			bind(Mouse.Wheel_Down(), lambda event: self._route(event, widget, [(self._axis(event), 3, True)]))

	def _axis(self, event: Event) -> str:
		return 'x' if isinstance(event.state, int) and event.state & Modifier.Shift.state else 'y'

	def _wheel(self, event: Event, widget: tkinter.Misc | None) -> str:
		# Tk 9 (and Windows) report 120 per notch, Tk 8.6 on macOS reports lines. A notch scrolls 3 lines.
		lines: float = -event.delta
		if tkinter.TkVersion >= 9 or self.root.tk.call('tk', 'windowingsystem') != 'aqua':
			lines /= 40
		return self._route(event, widget, [(self._axis(event), lines, True)])

	def _touchpad(self, event: Event, widget: tkinter.Misc | None) -> str:
		# The delta packs the x pixels in the high 16 bits and the signed y pixels in the low 16 bits (see `tk::PreciseScrollDeltas`)
		delta_x = event.delta >> 16
		delta_y = event.delta & 0xFFFF
		if delta_y >= 0x8000:
			delta_y -= 0x10000
		# Matches the scaling Tk applies to touchpad pixels (see `tk::ScaleNum`)
		scale = float(self.root.tk.call('tk', 'scaling')) * 0.75
		return self._route(event, widget, [('x', -delta_x * scale, False), ('y', -delta_y * scale, False)])

	# `amounts` are `(axis, amount, in_lines)`, positive amounts scroll towards the end of the content.
	# The scroll starts from `widget`, or the event's widget when `None`.
	def _route(self, event: Event, widget: tkinter.Misc | None, amounts: list[tuple[str, float, bool]]) -> str:
		path = str(widget) if widget is not None else self._pointer_widget(event)
		toplevel = self.root.tk.call('winfo', 'toplevel', path)
		if self.popup is not None and toplevel != str(self.popup):
			self.popup.close()
			return EventPropogation.Break
		now = monotonic()
		# Moving the pointer ends a gesture, so the next scroll goes to whatever is under the pointer now
		pointer = (event.x_root, event.y_root) if isinstance(event.x_root, int) and isinstance(event.y_root, int) else None
		if pointer != self._pointer and (pointer is None or self._pointer is None or max(abs(pointer[0] - self._pointer[0]), abs(pointer[1] - self._pointer[1])) > 4):
			self._latched.clear()
		self._pointer = pointer
		for axis, amount, in_lines in amounts:
			if not amount:
				continue
			latched = self._latched.get(axis)
			target: str | None
			if latched is not None and now - latched[1] < 0.3 and (latched[0] is None or (self.root.tk.getboolean(self.root.tk.call('winfo', 'exists', latched[0])) and self.root.tk.call('winfo', 'toplevel', latched[0]) == toplevel)):
				target = latched[0]
			else:
				target = self._find_target(path, axis, amount)
				self._remainders[axis] = 0.0
			self._latched[axis] = (target, now)
			if target is not None:
				self._scroll(target, axis, amount, in_lines)
		return EventPropogation.Break

	# On macOS a window resize can leave Tk delivering scroll events to a stale widget (its drag target) until the next click,
	# so the event goes to the widget actually under the pointer (the event's widget when it has no pointer position, e.g. a generated event)
	def _pointer_widget(self, event: Event) -> str:
		if isinstance(event.x_root, int) and isinstance(event.y_root, int):
			path = str(self.root.tk.call('winfo', 'containing', '-displayof', self.root, event.x_root, event.y_root))
			if path:
				return path
		return str(event.widget)

	def _find_target(self, path: str, axis: str, amount: float) -> str | None:
		while path:
			view = self._view(path, axis)
			if view is not None:
				first, last = view
				# Scrolling up/left needs content before the view, down/right needs content after it
				if (first > 0) if amount < 0 else (last < 1):
					return path
			if self.root.tk.call('winfo', 'toplevel', path) == path:
				return None
			path = self.root.tk.call('winfo', 'parent', path)
		return None

	# The `(first, last)` fractions of the content visible in a scrollable widget, or `None` if `path` is not scrollable on `axis`
	def _view(self, path: str, axis: str) -> tuple[float, float] | None:
		tk = self.root.tk
		class_name = tk.call('winfo', 'class', path)
		if class_name in ('Text', 'Listbox', 'Canvas', 'Treeview'):
			first, last = (float(fraction) for fraction in tk.splitlist(tk.call(path, f'{axis}view')))
			return (first, last)
		if class_name in ('Scrollbar', 'TScrollbar'):
			if not str(tk.call(path, 'cget', '-orient')).startswith('h' if axis == 'x' else 'v') or not str(tk.call(path, 'cget', '-command')):
				return None
			first, last = (float(fraction) for fraction in tk.splitlist(tk.call(path, 'get'))[:2])
			# An unconfigured `Scrollbar` reports `(0, 0)`
			if last <= first:
				return None
			return (first, last)
		return None

	# The pixel height (or width) a wheel notch's "line" scrolls in a widget
	def _line_size(self, path: str, class_name: str, axis: str) -> float:
		tk = self.root.tk
		if class_name in ('Text', 'Listbox'):
			font = tk.call(path, 'cget', '-font')
			if axis == 'x':
				return float(tk.call('font', 'measure', font, '0'))
			return float(tk.call('font', 'metrics', font, '-linespace'))
		if class_name == 'Treeview' and axis == 'y':
			row_height = tk.call('ttk::style', 'lookup', str(tk.call(path, 'cget', '-style')) or 'Treeview', '-rowheight')
			if str(row_height):
				return float(row_height)
		if class_name == 'Canvas':
			increment = float(tk.call('winfo', 'fpixels', path, tk.call(path, 'cget', f'-{axis}scrollincrement')))
			if increment > 0:
				return increment
		return float(tk.call('font', 'metrics', 'TkDefaultFont', '-linespace'))

	def _scroll(self, path: str, axis: str, amount: float, in_lines: bool) -> None:
		tk = self.root.tk
		class_name = tk.call('winfo', 'class', path)
		line_size = self._line_size(path, class_name, axis)
		pixels = amount * line_size if in_lines else amount
		# `Listbox` rows and vertical `Treeview` rows only scroll whole lines, while a horizontal `Treeview` unit is a pixel
		if class_name == 'Listbox' or (class_name == 'Treeview' and axis == 'y'):
			pixels /= line_size
		pixels += self._remainders.get(axis, 0.0)
		whole = int(pixels)
		self._remainders[axis] = pixels - whole
		if not whole:
			return
		if class_name == 'Text':
			tk.call(path, f'{axis}view', 'scroll', whole, 'pixels')
		elif class_name in ('Listbox', 'Treeview'):
			tk.call(path, f'{axis}view', 'scroll', whole, 'units')
		else:
			view = self._view(path, axis)
			if view is None:
				return
			first, last = view
			if class_name == 'Canvas':
				region = tk.splitlist(tk.call(path, 'cget', '-scrollregion'))
				if len(region) != 4:
					return
				start = 0 if axis == 'x' else 1
				size = float(region[start + 2]) - float(region[start])
				command = (path, f'{axis}view')
			else:
				# A `Scrollbar` can't tell the size of the content it scrolls, its visible part spans about the length of the scrollbar
				length = int(tk.call('winfo', 'width' if axis == 'x' else 'height', path))
				size = length / (last - first)
				command = tk.splitlist(tk.call(path, 'cget', '-command'))
			if size <= 0:
				return
			tk.call(*command, 'moveto', (round(first * size) + whole) / size)
