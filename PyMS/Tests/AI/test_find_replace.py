
import unittest

from ...PyAI.FindReplaceDialog import FindReplaceDialog


class Test_RecordHistory(unittest.TestCase):
	def test_empty_entry_is_not_recorded(self) -> None:
		history: list[str] = []
		FindReplaceDialog.record_history(history, '')
		self.assertEqual(history, [])

	def test_duplicate_moves_to_most_recent(self) -> None:
		history = ['a', 'b', 'c']
		FindReplaceDialog.record_history(history, 'a')
		self.assertEqual(history, ['b', 'c', 'a'])

	def test_new_entry_appended(self) -> None:
		history = ['a', 'b']
		FindReplaceDialog.record_history(history, 'c')
		self.assertEqual(history, ['a', 'b', 'c'])

	def test_history_is_capped(self) -> None:
		history: list[str] = []
		for n in range(FindReplaceDialog.HISTORY_LIMIT + 5):
			FindReplaceDialog.record_history(history, f'entry{n}')
		self.assertEqual(len(history), FindReplaceDialog.HISTORY_LIMIT)
		# The oldest entries are dropped, the most recent retained.
		self.assertEqual(history[-1], f'entry{FindReplaceDialog.HISTORY_LIMIT + 4}')
		self.assertNotIn('entry0', history)


if __name__ == '__main__':
	unittest.main()
