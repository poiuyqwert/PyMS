
from ...Utilities.UIKit.EventPattern import EventPattern, CustomEventPattern, Field, ModifiedField, Keysym, Modifier, Events, Key, Mouse, WidgetEvent, Cursor, Focus, EventPropogation, Shift, Ctrl, Alt, Double, Triple, Quadruple

import importlib.util
import unittest
from unittest import mock

from typing import Any

IS_MAC = 'PyMS.Utilities.UIKit.EventPattern.is_mac'


def _load_event_pattern(is_mac_value: bool) -> Any:
	# Re-execute the module as a throwaway copy with `is_mac` forced, so the
	# import-time platform constants can be checked for both platforms without
	# disturbing the canonical (already-imported) module.
	spec = importlib.util.find_spec('PyMS.Utilities.UIKit.EventPattern')
	assert spec is not None and spec.loader is not None
	module = importlib.util.module_from_spec(spec)
	with mock.patch('PyMS.Utilities.utils.is_mac', return_value=is_mac_value):
		spec.loader.exec_module(module)
	return module


class Test_EventPattern_name(unittest.TestCase):
	def test_joins_field_values_with_dash(self) -> None:
		self.assertEqual(EventPattern(Field('Control'), Field('a')).name(), 'Control-a')

	def test_single_field(self) -> None:
		self.assertEqual(EventPattern(Field('Configure')).name(), 'Configure')

	def test_empty(self) -> None:
		self.assertEqual(EventPattern().name(), '')


class Test_EventPattern_event(unittest.TestCase):
	def test_wraps_name_in_angle_brackets(self) -> None:
		self.assertEqual(EventPattern(Field('Control'), Field('a')).event(), '<Control-a>')

	def test_custom_event_uses_double_brackets(self) -> None:
		self.assertEqual(CustomEventPattern(Field('Foo')).event(), '<<Foo>>')

	def test_str_matches_event(self) -> None:
		pattern = EventPattern(Field('a'))
		self.assertEqual(str(pattern), pattern.event())

	def test_call_matches_event(self) -> None:
		pattern = EventPattern(Field('a'))
		self.assertEqual(pattern(), pattern.event())

	def test_repr_includes_class_and_event(self) -> None:
		self.assertEqual(repr(EventPattern(Field('a'))), '<EventPattern <a>>')


class Test_EventPattern_description(unittest.TestCase):
	def test_mac_joins_without_separator(self) -> None:
		pattern = EventPattern(Field('Ctrl', 'Ctrl'), Field('a', 'A'))
		with mock.patch(IS_MAC, return_value=True):
			self.assertEqual(pattern.description(), 'CtrlA')

	def test_non_mac_joins_with_plus(self) -> None:
		pattern = EventPattern(Field('Ctrl', 'Ctrl'), Field('a', 'A'))
		with mock.patch(IS_MAC, return_value=False):
			self.assertEqual(pattern.description(), 'Ctrl+A')

	def test_uses_field_description_not_value(self) -> None:
		pattern = EventPattern(Field('B1', 'Left-Click'))
		with mock.patch(IS_MAC, return_value=False):
			self.assertEqual(pattern.description(), 'Left-Click')


class Test_EventPattern_get_keysym(unittest.TestCase):
	def test_returns_trailing_keysym(self) -> None:
		keysym = Keysym('a')
		self.assertIs(EventPattern(Field('Control'), keysym).get_keysym(), keysym)

	def test_none_when_last_field_not_keysym(self) -> None:
		self.assertIsNone(EventPattern(Keysym('a'), Field('Control')).get_keysym())

	def test_none_when_empty(self) -> None:
		self.assertIsNone(EventPattern().get_keysym())


class Test_EventPattern_add(unittest.TestCase):
	def test_add_event_pattern_concatenates_fields(self) -> None:
		combined = EventPattern(Field('Control')) + EventPattern(Field('a'))
		self.assertEqual(combined.name(), 'Control-a')

	def test_add_field_appends(self) -> None:
		combined = EventPattern(Field('Control')) + Field('a')
		self.assertEqual(combined.name(), 'Control-a')

	def test_add_invalid_raises_type_error(self) -> None:
		not_addable: Any = 5
		with self.assertRaises(TypeError):
			_ = EventPattern(Field('a')) + not_addable


