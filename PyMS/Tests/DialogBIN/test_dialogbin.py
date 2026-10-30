
from ...FileFormats.DialogBIN import DialogBIN, BINWidget, BINSMK
from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO
from ..utils import resource_path

import io
import unittest

SAMPLE_BIN = 'gamemenu.bin'
ANSI_SAMPLE_BIN = 'titledlg.bin'


def _load_sample() -> DialogBIN:
	dialog = DialogBIN()
	dialog.load(resource_path(SAMPLE_BIN, __file__))
	return dialog


def _load_ansi_sample() -> DialogBIN:
	dialog = DialogBIN()
	dialog.load(resource_path(ANSI_SAMPLE_BIN, __file__))
	return dialog


def _decompile(dialog: DialogBIN) -> str:
	output = io.StringIO()
	dialog.decompile(output)
	return output.getvalue()


def _interpret(text: str) -> DialogBIN:
	dialog = DialogBIN()
	dialog.interpret(io.StringIO(text))
	return dialog


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

	def test_decodes_smk_filename(self) -> None:
		# SMK filenames are stored as a null-terminated byte string in the file
		# and must be decoded to str on load, like widget strings.
		source = DialogBIN()
		image = BINWidget(BINWidget.TYPE_IMAGE)
		smk = BINSMK()
		smk.filename = 'smk\\portrait.smk'
		image.smk = smk
		source.widgets.append(image)
		source.smks.append(smk)
		loaded = DialogBIN()
		loaded.load(IO.output_to_bytes(source.save))
		self.assertEqual(len(loaded.smks), 1)
		self.assertEqual(loaded.smks[0].filename, 'smk\\portrait.smk')
		self.assertIsInstance(loaded.smks[0].filename, str)

	def test_corrupt_data_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			DialogBIN().load(b'\x00' * 4)
		self.assertIn('Unsupported Dialog BIN file, could possibly be corrupt', str(cm.exception))

	def test_loads_legacy_file_with_ansi_strings(self) -> None:
		# Legacy (pre-Remastered) BINs store strings in the Windows ANSI code
		# page; bytes like 0xA9 (copyright sign) are not valid UTF-8 but must
		# still decode instead of aborting the legacy parse.
		dialog = _load_ansi_sample()
		self.assertFalse(dialog.remastered)
		self.assertEqual(len(dialog.widgets), 6)
		strings = [widget.string for widget in dialog.widgets]
		self.assertIn('Copyright © 1998 Blizzard Entertainment. All rights reserved.', strings)
		identifiers = [widget.identifier for widget in dialog.widgets]
		self.assertIn(65525, identifiers)
		self.assertIn(65526, identifiers)

	def test_loads_legacy_file_with_utf8_strings(self) -> None:
		# Legacy-layout files whose strings happen to be valid UTF-8 (e.g.
		# previously saved by PyBIN) must keep decoding as UTF-8.
		source = DialogBIN()
		label = BINWidget(BINWidget.TYPE_LABEL_LEFT_ALIGN)
		label.string = 'Xc'
		source.widgets.append(label)
		data = IO.output_to_bytes(lambda f: source.save(f, remastered=False))
		# Patch in a same-length UTF-8 encoding of a non-ASCII string so the
		# offsets stay valid.
		data = data.replace(b'Xc\x00', '©'.encode('utf-8') + b'\x00')
		loaded = DialogBIN()
		loaded.load(data)
		self.assertEqual(loaded.widgets[1].string, '©')


