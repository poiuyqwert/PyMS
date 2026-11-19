
from ..harness import UITestCase

from ...Utilities import UIKit as UI
from ...Utilities.UIKit.Components.DropDownChooser import DropDownChooser

from unittest import mock


def _touchpad_delta(delta_x: int, delta_y: int) -> int:
	# `TouchpadScroll` packs the x pixels in the high 16 bits and the signed y pixels in the low 16 bits
	return (delta_x << 16) | (delta_y & 0xFFFF)


class Test_MouseWheel(UITestCase):
	def setUp(self) -> None:
		super().setUp()
		# The clock stands still, so all wheel events in a test are one gesture until `self.now` moves past the latch time
		self.now = 0.0
		patcher = mock.patch('PyMS.Utilities.UIKit.MouseWheel.monotonic', side_effect=lambda: self.now)
		patcher.start()
		self.addCleanup(patcher.stop)

	def _scroll_view(self) -> tuple[UI.MainWindow, UI.ScrollView, UI.Label, UI.Text]:
		window = self.make_window(UI.MainWindow)
		window.geometry('300x300')
		scroll_view = UI.ScrollView(window)
		scroll_view.pack(fill=UI.BOTH, expand=1)
		label = UI.Label(scroll_view.content_view, text='top')
		label.pack()
		for n in range(30):
			UI.Label(scroll_view.content_view, text=f'row {n}').pack()
		text = UI.Text(scroll_view.content_view, height=5)
		text.insert('1.0', '\n'.join(str(n) for n in range(50)))
		text.pack()
		for n in range(30):
			UI.Label(scroll_view.content_view, text=f'row {n}').pack()
		self.pump(window)
		return (window, scroll_view, label, text)

	def _canvas(self, view: UI.ScrollView | UI.FlowView) -> UI.Canvas:
		# The canvas scrolling the view's content
		return next(child for child in view.winfo_children() if isinstance(child, UI.Canvas))

	def _wheel(self, widget: UI.Misc, delta: int, pattern: UI.EventPattern = UI.Mouse.Scroll) -> None:
		widget.event_generate(pattern(), delta=delta)
		self.pump(widget)

	def test_wheel_over_a_child_scrolls_the_scroll_view(self) -> None:
		_, scroll_view, label, text = self._scroll_view()
		self._wheel(label, -120)
		self.assertGreater(self._canvas(scroll_view).yview()[0], 0)
		self.assertEqual(text.yview()[0], 0)

	def test_wheel_over_nested_text_scrolls_only_the_text(self) -> None:
		_, scroll_view, _, text = self._scroll_view()
		self._wheel(text, -120)
		self.assertGreater(text.yview()[0], 0)
		self.assertEqual(self._canvas(scroll_view).yview()[0], 0)

	def test_new_gesture_at_nested_edge_scrolls_the_container(self) -> None:
		_, scroll_view, _, text = self._scroll_view()
		self._canvas(scroll_view).yview_moveto(0.3)
		self.pump(text)
		start = self._canvas(scroll_view).yview()[0]
		# The text is already at its top, so scrolling up moves the container instead
		self._wheel(text, 120)
		self.assertLess(self._canvas(scroll_view).yview()[0], start)
		self.assertEqual(text.yview()[0], 0)

	def test_gesture_reaching_nested_edge_does_not_spill_into_the_container(self) -> None:
		_, scroll_view, _, text = self._scroll_view()
		self._canvas(scroll_view).yview_moveto(0.3)
		text.yview_moveto(0.02)
		self.pump(text)
		start = self._canvas(scroll_view).yview()[0]
		self._wheel(text, 120)
		self.assertEqual(text.yview()[0], 0)
		# Same gesture: stays on the text even though it can't scroll further up
		self._wheel(text, 120)
		self.assertEqual(self._canvas(scroll_view).yview()[0], start)

	def test_gesture_stays_latched_when_nested_content_moves_under_the_pointer(self) -> None:
		_, scroll_view, label, text = self._scroll_view()
		self._wheel(label, -120)
		container = self._canvas(scroll_view).yview()[0]
		# The same gesture continues over the text, which scrolled under the pointer
		self._wheel(text, -120)
		self.assertGreater(self._canvas(scroll_view).yview()[0], container)
		self.assertEqual(text.yview()[0], 0)
		# A new gesture over the text scrolls the text
		self.now += 1
		self._wheel(text, -120)
		self.assertGreater(text.yview()[0], 0)

	def _side_by_side_texts(self) -> tuple[UI.Text, UI.Text]:
		window = self.make_window(UI.MainWindow)
		texts = []
		for _ in range(2):
			text = UI.Text(window, width=20, height=5)
			text.insert('1.0', '\n'.join(str(n) for n in range(50)))
			text.pack(side=UI.LEFT)
			texts.append(text)
		self.pump(window)
		return (texts[0], texts[1])

	def _wheel_at(self, widget: UI.Misc, delta: int, over: UI.Misc) -> None:
		# A wheel event delivered to `widget` while the pointer is over the middle of `over`
		x = over.winfo_rootx() + over.winfo_width() // 2 - widget.winfo_rootx()
		y = over.winfo_rooty() + over.winfo_height() // 2 - widget.winfo_rooty()
		widget.event_generate(UI.Mouse.Scroll(), delta=delta, x=x, y=y)
		self.pump(widget)

	def test_scrolls_the_widget_under_the_pointer_rather_than_the_event_widget(self) -> None:
		# Tk can deliver scroll events to a stale widget (e.g. after a window resize on macOS)
		left, right = self._side_by_side_texts()
		self._wheel_at(left, -120, over=right)
		self.assertGreater(right.yview()[0], 0)
		self.assertEqual(left.yview()[0], 0)

	def test_moving_the_pointer_ends_the_gesture(self) -> None:
		left, right = self._side_by_side_texts()
		self._wheel_at(left, -120, over=left)
		# Within the latch time, but over another widget
		self._wheel_at(right, -120, over=right)
		self.assertGreater(right.yview()[0], 0)

	def test_gesture_stays_latched_while_the_pointer_stays_still(self) -> None:
		left, right = self._side_by_side_texts()
		self._wheel_at(left, -120, over=left)
		start = left.yview()[0]
		self._wheel_at(right, -120, over=left)
		self.assertGreater(left.yview()[0], start)
		self.assertEqual(right.yview()[0], 0)

	def test_canvas_without_scrollregion_is_not_a_target(self) -> None:
		window = self.make_window(UI.MainWindow)
		window.geometry('300x300')
		scroll_view = UI.ScrollView(window)
		scroll_view.pack(fill=UI.BOTH, expand=1)
		preview = UI.Canvas(scroll_view.content_view, width=100, height=100)
		preview.pack()
		for n in range(40):
			UI.Label(scroll_view.content_view, text=f'row {n}').pack()
		self.pump(window)
		self._wheel(preview, -120)
		self.assertGreater(self._canvas(scroll_view).yview()[0], 0)

	def test_canvas_with_scrollregion_scrolls(self) -> None:
		window = self.make_window(UI.MainWindow)
		scrolled = UI.ScrolledCanvas(window, width=100, height=100, scrollregion=(0, 0, 100, 1000))
		scrolled.pack()
		self.pump(window)
		self._wheel(scrolled.canvas, -120)
		self.assertGreater(scrolled.canvas.yview()[0], 0)

	def test_shift_wheel_scrolls_horizontally(self) -> None:
		window = self.make_window(UI.MainWindow)
		text = UI.Text(window, width=10, height=5, wrap=UI.NONE)
		text.insert('1.0', 'x' * 500)
		text.pack()
		self.pump(window)
		self._wheel(text, -120, UI.Shift.Scroll)
		self.assertGreater(text.xview()[0], 0)
		self.assertEqual(text.yview()[0], 0)

	def test_touchpad_scrolls_both_axes(self) -> None:
		window = self.make_window(UI.MainWindow)
		text = UI.Text(window, width=10, height=5, wrap=UI.NONE)
		text.insert('1.0', '\n'.join('x' * 500 for _ in range(100)))
		text.pack()
		self.pump(window)
		# Negative deltas move the content towards its end, like dragging it up/left
		self._wheel(text, _touchpad_delta(-40, -40), UI.Mouse.TouchpadScroll)
		self.assertGreater(text.xview()[0], 0)
		self.assertGreater(text.yview()[0], 0)

	def test_small_touchpad_deltas_accumulate_into_listbox_rows(self) -> None:
		window = self.make_window(UI.MainWindow)
		listbox = UI.Listbox(window, height=5)
		for n in range(50):
			listbox.insert(UI.END, str(n))
		listbox.pack()
		self.pump(window)
		# Each event is less than a row, but the gesture as a whole scrolls several
		for _ in range(20):
			self._wheel(listbox, _touchpad_delta(0, -2), UI.Mouse.TouchpadScroll)
		self.assertGreater(listbox.nearest(0), 0)

	def test_wheel_over_scrollbar_scrolls_what_it_drives(self) -> None:
		window = self.make_window(UI.MainWindow)
		scrolled = UI.ScrolledListbox(window, height=5)
		for n in range(50):
			scrolled.insert(UI.END, str(n))
		scrolled.pack()
		self.pump(window)
		scrollbar = next(child for child in scrolled.winfo_children() if isinstance(child, UI.Scrollbar) and child.cget('orient') == UI.VERTICAL)
		self._wheel(scrollbar, -120)
		self.assertGreater(scrolled.listbox.yview()[0], 0)

	def test_unfocused_combobox_passes_the_wheel_to_its_container(self) -> None:
		window, scroll_view, _, _ = self._scroll_view()
		combobox = UI.Combobox(scroll_view.content_view, state=UI.READONLY, values=['a', 'b', 'c'])
		combobox.current(0)
		combobox.pack(before=scroll_view.content_view.winfo_children()[0])
		self.pump(window)
		self._wheel(combobox, -120)
		self.assertEqual(combobox.current(), 0)
		self.assertGreater(self._canvas(scroll_view).yview()[0], 0)

	def test_focused_combobox_steps_its_value(self) -> None:
		window, scroll_view, _, _ = self._scroll_view()
		combobox = UI.Combobox(scroll_view.content_view, state=UI.READONLY, values=['a', 'b', 'c'])
		combobox.current(0)
		combobox.pack(before=scroll_view.content_view.winfo_children()[0])
		self.show(window)
		combobox.focus_force()
		self.pump(window)
		self._wheel(combobox, -120)
		self.assertEqual(combobox.current(), 1)
		self.assertEqual(self._canvas(scroll_view).yview()[0], 0)

	def _dropdown(self) -> tuple[UI.MainWindow, UI.ScrollView, UI.DropDown]:
		window, scroll_view, _, _ = self._scroll_view()
		variable = UI.IntVar()
		dropdown = UI.DropDown(scroll_view.content_view, variable, ['a', 'b', 'c'])
		dropdown.pack(before=scroll_view.content_view.winfo_children()[0])
		self.pump(window)
		return (window, scroll_view, dropdown)

	def test_unfocused_dropdown_passes_the_wheel_to_its_container(self) -> None:
		_, scroll_view, dropdown = self._dropdown()
		self._wheel(dropdown.entry, -120)
		self.assertEqual(dropdown.variable.get(), 0)
		self.assertGreater(self._canvas(scroll_view).yview()[0], 0)

	def test_focused_dropdown_steps_its_value(self) -> None:
		window, scroll_view, dropdown = self._dropdown()
		self.show(window)
		dropdown.entry.focus_force()
		self.pump(window)
		self._wheel(dropdown.entry, -120)
		self.assertEqual(dropdown.variable.get(), 1)
		self._wheel(dropdown.entry, 120)
		self.assertEqual(dropdown.variable.get(), 0)
		self.assertEqual(self._canvas(scroll_view).yview()[0], 0)

	def test_wheel_outside_open_dropdown_closes_it_without_scrolling(self) -> None:
		window, scroll_view, dropdown = self._dropdown()
		with mock.patch.object(DropDownChooser, 'wait_window'):
			chooser = DropDownChooser(dropdown, dropdown.entries, 0)
		self.pump(window)
		self.assertIs(window.mouse_wheel.popup, chooser)
		self._wheel(scroll_view.content_view.winfo_children()[-1], -120)
		self.assertIsNone(window.mouse_wheel.popup)
		self.assertFalse(chooser.winfo_exists())
		self.assertEqual(self._canvas(scroll_view).yview()[0], 0)

	def test_wheel_inside_open_dropdown_scrolls_its_list(self) -> None:
		window, _, dropdown = self._dropdown()
		entries = [str(n) for n in range(40)]
		with mock.patch.object(DropDownChooser, 'wait_window'):
			chooser = DropDownChooser(dropdown, entries, 0)
		self.pump(window)
		self._wheel(chooser.listbox, -120)
		self.assertGreater(chooser.listbox.yview()[0], 0)
		self.assertIs(window.mouse_wheel.popup, chooser)
		chooser.close()

	def test_line_number_gutter_scrolls_the_code(self) -> None:
		window = self.make_window(UI.MainWindow)
		code = UI.CodeText(window)
		code.pack(fill=UI.BOTH, expand=1)
		code.load('\n'.join(str(n) for n in range(200)))
		self.pump(window)
		self._wheel(code.lines, -120)
		self.assertGreater(code.text.yview()[0], 0)
		self.assertAlmostEqual(code.lines.yview()[0], code.text.yview()[0], delta=0.01)
