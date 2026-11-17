from ...PyGRAFT.JumpTarget import JumpTarget
from ...FileFormats.Graft.CodeHandlers import ButtonCodeCommands, RequirementCodeCommands, CodeTypes
from ...FileFormats.Graft.CodeHandlers.RequirementCodeCommands import ReqCommandDefinition

import unittest

# The parameters that reference something a Jump To button could jump to
REFERENCE_TYPES = (CodeTypes.UnitCodeType, CodeTypes.UpgradeCodeType, CodeTypes.TechCodeType)

# Functions whose parameter is a reference type, but which don't use it
UNUSED_PARAM_FUNCTIONS = {
	ButtonCodeCommands.Siege,
	ButtonCodeCommands.Stim,
	ButtonCodeCommands.Burrow,
	ButtonCodeCommands.Cloak,
	ButtonCodeCommands.Heal,
	ButtonCodeCommands.BuildSubunit,
	ButtonCodeCommands.ArchonWarp,
	ButtonCodeCommands.DarkArchonMeld,
}

class Test_JumpTarget(unittest.TestCase):
	def test_every_button_function_reference_is_mapped(self) -> None:
		# A new function with a reference parameter must be mapped to a target, or listed as unused
		for cmd_def in ButtonCodeCommands.condition_commands + ButtonCodeCommands.action_commands:
			with self.subTest(function=cmd_def.name):
				target = JumpTarget.for_button_function(cmd_def)
				references = bool(cmd_def.param_types) and isinstance(cmd_def.param_types[0], REFERENCE_TYPES)
				if cmd_def in UNUSED_PARAM_FUNCTIONS or not references:
					self.assertIsNone(target)
				else:
					self.assertIsNotNone(target)

	def test_every_req_command_reference_is_mapped(self) -> None:
		cmd_defs = [value for value in vars(RequirementCodeCommands).values() if isinstance(value, ReqCommandDefinition)]
		self.assertTrue(cmd_defs)
		for cmd_def in cmd_defs:
			with self.subTest(command=cmd_def.name):
				target = JumpTarget.for_req_command(cmd_def)
				if cmd_def.param_types and isinstance(cmd_def.param_types[0], REFERENCE_TYPES):
					self.assertIsNotNone(target)
				else:
					self.assertIsNone(target)

	def test_button_function_targets(self) -> None:
		self.assertEqual(JumpTarget.for_button_function(ButtonCodeCommands.Train), JumpTarget.unit_reqs)
		self.assertEqual(JumpTarget.for_button_function(ButtonCodeCommands.CanCreateOrMorph), JumpTarget.unit_reqs)
		self.assertEqual(JumpTarget.for_button_function(ButtonCodeCommands.Upgrade), JumpTarget.upgrade_reqs)
		self.assertEqual(JumpTarget.for_button_function(ButtonCodeCommands.CanResearchTech), JumpTarget.research_reqs)
		self.assertEqual(JumpTarget.for_button_function(ButtonCodeCommands.ResearchTech), JumpTarget.research_reqs)
		self.assertEqual(JumpTarget.for_button_function(ButtonCodeCommands.UseTech), JumpTarget.tech_reqs)
		self.assertEqual(JumpTarget.for_button_function(ButtonCodeCommands.CanCloak), JumpTarget.tech_reqs)
		self.assertEqual(JumpTarget.for_button_function(ButtonCodeCommands.ShowButtonCard), JumpTarget.button_cards)
		self.assertIsNone(JumpTarget.for_button_function(ButtonCodeCommands.CancelTrain))
		self.assertIsNone(JumpTarget.for_button_function(ButtonCodeCommands.Move))

	def test_req_command_targets(self) -> None:
		self.assertEqual(JumpTarget.for_req_command(RequirementCodeCommands.MustHave), JumpTarget.unit_reqs)
		self.assertEqual(JumpTarget.for_req_command(RequirementCodeCommands.HasCompleted), JumpTarget.unit_reqs)
		self.assertEqual(JumpTarget.for_req_command(RequirementCodeCommands.IsResearched), JumpTarget.research_reqs)
		self.assertIsNone(JumpTarget.for_req_command(RequirementCodeCommands.Or))

	def test_tooltip(self) -> None:
		self.assertEqual(JumpTarget.unit_reqs.tooltip, 'Jump To Unit Training Reqs.')
		self.assertEqual(JumpTarget.button_sets.tooltip, 'Jump To Button Set')