class Test_Field(unittest.TestCase):
	def test_description_defaults_to_value(self) -> None:
		field = Field('Configure')
		self.assertEqual(field.value, 'Configure')
		self.assertEqual(field.description, 'Configure')

	def test_explicit_description(self) -> None:
		self.assertEqual(Field('B1', 'Left-Click').description, 'Left-Click')

	def test_equal_by_value(self) -> None:
		self.assertEqual(Field('a'), Field('a'))

	def test_equal_ignores_description(self) -> None:
		self.assertEqual(Field('a', 'first'), Field('a', 'second'))

	def test_not_equal_different_value(self) -> None:
		self.assertNotEqual(Field('a'), Field('b'))

	def test_not_equal_to_non_field(self) -> None:
		self.assertNotEqual(Field('a'), 'a')

	def test_add_field_builds_pattern(self) -> None:
		self.assertEqual((Field('Control') + Field('a')).name(), 'Control-a')

	def test_add_event_pattern_prepends(self) -> None:
		self.assertEqual((Field('Control') + EventPattern(Field('a'))).name(), 'Control-a')

	def test_add_invalid_raises_type_error(self) -> None:
		not_addable: Any = 5
		with self.assertRaises(TypeError):
			_ = Field('a') + not_addable


class Test_ModifiedField(unittest.TestCase):
	def test_stores_state(self) -> None:
		self.assertEqual(ModifiedField('Shift', state=0x01).state, 0x01)

	def test_default_state_is_zero(self) -> None:
		self.assertEqual(ModifiedField('Shift').state, 0)

	def test_is_a_field(self) -> None:
		field = ModifiedField('Control', '⌘', state=0x08)
		self.assertIsInstance(field, Field)
		self.assertEqual(field.value, 'Control')
		self.assertEqual(field.description, '⌘')


class Test_Keysym(unittest.TestCase):
	def test_description_defaults_to_capitalized_key(self) -> None:
		self.assertEqual(Keysym('a').description, 'A')

	def test_explicit_description(self) -> None:
		self.assertEqual(Keysym('slash', '/').description, '/')

	def test_capitalized_returns_capitalized_variant(self) -> None:
		capitalized = Keysym('a', capitalized_key='A').capitalized()
		self.assertEqual(capitalized.value, 'A')

	def test_capitalized_uses_capitalized_description(self) -> None:
		capitalized = Keysym('a', capitalized_key='A', capitalized_key_description='Shift-A').capitalized()
		self.assertEqual(capitalized.description, 'Shift-A')

	def test_capitalized_returns_self_without_capitalized_key(self) -> None:
		keysym = Keysym('Return')
		self.assertIs(keysym.capitalized(), keysym)

	def test_repr(self) -> None:
		self.assertEqual(repr(Keysym('a')), "<Keysym 'a'>")


class Test_exported_patterns(unittest.TestCase):
	def test_key_letter_event(self) -> None:
		self.assertEqual(Key.a.event(), '<a>')

	def test_key_function_key_event(self) -> None:
		self.assertEqual(Key.F1.event(), '<F1>')

	def test_key_carries_keysym(self) -> None:
		keysym = Key.a.get_keysym()
		assert keysym is not None
		self.assertEqual(keysym.value, 'a')

	def test_mouse_left_click_event(self) -> None:
		self.assertEqual(Mouse.Click_Left.event(), '<Button-1>')

	def test_widget_event_plain(self) -> None:
		self.assertEqual(WidgetEvent.Configure.event(), '<Configure>')

	def test_widget_event_custom_uses_double_brackets(self) -> None:
		self.assertEqual(WidgetEvent.Listbox.Select.event(), '<<ListboxSelect>>')


