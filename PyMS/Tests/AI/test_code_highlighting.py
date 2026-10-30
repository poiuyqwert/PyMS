from ...PyAI.CodeEditDialog import CodeEditDialog
from ...PyAI.Config import PyAIConfig

import unittest


class Test_PyAI_syntax_highlighting(unittest.TestCase):
	def setUp(self) -> None:
		self.highlighting = CodeEditDialog.build_syntax_highlighting(PyAIConfig().code.highlights)

	def _spans(self, line: str) -> list[tuple[str, str]]:
		return [(tag, line[head:tail]) for tag, head, tail in self.highlighting.highlight_spans(line)]

	def test_double_quoted_string_with_tbl(self) -> None:
		spans = self._spans('debug(b, "Hi<44> 2") # "c"')
		self.assertIn(('String', '"Hi<44> 2"'), spans)
		self.assertIn(('TBLFormat', '<44>'), spans)
		self.assertNotIn(('Number', '2'), spans)
		self.assertIn(('Comment', '# "c"'), spans)

	def test_single_quoted_string_with_escape(self) -> None:
		self.assertIn(('String', "'Don\\'t'"), self._spans("x 'Don\\'t' 3"))

	def test_hash_inside_string_is_not_comment(self) -> None:
		spans = self._spans('"a # b"')
		self.assertEqual(spans, [('String', '"a # b"')])

	def test_tbl_outside_string_not_highlighted(self) -> None:
		self.assertNotIn('TBLFormat', [tag for tag, _ in self._spans('<0>')])

	def test_unclosed_quote_not_string(self) -> None:
		self.assertNotIn('String', [tag for tag, _ in self._spans("Don't")])

	def test_components_listed_once(self) -> None:
		names = [component.name for component in self.highlighting.all_highlight_components()]
		self.assertEqual(names.count('String'), 1)
		self.assertEqual(names.count('TBL Format'), 1)
