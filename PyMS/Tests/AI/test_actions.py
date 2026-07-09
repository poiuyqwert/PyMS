
import unittest

from ...FileFormats.AIBIN import AIBIN
from ...FileFormats.AIBIN.AIScript import AIScript

from ...PyAI import Actions
from ...PyAI.Delegates import ActionDelegate


def _make_script(script_id: str, flags: int = 0, string_id: int = 0) -> AIScript:
	return AIScript(script_id, flags, string_id, AIScript.blank_entry_point(), False)


class _FakeDelegate(ActionDelegate):
	def __init__(self, ai_bin: AIBIN.AIBIN) -> None:
		self.ai_bin = ai_bin

	def get_ai_bin(self) -> AIBIN.AIBIN:
		return self.ai_bin

	def refresh_scripts(self, select_script_ids: list[str] | None = None) -> None:
		pass


class Test_EditScriptAction(unittest.TestCase):
	def test_rename_onto_existing_id_preserves_the_clobbered_script_on_undo(self) -> None:
		ai_bin = AIBIN.AIBIN()
		edited = _make_script('AAAA', string_id=1)
		victim = _make_script('BBBB', string_id=2)
		ai_bin.add_script(edited)
		ai_bin.add_script(victim)
		delegate = _FakeDelegate(ai_bin)

		action = Actions.EditScriptAction(delegate, edited, new_id='BBBB', new_flags=edited.flags, new_string_id=edited.string_id)
		action.apply()

		# The edited script now occupies the victim's ID.
		self.assertIs(ai_bin.get_script('BBBB'), edited)
		self.assertIsNone(ai_bin.get_script('AAAA'))

		action.undo()

		# Undo must restore both the edited script and the script it displaced.
		restored_edited = ai_bin.get_script('AAAA')
		self.assertIs(restored_edited, edited)
		self.assertIs(ai_bin.get_script('BBBB'), victim)
		# Each script remains registered as the sole owner of its own entry point.
		self.assertEqual(edited.entry_point.owners, [edited])
		self.assertEqual(victim.entry_point.owners, [victim])

	def test_rename_to_fresh_id_round_trips(self) -> None:
		ai_bin = AIBIN.AIBIN()
		edited = _make_script('AAAA')
		ai_bin.add_script(edited)
		delegate = _FakeDelegate(ai_bin)

		action = Actions.EditScriptAction(delegate, edited, new_id='CCCC', new_flags=edited.flags, new_string_id=edited.string_id)
		action.apply()
		self.assertIs(ai_bin.get_script('CCCC'), edited)
		self.assertIsNone(ai_bin.get_script('AAAA'))

		action.undo()
		self.assertIs(ai_bin.get_script('AAAA'), edited)
		self.assertIsNone(ai_bin.get_script('CCCC'))

	def test_edit_without_rename_leaves_no_phantom_replacement(self) -> None:
		ai_bin = AIBIN.AIBIN()
		edited = _make_script('AAAA', flags=0, string_id=1)
		ai_bin.add_script(edited)
		delegate = _FakeDelegate(ai_bin)

		action = Actions.EditScriptAction(delegate, edited, new_id='AAAA', new_flags=4, new_string_id=7)
		action.apply()
		self.assertEqual(edited.flags, 4)
		self.assertEqual(edited.string_id, 7)
		self.assertIsNone(action.replaced_script)

		action.undo()
		self.assertIs(ai_bin.get_script('AAAA'), edited)
		self.assertEqual(edited.flags, 0)
		self.assertEqual(edited.string_id, 1)


class Test_AddScriptAction(unittest.TestCase):
	def test_add_then_undo_round_trips(self) -> None:
		ai_bin = AIBIN.AIBIN()
		delegate = _FakeDelegate(ai_bin)
		script = _make_script('AAAA')

		action = Actions.AddScriptAction(delegate, script, None)
		action.apply()
		self.assertIs(ai_bin.get_script('AAAA'), script)
		self.assertEqual(script.entry_point.owners, [script])

		action.undo()
		self.assertIsNone(ai_bin.get_script('AAAA'))


if __name__ == '__main__':
	unittest.main()