# The `Ctrl`/`Alt` modifier values differ by platform ('Command'/'Option' on mac,
# 'Control'/'Alt' elsewhere), so the platform-dependent segments are derived from
# `Modifier.*.value` to keep these assertions correct on any OS. `Shift`,
# `Double`/`Triple`/`Quadruple`, and `Button-1` are stable and asserted literally.
class Test_modifier_combinations(unittest.TestCase):
	def test_shift_capitalizes_keysym(self) -> None:
		self.assertEqual(Shift.a.name(), 'Shift-A')
		self.assertEqual(Shift.a.event(), '<Shift-A>')

	def test_modifier_without_shift_keeps_keysym_lowercase(self) -> None:
		self.assertEqual(Ctrl.a.name(), f'{Modifier.Ctrl.value}-a')
		self.assertEqual(Alt.a.name(), f'{Modifier.Alt.value}-a')

	def test_shift_prefixes_mouse_event(self) -> None:
		self.assertEqual(Shift.Click_Left.name(), 'Shift-Button-1')

	def test_click_multiplier_modifiers(self) -> None:
		self.assertEqual(Double.Click_Left.name(), 'Double-Button-1')
		self.assertEqual(Triple.Click_Left.name(), 'Triple-Button-1')
		self.assertEqual(Quadruple.Click_Left.name(), 'Quadruple-Button-1')

	def test_two_modifiers_in_order(self) -> None:
		self.assertEqual(Ctrl.Alt.a.name(), f'{Modifier.Ctrl.value}-{Modifier.Alt.value}-a')

	def test_shift_and_multiplier(self) -> None:
		self.assertEqual(Shift.Double.Click_Left.name(), 'Shift-Double-Button-1')

	def test_deep_combination_keeps_modifier_order_and_capitalizes(self) -> None:
		self.assertEqual(Shift.Ctrl.Alt.a.name(), f'Shift-{Modifier.Ctrl.value}-{Modifier.Alt.value}-A')

	def test_deepest_combination_with_mouse_event(self) -> None:
		expected = f'Shift-{Modifier.Ctrl.value}-{Modifier.Alt.value}-Quadruple-Button-1'
		self.assertEqual(Shift.Ctrl.Alt.Quadruple.Click_Left.name(), expected)
		self.assertEqual(Shift.Ctrl.Alt.Quadruple.Click_Left.event(), f'<{expected}>')


class Test_Events_modify(unittest.TestCase):
	def test_modify_prepends_modifiers_in_order(self) -> None:
		class Sample(Events):
			click = EventPattern(Field('Button-1'))
		Sample.modify(Field('Ctrl'), Modifier.Double)
		self.assertEqual(Sample.click.name(), 'Ctrl-Double-Button-1')

	def test_modify_capitalizes_keysym_when_shift_present(self) -> None:
		class Sample(Events):
			key = EventPattern(Keysym('a', capitalized_key='A'))
		Sample.modify(Modifier.Shift)
		self.assertEqual(Sample.key.name(), 'Shift-A')

	def test_modify_keeps_keysym_when_shift_absent(self) -> None:
		class Sample(Events):
			key = EventPattern(Keysym('a', capitalized_key='A'))
		Sample.modify(Field('Ctrl'))
		self.assertEqual(Sample.key.name(), 'Ctrl-a')

	def test_modify_leaves_non_keysym_fields_unchanged(self) -> None:
		class Sample(Events):
			click = EventPattern(Field('Button-1'))
		Sample.modify(Modifier.Shift)
		self.assertEqual(Sample.click.name(), 'Shift-Button-1')


