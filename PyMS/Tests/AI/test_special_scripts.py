import unittest

from ...FileFormats.AIBIN.SpecialScripts import SPECIAL_SCRIPTS, SpecialScriptPlayers, special_script_players


class Test_SpecialScripts(unittest.TestCase):
	def test_shared_vision_ids_run_on_any_player(self) -> None:
		self.assertEqual(special_script_players('+Vi3'), SpecialScriptPlayers.any_player)
		self.assertEqual(special_script_players('-Vi7'), SpecialScriptPlayers.any_player)

	def test_rescue_id_runs_on_computer_and_neutral(self) -> None:
		self.assertEqual(special_script_players('Rscu'), SpecialScriptPlayers.computer_and_neutral)

	def test_ordinary_id_is_not_special(self) -> None:
		self.assertIsNone(special_script_players('MYAI'))

	def test_ids_are_case_sensitive(self) -> None:
		self.assertIsNone(special_script_players('rscu'))

	def test_all_ids_are_four_characters(self) -> None:
		for script_id in SPECIAL_SCRIPTS:
			self.assertEqual(len(script_id), 4, script_id)

	def test_registry_size(self) -> None:
		self.assertEqual(len(SPECIAL_SCRIPTS), 21)


if __name__ == '__main__':
	unittest.main()
