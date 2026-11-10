from ...FileFormats.Graft import Button, ButtonSet, ButtonCard
from ...FileFormats.Graft.CodeHandlers import ButtonCodeCommands

import unittest

MOVE = Button(position=1, icon=228, condition=ButtonCodeCommands.CanMove.function_index, action=9, enabled_string=664)
TRAIN = Button(position=1, icon=0, condition=ButtonCodeCommands.CanCreateOrMorph.function_index, condition_param=0, action=ButtonCodeCommands.ShowButtonCard.function_index, action_param=7, enabled_string=1, disabled_string=2)

class Test_Button(unittest.TestCase):
	def test_block_round_trip(self) -> None:
		for button in (MOVE, TRAIN):
			with self.subTest(button=button):
				self.assertEqual(Button.from_block(button.to_block()), button)

	def test_block_has_the_position_command(self) -> None:
		block = Button(position=7).to_block()
		self.assertEqual(block.header_params, [])
		self.assertEqual(block.param(ButtonCodeCommands.Position), 7)

	def test_block_drops_the_unused_parameter(self) -> None:
		button = Button(condition=ButtonCodeCommands.CanMove.function_index, condition_param=12, action=9, action_param=34)
		self.assertEqual(Button.from_block(button.to_block()), Button(condition=ButtonCodeCommands.CanMove.function_index, action=9))

	def test_known_functions_have_no_problem(self) -> None:
		self.assertIsNone(MOVE.find_unknown_function())

	def test_unknown_condition(self) -> None:
		self.assertEqual(Button(condition=len(ButtonCodeCommands.condition_commands)).find_unknown_function(), f'unknown button condition {len(ButtonCodeCommands.condition_commands)}')

	def test_unknown_action(self) -> None:
		self.assertEqual(Button(action=len(ButtonCodeCommands.action_commands)).find_unknown_function(), f'unknown button action {len(ButtonCodeCommands.action_commands)}')

class Test_ButtonSet(unittest.TestCase):
	def test_copy_is_deep(self) -> None:
		button_set = ButtonSet([MOVE.copy()])
		copy = button_set.copy()
		self.assertEqual(copy, button_set)
		copy.buttons[0].icon = 1
		copy.buttons.append(TRAIN.copy())
		self.assertEqual(button_set, ButtonSet([MOVE]))

	def test_block_round_trip(self) -> None:
		button_set = ButtonSet([MOVE, TRAIN])
		block = button_set.to_block(4)
		self.assertEqual(block.header_params, [4])
		self.assertEqual(ButtonSet.from_block(block), button_set)

	def test_empty_block_round_trip(self) -> None:
		self.assertEqual(ButtonSet.from_block(ButtonSet().to_block(0)), ButtonSet())

	def test_problem_is_the_first_unknown_function(self) -> None:
		self.assertIsNone(ButtonSet([MOVE, TRAIN]).find_unknown_function())
		button_set = ButtonSet([MOVE, Button(action=len(ButtonCodeCommands.action_commands)), Button(condition=len(ButtonCodeCommands.condition_commands))])
		self.assertEqual(button_set.find_unknown_function(), f'unknown button action {len(ButtonCodeCommands.action_commands)}')

class Test_ButtonCard(unittest.TestCase):
	def test_block_round_trip(self) -> None:
		for card in (ButtonCard(), ButtonCard(3, None), ButtonCard(None, 7), ButtonCard(2, 0)):
			with self.subTest(card=card):
				block = card.to_block(5)
				self.assertEqual(block.header_params, [5])
				self.assertEqual(ButtonCard.from_block(block), card)