class Test_platform_specifics(unittest.TestCase):
	mac: Any
	non_mac: Any

	@classmethod
	def setUpClass(cls) -> None:
		cls.mac = _load_event_pattern(True)
		cls.non_mac = _load_event_pattern(False)

	def test_shift_modifier(self) -> None:
		mac_shift = self.mac.Modifier.Shift
		self.assertEqual((mac_shift.value, mac_shift.description, mac_shift.state), ('Shift', '⇧', 0x01))
		non_mac_shift = self.non_mac.Modifier.Shift
		self.assertEqual((non_mac_shift.value, non_mac_shift.description, non_mac_shift.state), ('Shift', 'Shift', 0x01))

	def test_ctrl_modifier_is_command_on_mac(self) -> None:
		ctrl = self.mac.Modifier.Ctrl
		self.assertEqual((ctrl.value, ctrl.description, ctrl.state), ('Command', '⌘', 0x08))

	def test_ctrl_modifier_is_control_off_mac(self) -> None:
		ctrl = self.non_mac.Modifier.Ctrl
		self.assertEqual((ctrl.value, ctrl.description, ctrl.state), ('Control', 'Ctrl', 0x04))

	def test_alt_modifier_is_option_on_mac(self) -> None:
		alt = self.mac.Modifier.Alt
		self.assertEqual((alt.value, alt.description, alt.state), ('Option', '⌥', 0x10))

	def test_alt_modifier_is_alt_off_mac(self) -> None:
		alt = self.non_mac.Modifier.Alt
		self.assertEqual((alt.value, alt.description, alt.state), ('Alt', 'Alt', 0x10))

	def test_mac_ctrl_modifier_is_always_control(self) -> None:
		# `Modifier.Mac.Ctrl` is the real Control key (state 0x04) on either platform,
		# only its symbol differs.
		mac_ctrl = self.mac.Modifier.Mac.Ctrl
		self.assertEqual((mac_ctrl.value, mac_ctrl.description, mac_ctrl.state), ('Control', '⌃', 0x04))
		non_mac_ctrl = self.non_mac.Modifier.Mac.Ctrl
		self.assertEqual((non_mac_ctrl.value, non_mac_ctrl.description, non_mac_ctrl.state), ('Control', 'Ctrl', 0x04))

	def test_right_click_button_number(self) -> None:
		self.assertEqual(self.mac.Modifier.Click_Right.value, 'B2')
		self.assertEqual(self.non_mac.Modifier.Click_Right.value, 'B3')

	def test_mouse_right_click_event(self) -> None:
		self.assertEqual(self.mac.Mouse.Click_Right.name(), 'Button-2')
		self.assertEqual(self.non_mac.Mouse.Click_Right.name(), 'Button-3')

	def test_button_release_right_click_event(self) -> None:
		self.assertEqual(self.mac.ButtonRelease.Click_Right.name(), 'ButtonRelease-2')
		self.assertEqual(self.non_mac.ButtonRelease.Click_Right.name(), 'ButtonRelease-3')

	def test_shortcut_exit(self) -> None:
		self.assertEqual(self.mac.Shortcut.Exit.event(), '<Command-q>')
		self.assertEqual(self.non_mac.Shortcut.Exit.event(), '<Alt-F4>')

	def test_shortcut_close(self) -> None:
		self.assertEqual(self.mac.Shortcut.Close.event(), '<Command-w>')
		self.assertEqual(self.non_mac.Shortcut.Close.event(), '<Escape>')


class Test_event_groups(unittest.TestCase):
	def test_mouse_middle_click(self) -> None:
		self.assertEqual(Mouse.Click_Middle.event(), '<Button-2>')

	def test_mouse_motion(self) -> None:
		self.assertEqual(Mouse.Motion.event(), '<Motion>')

	def test_mouse_scroll(self) -> None:
		self.assertEqual(Mouse.Scroll.event(), '<MouseWheel>')

	def test_mouse_drag_left(self) -> None:
		self.assertEqual(Mouse.Drag_Left.name(), 'B1-Motion')

	def test_cursor_events(self) -> None:
		self.assertEqual(Cursor.Enter.event(), '<Enter>')
		self.assertEqual(Cursor.Leave.event(), '<Leave>')

	def test_focus_events(self) -> None:
		self.assertEqual(Focus.In.event(), '<FocusIn>')
		self.assertEqual(Focus.Out.event(), '<FocusOut>')

	def test_widget_event_destroy(self) -> None:
		self.assertEqual(WidgetEvent.Destroy.event(), '<Destroy>')

	def test_widget_event_custom_groups(self) -> None:
		self.assertEqual(WidgetEvent.Text.Modified.event(), '<<Modified>>')
		self.assertEqual(WidgetEvent.Treeview.Select.event(), '<<TreeviewSelect>>')
		self.assertEqual(WidgetEvent.Combobox.Selected.event(), '<<ComboboxSelected>>')


class Test_EventPropogation(unittest.TestCase):
	def test_break(self) -> None:
		self.assertEqual(EventPropogation.Break, 'break')

	def test_continue(self) -> None:
		self.assertEqual(EventPropogation.Continue, 'continue')
