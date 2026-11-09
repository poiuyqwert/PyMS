
from ...Utilities.SyntaxHighlightingFile import SyntaxHighlightingFile
from ...Utilities.PyMSError import PyMSError
from ...Utilities import Config
from ...Utilities import UIKit as UI

import io, json, unittest

def _component(name: str, style: Config.Style) -> UI.HighlightComponent:
	return UI.HighlightComponent(name=name, description='', highlight_style=Config.HighlightStyle(default=style))

def _style(foreground: str | None = None, background: str | None = None, bold: bool = False) -> dict:
	return {'foreground': foreground, 'background': background, 'bold': bold}

class Test_SyntaxHighlightingFile(unittest.TestCase):
	def test_save_load_round_trip(self) -> None:
		components = [_component('Number', Config.Style(foreground='#FF0000')), _component('TBL Format', Config.Style(background='#E6E6E6', bold=True))]
		highlights_file = SyntaxHighlightingFile()
		highlights_file.update(components)
		output = io.StringIO()
		highlights_file.save(output)

		self.assertEqual(json.loads(output.getvalue()), {
			'version': 1,
			'highlights': {
				'number': _style(foreground='#FF0000'),
				'tbl_format': _style(background='#E6E6E6', bold=True),
			}
		})

		loaded = SyntaxHighlightingFile()
		loaded.load(io.StringIO(output.getvalue()))
		self.assertEqual(loaded.highlights, highlights_file.highlights)

	def test_update_keeps_keys_of_other_programs(self) -> None:
		highlights_file = SyntaxHighlightingFile()
		highlights_file.load(json.dumps({'version': 1, 'highlights': {'ai_id': _style(foreground='#123456'), 'number': _style(foreground='#000000')}}))
		highlights_file.update([_component('Number', Config.Style(foreground='#FF0000'))])
		self.assertEqual(highlights_file.highlights, {
			'ai_id': _style(foreground='#123456'),
			'number': _style(foreground='#FF0000'),
		})

	def test_apply_sets_matching_styles_and_counts_them(self) -> None:
		number = _component('Number', Config.Style(foreground='#FF0000'))
		comment = _component('Comment', Config.Style(foreground='#008000'))
		highlights_file = SyntaxHighlightingFile()
		highlights_file.load(json.dumps({'version': 1, 'highlights': {'number': _style(foreground='#00FF00', bold=True), 'ai_id': _style(foreground='#123456')}}))

		self.assertEqual(highlights_file.apply([number, comment]), 1)
		self.assertEqual(number.highlight_style.style, Config.Style(foreground='#00FF00', bold=True))
		self.assertEqual(comment.highlight_style.style, Config.Style(foreground='#008000'))

	def test_apply_counts_shared_key_once(self) -> None:
		highlights_file = SyntaxHighlightingFile()
		highlights_file.load(json.dumps({'version': 1, 'highlights': {'number': _style(foreground='#00FF00')}}))
		number = _component('Number', Config.Style())
		self.assertEqual(highlights_file.apply([number, number]), 1)

	def test_load_invalid_json(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			SyntaxHighlightingFile().load(io.StringIO('{not json'))
		self.assertIn('not valid JSON', str(cm.exception))

	def test_load_requires_object(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			SyntaxHighlightingFile().load(io.StringIO('[]'))
		self.assertIn('must contain a JSON object', str(cm.exception))

	def test_load_requires_version(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			SyntaxHighlightingFile().load(io.StringIO(json.dumps({'highlights': {}})))
		self.assertIn('missing a valid `version`', str(cm.exception))

	def test_load_rejects_newer_version(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			SyntaxHighlightingFile().load(io.StringIO(json.dumps({'version': 2, 'highlights': {}})))
		self.assertIn('newer than the supported version', str(cm.exception))

	def test_load_requires_highlights(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			SyntaxHighlightingFile().load(io.StringIO(json.dumps({'version': 1})))
		self.assertIn('missing the `highlights` object', str(cm.exception))
