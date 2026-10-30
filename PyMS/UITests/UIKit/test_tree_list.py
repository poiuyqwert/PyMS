
from ..harness import UITestCase

from ...Utilities import UIKit as UI


# (name, children) where children is None for a leaf. Every group is expanded,
# mirroring how the Help dialog builds its tree.
_TREE = [
	('A', [
		('a1', None),
		('AG1', [
			('g1a', None),
			('g1b', None),
			('g1c', None),
		]),
		('AG2', [
			('AG2N', [
				('n1', None),
			]),
			('g2a', None),
		]),
		('a2', None),
	]),
	('B', [
		('b1', None),
		('BG', [
			('bg1', None),
		]),
		('b2', None),
	]),
]

_ALL_ROWS = ['A', 'a1', 'AG1', 'g1a', 'g1b', 'g1c', 'AG2', 'AG2N', 'n1', 'g2a', 'a2', 'B', 'b1', 'BG', 'bg1', 'b2']


class Test_TreeList(UITestCase):
	def _tree(self) -> UI.TreeList:
		window = self.make_window(UI.MainWindow)
		tree = UI.TreeList(window, width=30, height=20)
		tree.pack()
		tree.build(
			[(node, True) for node in _TREE],
			lambda node: [(child, None if child[1] is None else True) for child in (node[1] or [])],
			lambda node: node[0]
		)
		self.pump(window)
		return tree

	def _visible_rows(self, tree: UI.TreeList) -> list[str]:
		return [line.strip() for line in tree.text.get('1.0', UI.END).split('\n') if line.strip()]

	def _row_entries(self, tree: UI.TreeList) -> list[int]:
		# The entry tag found on each text line, in display order.
		entries: list[int] = []
		line_count = int(tree.text.index('end -1c').split('.')[0])
		for line in range(1, line_count + 1):
			line_entries: set[int] = set()
			for col in range(int(tree.text.index(f'{line}.0 lineend').split('.')[1])):
				line_entries.update(int(tag[5:]) for tag in tree.text.tag_names(f'{line}.{col}') if tag.startswith('entry'))
			self.assertLessEqual(len(line_entries), 1, f'line {line} carries multiple entries')
			entries.extend(line_entries)
		return entries

	def test_initial_rows_are_preorder(self) -> None:
		tree = self._tree()
		self.assertEqual(self._visible_rows(tree), _ALL_ROWS)

	def test_collapse_hides_only_descendants(self) -> None:
		tree = self._tree()
		tree.toggle('0')
		self.assertEqual(self._visible_rows(tree), ['A', 'B', 'b1', 'BG', 'bg1', 'b2'])

	def test_collapse_then_expand_restores_nested_expanded_groups(self) -> None:
		tree = self._tree()
		entries = self._row_entries(tree)
		tree.toggle('0')
		tree.toggle('0')
		self.assertEqual(self._visible_rows(tree), _ALL_ROWS)
		self.assertEqual(self._row_entries(tree), entries)

	def test_repeated_toggle_keeps_following_siblings_intact(self) -> None:
		tree = self._tree()
		entries = self._row_entries(tree)
		for _ in range(3):
			tree.toggle('0')
			self.assertEqual(self._visible_rows(tree), ['A', 'B', 'b1', 'BG', 'bg1', 'b2'])
			tree.toggle('0')
			self.assertEqual(self._visible_rows(tree), _ALL_ROWS)
		self.assertEqual(self._row_entries(tree), entries)

	def test_toggle_nested_group_round_trips(self) -> None:
		tree = self._tree()
		tree.toggle('0.2')
		self.assertEqual(self._visible_rows(tree), ['A', 'a1', 'AG1', 'g1a', 'g1b', 'g1c', 'AG2', 'a2', 'B', 'b1', 'BG', 'bg1', 'b2'])
		tree.toggle('0')
		tree.toggle('0')
		self.assertEqual(self._visible_rows(tree), ['A', 'a1', 'AG1', 'g1a', 'g1b', 'g1c', 'AG2', 'a2', 'B', 'b1', 'BG', 'bg1', 'b2'])
		tree.toggle('0.2')
		self.assertEqual(self._visible_rows(tree), _ALL_ROWS)
