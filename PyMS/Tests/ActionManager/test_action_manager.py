
from ...Utilities.ActionManager import ActionManager, ActionGroup

import unittest


class CountingAction:
	def __init__(self) -> None:
		self.applied = 0
		self.undone = 0

	def has_changes(self) -> bool:
		return True

	def apply(self) -> None:
		self.applied += 1

	def undo(self) -> None:
		self.undone += 1


class Test_end_group(unittest.TestCase):
	def test_collapsing_single_action_group_moves_without_reapplying(self) -> None:
		manager = ActionManager()
		action = CountingAction()
		group = ActionGroup()
		group.add_action(action)
		group.complete = True
		manager.actions.append(group)
		manager.end_group()
		self.assertEqual(action.applied, 1)
		self.assertEqual(manager.actions, [action])

	def test_empty_group_is_removed(self) -> None:
		manager = ActionManager()
		group = ActionGroup()
		group.complete = True
		manager.actions.append(group)
		manager.end_group()
		self.assertEqual(manager.actions, [])

	def test_multi_action_group_is_kept(self) -> None:
		manager = ActionManager()
		first = CountingAction()
		second = CountingAction()
		group = ActionGroup()
		group.add_action(first)
		group.add_action(second)
		group.complete = True
		manager.actions.append(group)
		manager.end_group()
		self.assertEqual(first.applied, 1)
		self.assertEqual(second.applied, 1)
		self.assertEqual(manager.actions, [group])
