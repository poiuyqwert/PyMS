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

def gui_font_height(view: ButtonSetBuilderView) -> int:
	font = view.data_context.font8_fnt
	assert font is not None
	return font.height