class Test_save(unittest.TestCase):
	def test_real_file_binary_round_trip(self) -> None:
		original = IO.output_to_bytes(_load_sample().save)
		reloaded = DialogBIN()
		reloaded.load(original)
		self.assertEqual(IO.output_to_bytes(reloaded.save), original)

	def test_ansi_file_binary_round_trip(self) -> None:
		# Legacy files must save their strings back in the ANSI code page
		# (readable by legacy StarCraft), and the result must round-trip.
		original = IO.output_to_bytes(_load_ansi_sample().save)
		self.assertIn('Copyright © 1998'.encode('cp1252'), original)
		reloaded = DialogBIN()
		reloaded.load(original)
		self.assertFalse(reloaded.remastered)
		self.assertEqual(IO.output_to_bytes(reloaded.save), original)

	def test_legacy_save_rejects_non_ansi_strings(self) -> None:
		dialog = DialogBIN()
		label = BINWidget(BINWidget.TYPE_LABEL_LEFT_ALIGN)
		label.string = '你'
		dialog.widgets.append(label)
		with self.assertRaises(PyMSError) as cm:
			IO.output_to_bytes(lambda f: dialog.save(f, remastered=False))
		self.assertIn("can't be encoded in a legacy Dialog BIN", str(cm.exception))

	def test_remastered_save_round_trips_non_ansi_strings(self) -> None:
		source = DialogBIN()
		label = BINWidget(BINWidget.TYPE_LABEL_LEFT_ALIGN)
		label.string = '你好'
		source.widgets.append(label)
		data = IO.output_to_bytes(lambda f: source.save(f, remastered=True))
		loaded = DialogBIN()
		loaded.load(data)
		self.assertEqual(loaded.widgets[1].string, '你好')
		self.assertEqual(IO.output_to_bytes(lambda f: loaded.save(f, remastered=True)), data)

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
		for load in (_load_sample, _load_ansi_sample):
			dialog = load()
			text = _decompile(dialog)
			reinterpreted = _interpret(text)
			self.assertEqual(_decompile(reinterpreted), text)

	def test_interpret_reproduces_binary(self) -> None:
		for load in (_load_sample, _load_ansi_sample):
			dialog = load()
			reinterpreted = _interpret(_decompile(dialog))
			self.assertEqual(IO.output_to_bytes(reinterpreted.save), IO.output_to_bytes(dialog.save))

	def test_decompile_emits_one_attribute_per_line(self) -> None:
		text = _decompile(_load_sample())
		widget_lines = [line.strip() for line in text.split('\n') if line.startswith('\t')]
		self.assertIn('string GameMenu', [' '.join(line.split()) for line in widget_lines])

	def test_decompile_emits_named_types_and_flags(self) -> None:
		text = _decompile(_load_sample())
		self.assertIn('\ttype dialog\n', text)
		self.assertIn('\ttype button\n', text)
		self.assertIn('\tflags.visible 1\n', text)

	def test_empty_string_round_trips(self) -> None:
		dialog = DialogBIN()
		dialog.widgets[0].string = ''
		text = _decompile(dialog)
		self.assertIn('\tstring:\n', text)
		self.assertEqual(_interpret(text).widgets[0].string, '')

	def test_escaped_strings_round_trip(self) -> None:
		strings = ('a#b', 'a//b', ' leading', 'trailing ', '\x07hotkey', 'lit<32>eral')
		dialog = DialogBIN()
		for string in strings:
			widget = BINWidget(BINWidget.TYPE_LABEL_LEFT_ALIGN)
			widget.string = string
			dialog.add_widget(widget)
		loaded = _interpret(_decompile(dialog))
		self.assertEqual(tuple(widget.string for widget in loaded.widgets[1:]), strings)

	def test_widget_flags_are_lossless(self) -> None:
		dialog = DialogBIN()
		dialog.widgets[0].flags = 0xFFFFFFFF
		self.assertEqual(_interpret(_decompile(dialog)).widgets[0].flags, 0xFFFFFFFF)

	def test_smk_flags_are_lossless(self) -> None:
		dialog = DialogBIN()
		smk = BINSMK()
		smk.flags = 0xFFFF
		dialog.smks.append(smk)
		self.assertEqual(_interpret(_decompile(dialog)).smks[0].flags, 0xFFFF)

	def test_smk_references_round_trip(self) -> None:
		dialog = DialogBIN()
		base = BINSMK()
		base.filename = 'smk\\base.smk'
		overlay = BINSMK()
		overlay.filename = 'smk\\overlay.smk'
		overlay.overlay_smk = base
		dialog.smks.extend((base, overlay))
		image = BINWidget(BINWidget.TYPE_IMAGE)
		image.smk = overlay
		dialog.add_widget(image)
		text = _decompile(dialog)
		self.assertIn('SMK(0):\n', text)
		self.assertIn('SMK(1):\n', text)
		loaded = _interpret(text)
		self.assertEqual(len(loaded.smks), 2)
		self.assertIsNone(loaded.smks[0].overlay_smk)
		self.assertIs(loaded.smks[1].overlay_smk, loaded.smks[0])
		self.assertIsNone(loaded.widgets[0].smk)
		self.assertIs(loaded.widgets[1].smk, loaded.smks[1])

	def test_decompile_unlisted_smk_raises(self) -> None:
		dialog = DialogBIN()
		image = BINWidget(BINWidget.TYPE_IMAGE)
		image.smk = BINSMK()
		dialog.add_widget(image)
		with self.assertRaises(PyMSError) as cm:
			_decompile(dialog)
		self.assertIn("Referenced 'SMK' object has no ID", str(cm.exception))

	def test_remastered_field_presence_round_trips(self) -> None:
		dialog = DialogBIN()
		remastered_text = io.StringIO()
		dialog.decompile(remastered_text, remastered=True)
		self.assertIn('\tscr_unknown1 0\n', remastered_text.getvalue())
		self.assertTrue(_interpret(remastered_text.getvalue()).remastered)
		legacy_text = _decompile(dialog)
		self.assertNotIn('scr_unknown1', legacy_text)
		self.assertFalse(_interpret(legacy_text).remastered)


