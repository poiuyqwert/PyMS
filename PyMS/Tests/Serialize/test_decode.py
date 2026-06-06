
from ...Utilities.Serialize import IntEncoder, StrEncoder, IntFlagEncoder, Definition, IDMode, encode_text, decode_text, LineScanner, repeater_ignore, repeater_loop, repeater_repeat_last
from ...Utilities.PyMSError import PyMSError

import unittest


class Sample:
	def __init__(self, count: int = 0, label: str = '', flags: int = 0) -> None:
		self.count = count
		self.label = label
		self.flags = flags


def sample_definition() -> Definition:
	return Definition('Sample', IDMode.comment, {
		'count': IntEncoder(),
		'label': StrEncoder(),
	})


def count_definition() -> Definition:
	return Definition('Sample', IDMode.comment, {
		'count': IntEncoder(),
	})


def build_sample(_n: int, _definition: Definition) -> Sample:
	return Sample()


class Test_LineScanner(unittest.TestCase):
	def test_pop_returns_lines_in_order(self) -> None:
		scanner = LineScanner('one\ntwo')
		self.assertEqual(scanner.pop(), 'one')
		self.assertEqual(scanner.pop(), 'two')

	def test_pop_past_end_raises(self) -> None:
		scanner = LineScanner('only')
		scanner.pop()
		with self.assertRaises(PyMSError):
			scanner.pop()

	def test_peek_does_not_advance(self) -> None:
		scanner = LineScanner('one\ntwo')
		self.assertEqual(scanner.peek(), 'one')
		self.assertEqual(scanner.peek(), 'one')
		self.assertEqual(scanner.pop(), 'one')

	def test_peek_at_end_raises(self) -> None:
		scanner = LineScanner('only')
		scanner.pop()
		with self.assertRaises(PyMSError):
			scanner.peek()

	def test_skip_advances_without_returning(self) -> None:
		scanner = LineScanner('one\ntwo')
		scanner.skip()
		self.assertEqual(scanner.pop(), 'two')

	def test_at_end_tracks_position(self) -> None:
		scanner = LineScanner('one\ntwo')
		self.assertFalse(scanner.at_end())
		scanner.pop()
		self.assertFalse(scanner.at_end())
		scanner.pop()
		self.assertTrue(scanner.at_end())

	def test_empty_text_is_immediately_at_end(self) -> None:
		self.assertTrue(LineScanner('').at_end())


class Test_repeaters(unittest.TestCase):
	def test_ignore_returns_index_within_count(self) -> None:
		self.assertEqual(repeater_ignore(2, 0, 4), 0)
		self.assertEqual(repeater_ignore(2, 1, 4), 1)

	def test_ignore_returns_none_past_count(self) -> None:
		self.assertIsNone(repeater_ignore(2, 2, 4))

	def test_loop_wraps_around(self) -> None:
		self.assertEqual(repeater_loop(2, 2, 4), 0)
		self.assertEqual(repeater_loop(2, 3, 4), 1)

	def test_repeat_last_clamps_to_final_index(self) -> None:
		self.assertEqual(repeater_repeat_last(2, 0, 4), 0)
		self.assertEqual(repeater_repeat_last(2, 1, 4), 1)
		self.assertEqual(repeater_repeat_last(2, 3, 4), 1)


class Test_decode_text(unittest.TestCase):
	def test_round_trip_single_object(self) -> None:
		definition = sample_definition()
		original = Sample(count=5, label='hi')
		text = encode_text(original, 0, definition)
		result = decode_text(text, [definition], build_sample)
		self.assertEqual(len(result), 1)
		self.assertEqual(result[0].count, 5)
		self.assertEqual(result[0].label, 'hi')

	def test_round_trip_multiline_value(self) -> None:
		definition = sample_definition()
		text = encode_text(Sample(count=1, label='one\ntwo'), 0, definition)
		result = decode_text(text, [definition], build_sample)
		self.assertEqual(result[0].label, 'one\ntwo')

	def test_round_trip_multiple_objects(self) -> None:
		definition = count_definition()
		text = encode_text(Sample(count=10), 0, definition) + '\n' + encode_text(Sample(count=20), 1, definition)
		result = decode_text(text, [definition], build_sample)
		self.assertEqual([s.count for s in result], [10, 20])

	def test_round_trip_flags(self) -> None:
		definition = Definition('Sample', IDMode.none, {
			'flags': IntFlagEncoder({'a': 1, 'b': 2, 'c': 4}),
		})
		text = encode_text(Sample(flags=5), None, definition)
		result = decode_text(text, [definition], build_sample)
		self.assertEqual(result[0].flags, 5)

	def test_comments_and_blank_lines_ignored(self) -> None:
		definition = sample_definition()
		text = '# leading comment\nSample:\n\tcount 5 // trailing comment\n'
		result = decode_text(text, [definition], build_sample)
		self.assertEqual(result[0].count, 5)

	def test_objs_with_ignore_repeater_stops_early(self) -> None:
		definition = count_definition()
		text = encode_text(Sample(count=10), 0, definition) + '\n' + encode_text(Sample(count=20), 1, definition)
		result = decode_text(text, [definition], build_sample, objs=4, repeater=repeater_ignore)
		self.assertEqual([s.count for s in result], [10, 20])

	def test_objs_with_loop_repeater_cycles(self) -> None:
		definition = count_definition()
		text = encode_text(Sample(count=10), 0, definition) + '\n' + encode_text(Sample(count=20), 1, definition)
		result = decode_text(text, [definition], build_sample, objs=4, repeater=repeater_loop)
		self.assertEqual([s.count for s in result], [10, 20, 10, 20])

	def test_objs_with_repeat_last_repeater(self) -> None:
		definition = count_definition()
		text = encode_text(Sample(count=10), 0, definition) + '\n' + encode_text(Sample(count=20), 1, definition)
		result = decode_text(text, [definition], build_sample, objs=4, repeater=repeater_repeat_last)
		self.assertEqual([s.count for s in result], [10, 20, 20, 20])


class Test_decode_text_errors(unittest.TestCase):
	def test_empty_text_raises(self) -> None:
		with self.assertRaises(PyMSError):
			decode_text('', [sample_definition()], build_sample)

	def test_comment_only_text_raises(self) -> None:
		with self.assertRaises(PyMSError):
			decode_text('# just a comment\n', [sample_definition()], build_sample)

	def test_field_before_type_raises(self) -> None:
		with self.assertRaises(PyMSError):
			decode_text('\tcount 5\n', [sample_definition()], build_sample)

	def test_unknown_type_raises(self) -> None:
		with self.assertRaises(PyMSError):
			decode_text('Unknown:\n\tcount 5\n', [sample_definition()], build_sample)

	def test_empty_object_raises(self) -> None:
		with self.assertRaises(PyMSError):
			decode_text('Sample:\n', [sample_definition()], build_sample)

	def test_unknown_field_raises(self) -> None:
		with self.assertRaises(PyMSError):
			decode_text('Sample:\n\tbogus 5\n', [sample_definition()], build_sample)

	def test_unexpected_line_raises(self) -> None:
		with self.assertRaises(PyMSError):
			decode_text('Sample:\n??? nope\n', [sample_definition()], build_sample)
