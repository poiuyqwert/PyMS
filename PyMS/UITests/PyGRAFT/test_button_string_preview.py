from .utils import PyGRAFTTestCase

from ...PyGRAFT.PyGRAFT import PyGRAFT
from ...PyGRAFT.Tabs import ButtonSetsTab
from ...PyGRAFT.ButtonSetEditor.ButtonSetBuilderView import ButtonSetBuilderView
from ...FileFormats.Graft import Button
from ...FileFormats.Graft.CodeHandlers import ButtonCodeCommands
from ...FileFormats.FNT import FNT
from ...FileFormats.PCX import PCX
from ...FileFormats.TBL import TBL
from ...Utilities import Assets
from ...Utilities import UIKit as UI
from ...Utilities.DataContext import CmdIconState

from unittest import mock

class Test_PyGRAFT_button_string_preview(PyGRAFTTestCase):
	def open_builder(self, *, fonts: bool = True) -> tuple[PyGRAFT, ButtonSetBuilderView]:
		gui = self.open_pygraft()
		stat_txt = TBL()
		stat_txt.strings = ['Terran Marine\x00', 'm\x01Train \x03M\x01arine\x00', 'm\x00\x03M\x01ove\x00', 'Stim Packs:\n   Research at Academy\x00']
		gui.data_context.set_stat_txt_tbl(stat_txt)
		if fonts:
			font8 = FNT()
			font8.load(Assets.mpq_file_path('font', 'font8.fnt'))
			tfontgam = PCX()
			tfontgam.load(Assets.mpq_file_path('game', 'tfontgam.pcx'))
			gui.data_context.set_font8_fnt(font8)
			gui.data_context.set_tfontgam_pcx(tfontgam)
		tab = self.display_tab(gui, 'Button Sets')
		assert isinstance(tab, ButtonSetsTab)
		view = tab.editor.builder_view
		assert view.entry_id is not None
		gui.buttons_data.graft.button_sets[view.entry_id].buttons = [
			Button(position=1, action=ButtonCodeCommands.Train.function_index, enabled_string=2, disabled_string=0),
			Button(position=2, action=ButtonCodeCommands.Move.function_index, enabled_string=1, disabled_string=4),
		]
		view.load(view.entry_id, view.entry_name)
		self.pump(gui)
		return gui, view

	def test_inline_previews_show_the_hotkey_strings(self) -> None:
		_, view = self.open_builder()
		settings = view.settings_view
		enabled = settings.enabled_string_preview
		self.assertIsNotNone(enabled.drawing)
		assert enabled.drawing is not None
		self.assertTrue(enabled.canvas.find_all())
		# A unit's tooltip has its cost line under its text
		self.assertGreater(enabled.drawing.height, gui_font_height(view))
		# No string, no preview
		self.assertIsNone(settings.disabled_string_preview.drawing)
		self.assertFalse(settings.disabled_string_preview.canvas.winfo_ismapped())
		self.assertTrue(enabled.canvas.winfo_ismapped())

	def test_inline_preview_follows_the_string(self) -> None:
		gui, view = self.open_builder()
		settings = view.settings_view
		settings.enabled_string.set(0)
		settings.enabled_string_changed(0)
		self.pump(gui)
		self.assertIsNone(settings.enabled_string_preview.drawing)
		self.assertFalse(settings.enabled_string_preview.canvas.find_all())
		settings.enabled_string.set(3)
		settings.enabled_string_changed(3)
		self.pump(gui)
		self.assertIsNotNone(settings.enabled_string_preview.drawing)

	def test_enabled_strings_that_arent_hotkey_strings_have_no_preview(self) -> None:
		gui, view = self.open_builder()
		view.select_button(1)
		self.pump(gui)
		self.assertIsNone(view.settings_view.enabled_string_preview.drawing)

	def test_disabled_string_preview_shows_its_plain_text(self) -> None:
		# Disabled strings are plain text (like requirements), without a hotkey or cost line
		gui, view = self.open_builder()
		view.select_button(1)
		self.pump(gui)
		disabled = view.settings_view.disabled_string_preview
		assert disabled.drawing is not None
		self.assertTrue(disabled.canvas.find_all())
		self.assertTrue(disabled.canvas.winfo_ismapped())
		self.assertEqual(disabled.drawing.height, gui_font_height(view) * 2)

	def test_disabled_string_preview_follows_the_string(self) -> None:
		gui, view = self.open_builder()
		settings = view.settings_view
		self.assertIsNone(settings.disabled_string_preview.drawing)
		settings.disabled_string.set(4)
		settings.disabled_string_changed(4)
		self.pump(gui)
		self.assertIsNotNone(settings.disabled_string_preview.drawing)
		self.assertTrue(settings.disabled_string_preview.canvas.winfo_ismapped())
		settings.disabled_string.set(0)
		settings.disabled_string_changed(0)
		self.pump(gui)
		self.assertIsNone(settings.disabled_string_preview.drawing)
		self.assertFalse(settings.disabled_string_preview.canvas.find_all())

	def test_tooltips_of_missing_strings_are_empty(self) -> None:
		_, view = self.open_builder()
		# String IDs are 1-based, so 5 is past the 4 strings
		self.assertIsNone(view.button_tooltip(Button(enabled_string=5)))
		self.assertIsNone(view.button_tooltip(Button(disabled_string=5), enabled=False))

	def test_disabled_tooltip_draws_a_hotkey_string_as_it_is(self) -> None:
		_, view = self.open_builder()
		drawing = view.button_tooltip(Button(disabled_string=2), enabled=False)
		assert drawing is not None
		self.assertEqual(drawing.height, gui_font_height(view))

	def test_no_previews_without_the_fonts(self) -> None:
		_, view = self.open_builder(fonts=False)
		self.assertIsNone(view.settings_view.enabled_string_preview.drawing)

	def test_hovering_a_slot_shows_its_tooltip(self) -> None:
		gui, view = self.open_builder()
		tooltip = view.preview.tooltips[1]
		tooltip.showtip()
		self.pump(gui)
		self.assertIsNotNone(tooltip.tip)
		assert tooltip.canvas is not None
		self.assertTrue(tooltip.canvas.find_all())
		tooltip.hidetip()
		self.assertIsNone(tooltip.tip)
		# Slot 2's button has no hotkey string, and slot 3 has no button
		for position in (2, 3):
			view.preview.tooltips[position].showtip()
			self.assertIsNone(view.preview.tooltips[position].tip)

	def press_control(self, gui: PyGRAFT, pattern: UI.EventPattern) -> None:
		gui.event_generate(pattern.event(), keysym='Control_L')
		self.pump(gui)

	def test_holding_control_shows_the_disabled_tooltips(self) -> None:
		gui, view = self.open_builder()
		self.show(gui)
		self.press_control(gui, UI.Key.Pressed)
		self.assertTrue(view.preview.show_disabled)
		# Slot 2's button has a disabled string, slot 1's doesn't
		tooltip = view.preview.tooltips[2]
		tooltip.showtip()
		self.assertIsNotNone(tooltip.tip)
		assert tooltip.drawing is not None
		disabled = view.button_tooltip(view.buttons()[1], enabled=False)
		assert disabled is not None
		self.assertEqual((tooltip.drawing.width, tooltip.drawing.height), (disabled.width, disabled.height))
		view.preview.tooltips[1].showtip()
		self.assertIsNone(view.preview.tooltips[1].tip)
		tooltip.hidetip()
		self.press_control(gui, UI.Key.Released)
		self.assertFalse(view.preview.show_disabled)
		view.preview.tooltips[1].showtip()
		self.assertIsNotNone(view.preview.tooltips[1].tip)
		view.preview.tooltips[1].hidetip()

	def test_control_switches_the_hovered_slots_tooltip(self) -> None:
		gui, view = self.open_builder()
		self.show(gui)
		slot = view.preview.slots[1]
		slot.event_generate(UI.Cursor.Enter.event(), state=0)
		self.pump(gui)
		tooltip = view.preview.tooltips[1]
		tooltip.showtip()
		self.assertIsNotNone(tooltip.tip)
		# Slot 1's button has no disabled string, so its tooltip goes away while Control is held, and comes back when it's released
		self.press_control(gui, UI.Key.Pressed)
		self.assertIsNone(tooltip.tip)
		self.press_control(gui, UI.Key.Released)
		self.assertIsNotNone(tooltip.tip)
		# Other slots' tooltips aren't shown
		self.assertIsNone(view.preview.tooltips[2].tip)
		slot.event_generate(UI.Cursor.Leave.event())
		self.pump(gui)
		self.assertIsNone(tooltip.tip)
		self.assertIsNone(view.preview.hovered)

	def test_control_redraws_the_hovered_slots_tooltip_in_its_window(self) -> None:
		gui, view = self.open_builder()
		self.show(gui)
		# Slot 2's button gets both strings
		view.buttons()[1].enabled_string = 2
		view.sync()
		view.preview.slots[2].event_generate(UI.Cursor.Enter.event(), state=0)
		self.pump(gui)
		tooltip = view.preview.tooltips[2]
		tooltip.showtip()
		tip = tooltip.tip
		self.assertIsNotNone(tip)
		for pattern, enabled in ((UI.Key.Pressed, False), (UI.Key.Released, True)):
			self.press_control(gui, pattern)
			# Redrawn in the same window, which closing and opening a window under the mouse would hide
			self.assertIs(tooltip.tip, tip)
			expected = view.button_tooltip(view.buttons()[1], enabled=enabled)
			assert tooltip.drawing is not None and expected is not None
			self.assertEqual((tooltip.drawing.width, tooltip.drawing.height), (expected.width, expected.height))
		tooltip.hidetip()

	def test_holding_control_shows_the_disabled_icons(self) -> None:
		gui, view = self.open_builder()
		with mock.patch.object(view, 'button_icon', wraps=view.button_icon) as button_icon:
			view.preview.set_show_disabled(True)
			self.assertEqual(set(call.args[1] for call in button_icon.call_args_list), {CmdIconState.disabled})
			self.assertEqual(button_icon.call_count, 2)
			button_icon.reset_mock()
			view.preview.set_show_disabled(False)
			self.assertEqual(set(call.args[1] for call in button_icon.call_args_list), {CmdIconState.enabled})
			# Changing the buttons keeps drawing the current state
			view.preview.set_show_disabled(True)
			button_icon.reset_mock()
			view.sync()
			self.assertEqual(set(call.args[1] for call in button_icon.call_args_list if len(call.args) > 1), {CmdIconState.disabled})
		self.pump(gui)

	def test_control_shows_disabled_while_a_settings_dropdown_has_the_focus(self) -> None:
		gui, view = self.open_builder()
		self.show(gui)
		entry = view.settings_view.position_dropdown.entry
		entry.focus_force()
		self.pump(gui)
		entry.event_generate(UI.Key.Pressed.event(), keysym='Control_L')
		self.pump(gui)
		self.assertTrue(view.preview.show_disabled)
		entry.event_generate(UI.Key.Released.event(), keysym='Control_L')
		self.pump(gui)
		self.assertFalse(view.preview.show_disabled)

	def test_losing_the_focus_stops_showing_disabled(self) -> None:
		gui, view = self.open_builder()
		self.show(gui)
		self.press_control(gui, UI.Key.Pressed)
		self.assertTrue(view.preview.show_disabled)
		gui.event_generate(UI.Focus.Out.event())
		self.pump(gui)
		self.assertFalse(view.preview.show_disabled)

	def test_other_keys_dont_show_disabled(self) -> None:
		gui, view = self.open_builder()
		self.show(gui)
		gui.event_generate(UI.Key.Pressed.event(), keysym='Shift_L')
		self.pump(gui)
		self.assertFalse(view.preview.show_disabled)

	def test_mouse_events_dont_change_showing_disabled(self) -> None:
		# Only the Control key events show disabled: Tk sends a Leave and Enter without the modifiers when a tooltip window opens or closes under the mouse
		gui, view = self.open_builder()
		self.show(gui)
		slot = view.preview.slots[2]
		slot.event_generate(UI.Cursor.Enter.event(), state=0)
		self.press_control(gui, UI.Key.Pressed)
		self.assertTrue(view.preview.show_disabled)
		slot.event_generate(UI.Cursor.Leave.event(), state=0)
		slot.event_generate(UI.Cursor.Enter.event(), state=0)
		self.pump(gui)
		self.assertTrue(view.preview.show_disabled)
		self.press_control(gui, UI.Key.Released)
		self.assertFalse(view.preview.show_disabled)
		# Control held from another window isn't used
		slot.event_generate(UI.Cursor.Enter.event(), state=UI.Modifier.Mac.Ctrl.state)
		self.pump(gui)
		self.assertFalse(view.preview.show_disabled)

def gui_font_height(view: ButtonSetBuilderView) -> int:
	font = view.data_context.font8_fnt
	assert font is not None
	return font.height
