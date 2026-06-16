
from ...FileFormats.DialogBIN import DialogBIN, BINWidget, flags
from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO
from ..utils import resource_path

import io
import unittest

SAMPLE_BIN = 'gamemenu.bin'


def _load_sample() -> DialogBIN:
	dialog = DialogBIN()
	dialog.load(resource_path(SAMPLE_BIN, __file__))
	return dialog


def _decompile(dialog: DialogBIN) -> str:
	output = io.StringIO()
	dialog.decompile_file(output)
	return output.getvalue()


class Test_flags(unittest.TestCase):
	def test_int_to_binary_string(self) -> None:
		self.assertEqual(flags(5, 4), '0101')

	def test_int_to_binary_string_width(self) -> None:
		self.assertEqual(flags(1, 8), '00000001')

	def test_binary_string_to_int(self) -> None:
		self.assertEqual(flags('0101', 4), 5)

	def test_round_trip(self) -> None:
		self.assertEqual(flags(flags(0b101101, 8), 8), 0b101101)

	def test_invalid_length_raises(self) -> None:
		with self.assertRaises(PyMSError):
			flags('010', 4)

	def test_invalid_characters_raise(self) -> None:
		with self.assertRaises(PyMSError):
			flags('012x', 4)


class Test_BINWidget(unittest.TestCase):
	def test_bounding_box_normalizes(self) -> None:
		widget = BINWidget(BINWidget.TYPE_IMAGE)
		widget.x1, widget.y1, widget.x2, widget.y2 = 100, 50, 10, 5
		self.assertEqual(widget.bounding_box(), (10, 5, 100, 50))

	def test_is_button(self) -> None:
		self.assertTrue(BINWidget(BINWidget.TYPE_BUTTON).is_button())
		self.assertTrue(BINWidget(BINWidget.TYPE_DEFAULT_BTN).is_button())
		self.assertFalse(BINWidget(BINWidget.TYPE_LABEL_LEFT_ALIGN).is_button())

	def test_has_responsive(self) -> None:
		self.assertTrue(BINWidget(BINWidget.TYPE_BUTTON).has_responsive())
		self.assertFalse(BINWidget(BINWidget.TYPE_IMAGE).has_responsive())

	def test_responsive_box_offsets_bounding_box(self) -> None:
		widget = BINWidget(BINWidget.TYPE_BUTTON)
		widget.x1, widget.y1, widget.x2, widget.y2 = 10, 20, 110, 50
		widget.responsive_x1, widget.responsive_y1, widget.responsive_x2, widget.responsive_y2 = 1, 2, 90, 28
		self.assertEqual(widget.responsive_box(), (11, 22, 100, 48))

	def test_display_text_strips_button_hotkey(self) -> None:
		widget = BINWidget(BINWidget.TYPE_BUTTON)
		widget.string = '\x1bReturn'
		widget.flags |= BINWidget.FLAG_HAS_HOTKEY
		self.assertEqual(widget.display_text(), 'Return')

	def test_display_text_label_unchanged(self) -> None:
		widget = BINWidget(BINWidget.TYPE_LABEL_LEFT_ALIGN)
		widget.string = 'Hello'
		self.assertEqual(widget.display_text(), 'Hello')

	def test_display_text_none_for_dialog_and_image(self) -> None:
		self.assertIsNone(BINWidget(BINWidget.TYPE_DIALOG).display_text())
		self.assertIsNone(BINWidget(BINWidget.TYPE_IMAGE).display_text())


class Test_remastered_required(unittest.TestCase):
	def test_false_for_legacy_widgets(self) -> None:
		self.assertFalse(DialogBIN().remastered_required())

	def test_true_when_html_widget_present(self) -> None:
		dialog = DialogBIN()
		dialog.widgets.append(BINWidget(BINWidget.TYPE_HTML))
		self.assertTrue(dialog.remastered_required())


class Test_load(unittest.TestCase):
	def test_loads_real_file(self) -> None:
		dialog = _load_sample()
		self.assertFalse(dialog.remastered)
		self.assertEqual(len(dialog.widgets), 11)
		self.assertEqual(dialog.widgets[0].type, BINWidget.TYPE_DIALOG)

	def test_decodes_widget_strings(self) -> None:
		dialog = _load_sample()
		self.assertIn('GameMenu', [widget.string for widget in dialog.widgets])

	def test_legacy_to_remastered_fallback(self) -> None:
		# A dialog with an HTML widget can only be read as remastered; load
		# tries legacy first, fails on the unknown widget type, and falls back.
		source = DialogBIN()
		source.widgets.append(BINWidget(BINWidget.TYPE_HTML))
		loaded = DialogBIN()
		loaded.load(IO.output_to_bytes(lambda f: source.save(f, remastered=True)))
		self.assertTrue(loaded.remastered)

	def test_corrupt_data_raises(self) -> None:
		with self.assertRaises(PyMSError):
			DialogBIN().load(io.BytesIO(b'\x00' * 4))


class Test_save(unittest.TestCase):
	def test_real_file_binary_round_trip(self) -> None:
		original = IO.output_to_bytes(_load_sample().save)
		reloaded = DialogBIN()
		reloaded.load(original)
		self.assertEqual(IO.output_to_bytes(reloaded.save), original)

	def test_crafted_round_trip_preserves_widgets(self) -> None:
		source = DialogBIN()
		button = BINWidget(BINWidget.TYPE_BUTTON)
		button.string = 'OK'
		button.x1, button.y1, button.x2, button.y2 = 10, 20, 110, 50
		source.widgets.append(button)
		data = IO.output_to_bytes(source.save)
		loaded = DialogBIN()
		loaded.load(data)
		self.assertEqual(len(loaded.widgets), 2)
		self.assertEqual(loaded.widgets[1].string, 'OK')
		self.assertEqual(IO.output_to_bytes(loaded.save), data)


class Test_text_round_trip(unittest.TestCase):
	def test_decompile_interpret_is_stable(self) -> None:
		dialog = _load_sample()
		text = _decompile(dialog)
		reinterpreted = DialogBIN()
		reinterpreted.interpret_file(io.StringIO(text))
		self.assertEqual(_decompile(reinterpreted), text)

	def test_interpret_reproduces_binary(self) -> None:
		dialog = _load_sample()
		text = _decompile(dialog)
		reinterpreted = DialogBIN()
		reinterpreted.interpret_file(io.StringIO(text))
		self.assertEqual(IO.output_to_bytes(reinterpreted.save), IO.output_to_bytes(dialog.save))

	def test_decompile_emits_one_attribute_per_line(self) -> None:
		text = _decompile(_load_sample())
		widget_lines = [line.strip() for line in text.split('\n') if line.startswith('\t')]
		self.assertIn('string GameMenu', [' '.join(line.split()) for line in widget_lines])
