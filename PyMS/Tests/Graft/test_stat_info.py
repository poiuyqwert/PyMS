from ...FileFormats.Graft import StatInfo
from ...FileFormats.Graft.CodeHandlers import StatInfoCodeCommands

import unittest

class Test_StatInfo(unittest.TestCase):
	def test_block_round_trip(self) -> None:
		info = StatInfo(12, StatInfoCodeCommands.ChangedBuilding.function_index, StatInfoCodeCommands.DrawBuilding.function_index)
		block = info.to_block(3)
		self.assertEqual(block.header_params, [3])
		self.assertEqual(StatInfo.from_block(block, 3), info)

	def test_debug_id_defaults_to_the_unit(self) -> None:
		block = StatInfo(0, StatInfoCodeCommands.ChangedUnit.function_index, StatInfoCodeCommands.DrawUnit.function_index).to_block(9)
		block.commands = [command for command in block.commands if command.definition is not StatInfoCodeCommands.DebugID]
		self.assertEqual(StatInfo.from_block(block, 9), StatInfo(9, StatInfoCodeCommands.ChangedUnit.function_index, StatInfoCodeCommands.DrawUnit.function_index))

	def test_known_functions_have_no_problem(self) -> None:
		self.assertIsNone(StatInfo(0, len(StatInfoCodeCommands.status_function_commands) - 1, len(StatInfoCodeCommands.display_function_commands) - 1).find_unknown_function())

	def test_unknown_status_function(self) -> None:
		status_function = len(StatInfoCodeCommands.status_function_commands)
		self.assertEqual(StatInfo(0, status_function, 0).find_unknown_function(), f'unknown status function {status_function}')

	def test_unknown_display_function(self) -> None:
		display_function = len(StatInfoCodeCommands.display_function_commands)
		self.assertEqual(StatInfo(0, 0, display_function).find_unknown_function(), f'unknown display function {display_function}')
