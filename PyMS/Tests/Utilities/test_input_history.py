
import unittest

from ...Utilities.UIKit.InputHistory import InputHistory
from ...Utilities import Config


class Test_InputHistory(unittest.TestCase):
	def test_empty_entry_is_not_recorded(self) -> None:
		history = InputHistory()
		history.record('')
		self.assertEqual(history.entries, [])

	def test_most_recent_entry_is_first(self) -> None:
		history = InputHistory()
		history.record('a')
		history.record('b')
		self.assertEqual(history.entries, ['b', 'a'])

	def test_duplicate_moves_to_most_recent(self) -> None:
		history = InputHistory()
		for entry in ('a', 'b', 'c'):
			history.record(entry)
		history.record('a')
		self.assertEqual(history.entries, ['a', 'c', 'b'])

	def test_history_is_capped(self) -> None:
		history = InputHistory()
		for n in range(history.limit + 5):
			history.record(f'entry{n}')
		self.assertEqual(len(history.entries), history.limit)
		# The oldest entries are dropped, the most recent retained.
		self.assertEqual(history.entries[0], f'entry{history.limit + 4}')
		self.assertNotIn('entry0', history.entries)

	def test_custom_limit(self) -> None:
		history = InputHistory(limit=2)
		for entry in ('a', 'b', 'c'):
			history.record(entry)
		self.assertEqual(history.entries, ['c', 'b'])

	def test_config_backed_history_records_into_config_data(self) -> None:
		config = Config.List(value_type=str)
		history = InputHistory(config=config)
		history.record('a')
		self.assertEqual(config.data, ['a'])

	def test_config_backed_history_reads_through_after_decode(self) -> None:
		# Config.List rebinds `.data` on decode, so the history must read the
		# live list rather than capture it at construction time.
		config = Config.List(value_type=str)
		history = InputHistory(config=config)
		config.decode(['a', 'b'])
		history.record('c')
		self.assertEqual(config.data, ['c', 'a', 'b'])
		self.assertEqual(history.entries, ['c', 'a', 'b'])

	def test_oversized_history_is_trimmed_on_record(self) -> None:
		config = Config.List(value_type=str, defaults=[f'entry{n}' for n in range(15)])
		history = InputHistory(config=config)
		history.record('new')
		self.assertEqual(len(history.entries), history.limit)
		self.assertEqual(history.entries[0], 'new')


if __name__ == '__main__':
	unittest.main()
