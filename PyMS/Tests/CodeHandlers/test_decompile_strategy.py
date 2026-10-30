
# pylint: disable=protected-access

from ...Utilities.CodeHandlers.CodeBlock import CodeBlock
from ...Utilities.CodeHandlers.DecompileStrategy import DecompileStrategy, DecompileStrategyBuilder
from ...Utilities.PyMSError import PyMSError

import unittest, threading


class FakeHeader:
	def __init__(self, name: str, entry_points=None) -> None:
		self._name = name
		self._entry_points = entry_points if entry_points is not None else []

	def get_name(self) -> str:
		return self._name

	def get_entry_points(self):
		return self._entry_points

	def has_entry_point(self, entry_point) -> bool:
		return any(entry_point is block for block, _ in self._entry_points)

	def serialize(self, serialize_context) -> None:
		pass


class Test_DecompileStrategy(unittest.TestCase):
	def test_empty(self) -> None:
		strategy = DecompileStrategy.empty()
		self.assertEqual(list(strategy.items), [])
		self.assertEqual(dict(strategy.labels), {})

	def test_block_label_missing_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			DecompileStrategy.empty().block_label(CodeBlock())
		self.assertIn('Decompile strategy missing label for block', str(cm.exception))

	def test_block_comment_default_none(self) -> None:
		self.assertIsNone(DecompileStrategy.empty().block_comment(CodeBlock()))


class Test_DecompileStrategyBuilder(unittest.TestCase):
	def test_single_header_block_label_from_header_name(self) -> None:
		block = CodeBlock()
		builder = DecompileStrategyBuilder()
		builder.add_header(FakeHeader('main', [(block, None)]))
		strategy = builder.build()
		self.assertEqual(strategy.block_label(block), 'main_0000')

	def test_block_without_header_is_unused(self) -> None:
		block = CodeBlock()
		builder = DecompileStrategyBuilder()
		builder.add_block(block)
		strategy = builder.build()
		self.assertEqual(strategy.block_label(block), 'unused_0000')

	def test_block_shared_by_two_headers(self) -> None:
		block = CodeBlock()
		builder = DecompileStrategyBuilder()
		builder.add_header(FakeHeader('aaa', [(block, None)]))
		builder.add_header(FakeHeader('bbb', [(block, None)]))
		strategy = builder.build()
		self.assertTrue(strategy.block_label(block).startswith('shared'))
		comment = strategy.block_comment(block)
		assert comment is not None
		self.assertIn('aaa', comment)
		self.assertIn('bbb', comment)

	def test_label_sanitizes_non_identifier_characters(self) -> None:
		block = CodeBlock()
		builder = DecompileStrategyBuilder()
		builder.add_header(FakeHeader('a b!c', [(block, None)]))
		strategy = builder.build()
		# Spaces and punctuation become underscores.
		self.assertNotIn(' ', strategy.block_label(block))
		self.assertNotIn('!', strategy.block_label(block))

	def test_build_terminates_when_external_header_already_present(self) -> None:
		# build() processes pending external headers; if one is already in the
		# items list it must still make progress rather than spin forever.
		builder = DecompileStrategyBuilder()
		header = FakeHeader('present', [])
		builder.items.append(header)
		builder._external_headers.append(header)

		finished: list[bool] = []

		def run() -> None:
			builder.build()
			finished.append(True)

		thread = threading.Thread(target=run, daemon=True)
		thread.start()
		thread.join(1.0)
		self.assertTrue(finished, 'build() did not terminate')


if __name__ == '__main__':
	unittest.main()
