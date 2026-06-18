
from ...Utilities.EditedState import EditedState

import unittest


class Test_EditedState(unittest.TestCase):
	def test_sub_state_edit_propagates_to_parent_callback(self) -> None:
		parent = EditedState()
		notifications: list[bool] = []
		parent.callback += notifications.append
		child = parent.sub_state()
		child.mark_edited(True)
		self.assertEqual(notifications[-1], True)

	def test_removed_sub_state_no_longer_notifies_parent(self) -> None:
		parent = EditedState()
		notifications: list[bool] = []
		parent.callback += notifications.append
		child = parent.sub_state()
		parent.remove_sub_state(child)
		notifications.clear()
		child.mark_edited(True)
		self.assertEqual(notifications, [])

	def test_removed_sub_state_does_not_count_toward_edited(self) -> None:
		parent = EditedState()
		child = parent.sub_state()
		child.mark_edited(True)
		self.assertTrue(parent.is_edited)
		parent.remove_sub_state(child)
		self.assertFalse(parent.is_edited)
