
from ...FileFormats.TRG.Trigger import Trigger
from ...FileFormats.TRG.Condition import Condition
from ...FileFormats.TRG.Action import Action
from ...FileFormats.TRG.Constants import ConditionType, ActionType, PlayerGroup
from ...FileFormats.TRG.TRG import TRG

import io
import unittest


def _condition(condition_type: int) -> Condition:
	condition = Condition()
	condition.condition_type = condition_type
	return condition


def _action(action_type: int) -> Action:
	action = Action()
	action.action_type = action_type
	return action


class Test_capacity(unittest.TestCase):
	def test_conditions_free_starts_full(self) -> None:
		self.assertEqual(Trigger().conditions_free, Trigger.CONDITION_COUNT)

	def test_add_condition_until_full(self) -> None:
		trigger = Trigger()
		for _ in range(Trigger.CONDITION_COUNT):
			self.assertTrue(trigger.add_condition(_condition(ConditionType.always)))
		self.assertEqual(trigger.conditions_free, 0)
		self.assertFalse(trigger.add_condition(_condition(ConditionType.always)))

	def test_actions_free_starts_full(self) -> None:
		self.assertEqual(Trigger().actions_free, Trigger.ACTION_COUNT)

	def test_add_action_until_full(self) -> None:
		trigger = Trigger()
		for _ in range(Trigger.ACTION_COUNT):
			self.assertTrue(trigger.add_action(_action(ActionType.victory)))
		self.assertFalse(trigger.add_action(_action(ActionType.victory)))


class Test_pack_lifecycle(unittest.TestCase):
	def test_pre_pack_pads_to_capacity(self) -> None:
		trigger = Trigger()
		trigger.add_condition(_condition(ConditionType.always))
		trigger.add_action(_action(ActionType.victory))
		trigger.pre_pack()
		self.assertEqual(len(trigger.conditions), Trigger.CONDITION_COUNT)
		self.assertEqual(len(trigger.actions), Trigger.ACTION_COUNT)

	def test_post_pack_trims_padding(self) -> None:
		trigger = Trigger()
		trigger.add_condition(_condition(ConditionType.always))
		trigger.add_action(_action(ActionType.victory))
		trigger.pre_pack()
		trigger.post_pack()
		self.assertEqual(len(trigger.conditions), 1)
		self.assertEqual(len(trigger.actions), 1)

	def test_post_unpack_drops_empty_entries(self) -> None:
		trigger = Trigger()
		trigger.conditions = [_condition(ConditionType.always), _condition(ConditionType.no_condition)]
		trigger.actions = [_action(ActionType.victory), _action(ActionType.no_action)]
		trigger.post_unpack()
		self.assertEqual(len(trigger.conditions), 1)
		self.assertEqual(len(trigger.actions), 1)


class Test_is_missing_briefing(unittest.TestCase):
	def test_true_when_briefing_condition_present(self) -> None:
		trigger = Trigger()
		trigger.add_condition(_condition(ConditionType.is_mission_briefing))
		self.assertTrue(trigger.is_missing_briefing)

	def test_false_otherwise(self) -> None:
		trigger = Trigger()
		trigger.add_condition(_condition(ConditionType.always))
		self.assertFalse(trigger.is_missing_briefing)


class Test_decompile(unittest.TestCase):
	def _decompile(self, trigger: Trigger) -> str:
		output = io.StringIO()
		trigger.decompile(TRG(), output)
		return output.getvalue()

	def test_normal_trigger(self) -> None:
		trigger = Trigger()
		trigger.execution.player_groups[PlayerGroup.p1] = 1
		trigger.add_condition(_condition(ConditionType.always))
		trigger.add_action(_action(ActionType.victory))
		text = self._decompile(trigger)
		self.assertTrue(text.startswith('Trigger(Player 1):'))
		self.assertIn('Conditions:', text)
		self.assertIn('Always()', text)
		self.assertIn('Actions:', text)
		self.assertIn('Victory()', text)

	def test_lists_multiple_players(self) -> None:
		trigger = Trigger()
		trigger.execution.player_groups[PlayerGroup.p1] = 1
		trigger.execution.player_groups[PlayerGroup.p2] = 1
		text = self._decompile(trigger)
		self.assertTrue(text.startswith('Trigger(Player 1, Player 2):'))

	def test_empty_conditions_emit_placeholder(self) -> None:
		trigger = Trigger()
		trigger.execution.player_groups[PlayerGroup.p1] = 1
		trigger.add_action(_action(ActionType.victory))
		text = self._decompile(trigger)
		self.assertIn('NoCondition()', text)

	def test_briefing_trigger_header(self) -> None:
		trigger = Trigger()
		trigger.add_condition(_condition(ConditionType.is_mission_briefing))
		text = self._decompile(trigger)
		self.assertTrue(text.startswith('BriefingTrigger():'))
		self.assertNotIn('Conditions:', text)
