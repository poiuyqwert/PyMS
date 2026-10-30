
from ...Utilities.CodeHandlers.CodeHeader import CodeHeader
from ...Utilities.CodeHandlers.CodeBlock import CodeBlock
from ...Utilities.CodeHandlers.SerializeContext import SerializeContext

import unittest


class FakeHeader(CodeHeader):
	def __init__(self, entry_points: list[tuple[CodeBlock, str | None]]) -> None:
		self._entry_points = entry_points

	def get_name(self) -> str:
		return 'fake'

	def get_entry_points(self) -> list[tuple[CodeBlock, str | None]]:
		return self._entry_points

	def serialize(self, serialize_context: SerializeContext) -> None:
		pass


class Test_has_entry_point(unittest.TestCase):
	def test_true_for_listed_block(self) -> None:
		block = CodeBlock()
		header = FakeHeader([(block, 'main')])
		self.assertTrue(header.has_entry_point(block))

	def test_false_for_unlisted_block(self) -> None:
		header = FakeHeader([(CodeBlock(), 'main')])
		self.assertFalse(header.has_entry_point(CodeBlock()))

	def test_false_when_no_entry_points(self) -> None:
		header = FakeHeader([])
		self.assertFalse(header.has_entry_point(CodeBlock()))