class Test_interpret(unittest.TestCase):
	def test_type_accepts_names_and_ints(self) -> None:
		dialog = _interpret('Widget:\n\ttype dialog\n\nWidget:\n\ttype 2\n')
		self.assertEqual(dialog.widgets[0].type, BINWidget.TYPE_DIALOG)
		self.assertEqual(dialog.widgets[1].type, BINWidget.TYPE_BUTTON)

	def test_invalid_type_name_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_interpret('Widget:\n\ttype bogus\n')
		self.assertIn('is not a valid widget type', str(cm.exception))

	def test_dialog_widget_is_moved_to_front(self) -> None:
		dialog = _interpret('Widget:\n\ttype button\n\nWidget:\n\ttype dialog\n')
		self.assertEqual(dialog.widgets[0].type, BINWidget.TYPE_DIALOG)
		self.assertEqual(dialog.widgets[1].type, BINWidget.TYPE_BUTTON)

	def test_no_dialog_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_interpret('Widget:\n\ttype button\n')
		self.assertIn('No dialog found.', str(cm.exception))

	def test_missing_smk_reference_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_interpret('Widget:\n\ttype dialog\n\tsmk 5\n')
		self.assertIn("'SMK' object with ID '5' is missing", str(cm.exception))

	def test_duplicate_smk_id_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_interpret('SMK(0):\n\tflags.fade_in 0\n\nSMK(0):\n\tflags.dark 0\n\nWidget:\n\ttype dialog\n')
		self.assertIn("Duplicate ID '0' for 'SMK' object", str(cm.exception))

	def test_smk_without_id_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_interpret('SMK:\n\tflags.fade_in 0\n\nWidget:\n\ttype dialog\n')
		self.assertIn("'SMK' object is missing an ID", str(cm.exception))

	def test_invalid_smk_reference_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_interpret('Widget:\n\ttype dialog\n\tsmk bogus\n')
		self.assertIn('Invalid SMK reference', str(cm.exception))

	def test_invalid_field_name_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_interpret('Widget:\n\tbogus 5\n')
		self.assertIn('is not a valid field name', str(cm.exception))

	def test_flags_require_named_sub_fields(self) -> None:
		# The old text format's bare binary flag strings are not valid input
		with self.assertRaises(PyMSError) as cm:
			_interpret('Widget:\n\ttype dialog\n\tflags 00000000000000000000000000001000\n')
		self.assertIn("'flags' needs a sub-field", str(cm.exception))

	def test_empty_text_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_interpret('')
		self.assertIn('Nothing to decode.', str(cm.exception))
