
from unittest import mock

from .harness import UITestCase

from ..Utilities import UIKit as UI


_DROPDOWN_CHOOSER = 'PyMS.Utilities.UIKit.Components.DropDown.DropDownChooser'


class _FakeChooser:
	# Stand-in for the modal DropDownChooser: records the args it was built with
	# and exposes a predetermined `result` without entering a blocking modal.
	last: '_FakeChooser | None' = None

	def __init__(self, parent, options, select) -> None:
		self.parent = parent
		self.options = options
		self.select = select
		self.result = _FakeChooser._next_result
		_FakeChooser.last = self

	_next_result = -1

	@classmethod
	def returning(cls, result: int) -> type['_FakeChooser']:
		cls._next_result = result
		cls.last = None
		return cls


class Test_DropDown(UITestCase):
	def _dropdown(self, entries, *, value=0, **kwargs) -> UI.DropDown:
		window = self.make_window(UI.MainWindow)
		variable = UI.IntVar()
		variable.set(value)
		dropdown = UI.DropDown(window, variable, entries, **kwargs)
		dropdown.pack()
		self.pump(window)
		return dropdown

	def test_initial_text_reflects_variable(self) -> None:
		dropdown = self._dropdown(['a', 'b', 'c'], value=1)
		self.assertEqual(dropdown.text.get(), 'b')

	def test_set_updates_variable_and_text(self) -> None:
		dropdown = self._dropdown(['a', 'b', 'c'])
		dropdown.set(2)
		self.assertEqual(dropdown.variable.get(), 2)
		self.assertEqual(dropdown.text.get(), 'c')

	def test_setting_the_variable_updates_the_text(self) -> None:
		# Setting the bound variable (from anywhere) must keep the displayed text
		# in sync with the selected entry.
		dropdown = self._dropdown(['a', 'b', 'c'])
		dropdown.variable.set(2)
		self.assertEqual(dropdown.text.get(), 'c')

	def test_setentries_refreshes_text_for_current_value(self) -> None:
		dropdown = self._dropdown(['a', 'b', 'c'], value=1)
		dropdown.setentries(['x', 'y', 'z'])
		self.assertEqual(dropdown.text.get(), 'y')

	def test_setentries_empty_clears_text(self) -> None:
		dropdown = self._dropdown(['a', 'b'])
		dropdown.setentries([])
		self.assertEqual(dropdown.text.get(), '')

	def test_out_of_range_value_clamps_displayed_text(self) -> None:
		dropdown = self._dropdown(['a', 'b', 'c'])
		dropdown.set(99)
		self.assertEqual(dropdown.text.get(), 'c')

	def test_none_value_shows_none_name(self) -> None:
		dropdown = self._dropdown(['a', 'b', 'c'], value=65535, none_value=65535, none_name='(none)')
		self.assertEqual(dropdown.text.get(), '(none)')

	def test_set_to_in_range_none_value_shows_none_name(self) -> None:
		dropdown = self._dropdown(['a', 'b', 'c'], none_value=1, none_name='(none)')
		dropdown.set(1)
		self.assertEqual(dropdown.text.get(), '(none)')
		self.assertEqual(dropdown.variable.get(), 1)

	def test_display_callback_is_invoked_on_set(self) -> None:
		received: list[int] = []
		window = self.make_window(UI.MainWindow)
		dropdown = UI.DropDown(window, UI.IntVar(), ['a', 'b', 'c'], received.append)
		dropdown.pack()
		self.pump(window)
		dropdown.set(2)
		self.assertEqual(received[-1], 2)

	def test_display_variable_is_synced_on_set(self) -> None:
		# When `display` is a Variable, selecting in the dropdown mirrors the value
		# into that variable (the PyTILE editor pattern).
		window = self.make_window(UI.MainWindow)
		display = UI.IntegerVar(0, [0, 2])
		dropdown = UI.DropDown(window, UI.IntVar(), ['a', 'b', 'c'], display)
		dropdown.pack()
		self.pump(window)
		dropdown.set(2)
		self.assertEqual(display.get(), 2)

	def test_display_variable_change_drives_the_dropdown(self) -> None:
		# The reverse of the above: writing the display variable updates the
		# dropdown's own selection/text.
		window = self.make_window(UI.MainWindow)
		display = UI.IntegerVar(0, [0, 2])
		dropdown = UI.DropDown(window, UI.IntVar(), ['a', 'b', 'c'], display)
		dropdown.pack()
		self.pump(window)
		display.set(1)
		self.assertEqual(dropdown.text.get(), 'b')
		self.assertEqual(dropdown.variable.get(), 1)

	def test_choose_selects_entry_and_sets_value(self) -> None:
		dropdown = self._dropdown(['a', 'b', 'c'])
		with mock.patch(_DROPDOWN_CHOOSER, _FakeChooser.returning(2)):
			dropdown.choose()
		self.assertEqual(dropdown.variable.get(), 2)
		self.assertEqual(dropdown.text.get(), 'c')

	def test_choose_passes_current_index_as_initial_selection(self) -> None:
		dropdown = self._dropdown(['a', 'b', 'c'], value=1)
		with mock.patch(_DROPDOWN_CHOOSER, _FakeChooser.returning(1)):
			dropdown.choose()
		assert _FakeChooser.last is not None
		self.assertEqual(_FakeChooser.last.select, 1)

	def test_choose_does_not_raise_when_none_name_absent_from_entries(self) -> None:
		# With a `none_value` selected but no matching `none_name` entry, opening
		# the chooser must not raise — it should fall back to the current value.
		dropdown = self._dropdown(['a', 'b', 'c'], none_value=65535, none_name='(none)')
		dropdown.variable.set(65535)
		with mock.patch(_DROPDOWN_CHOOSER, _FakeChooser.returning(1)):
			dropdown.choose()
		self.assertEqual(dropdown.variable.get(), 1)

	def test_choosing_none_name_entry_sets_none_value_even_when_zero(self) -> None:
		# Selecting the entry whose text is `none_name` stores `none_value`, even
		# when `none_value` is the falsy `0`.
		dropdown = self._dropdown(['a', '(none)', 'b'], value=2, none_value=0, none_name='(none)')
		with mock.patch(_DROPDOWN_CHOOSER, _FakeChooser.returning(1)):
			dropdown.choose()
		self.assertEqual(dropdown.variable.get(), 0)


class Test_EntryDropDown(UITestCase):
	def _entry_dropdown(self, entries, *, value=0) -> UI.EntryDropDown:
		window = self.make_window(UI.MainWindow)
		variable = UI.IntegerVar(value)
		entry_dropdown = UI.EntryDropDown(window, variable, entries)
		entry_dropdown.pack()
		self.pump(window)
		return entry_dropdown

	def test_initial_value_selects_matching_dropdown_index(self) -> None:
		entry_dropdown = self._entry_dropdown(['a', 'b', 'c'], value=1)
		self.assertEqual(entry_dropdown.dropdown_variable.get(), 1)
		self.assertEqual(entry_dropdown.dropdown.text.get(), 'b')

	def test_plain_entries_use_index_as_value(self) -> None:
		entry_dropdown = self._entry_dropdown(['a', 'b', 'c'])
		self.assertEqual(entry_dropdown.value_to_index_map, {0: 0, 1: 1, 2: 2})

	def test_tuple_entries_use_custom_values(self) -> None:
		entry_dropdown = self._entry_dropdown([('x', 10), ('y', 20)], value=20)
		self.assertEqual(entry_dropdown.value_to_index_map, {10: 0, 20: 1})
		self.assertEqual(entry_dropdown.dropdown_variable.get(), 1)
		self.assertEqual(entry_dropdown.dropdown.text.get(), 'y')

	def test_choosing_in_dropdown_updates_entry_value(self) -> None:
		entry_dropdown = self._entry_dropdown([('x', 10), ('y', 20)])
		entry_dropdown.dropdown.set(1)
		self.assertEqual(entry_dropdown.variable.get(), 20)

	def test_setting_entry_value_selects_dropdown_index(self) -> None:
		entry_dropdown = self._entry_dropdown([('x', 10), ('y', 20)])
		entry_dropdown.variable.set(20)
		self.assertEqual(entry_dropdown.dropdown_variable.get(), 1)

	def test_unknown_value_selects_the_none_entry(self) -> None:
		# An entry with value `None` is the catch-all for any unmapped value.
		entry_dropdown = self._entry_dropdown([('known', 5), ('any', None)], value=999)
		self.assertEqual(entry_dropdown.dropdown_variable.get(), 1)
		self.assertEqual(entry_dropdown.dropdown.text.get(), 'any')
