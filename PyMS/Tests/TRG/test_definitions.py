
from ...FileFormats.TRG import Conditions, Actions
from ...FileFormats.TRG.Condition import Condition
from ...FileFormats.TRG.Action import Action
from ...FileFormats.TRG.Constants import ConditionType, ActionType, PlayerGroup, Mask, Matches

import unittest


class Test_Conditions_get_definition(unittest.TestCase):
	def test_basic_by_condition_type(self) -> None:
		condition = Condition()
		condition.condition_type = ConditionType.always
		self.assertEqual(Conditions.get_definition(condition).name, 'Always')

	def test_deaths_resolves_to_basic_by_default(self) -> None:
		condition = Condition()
		condition.condition_type = ConditionType.deaths
		self.assertEqual(Conditions.get_definition(condition).name, 'Deaths')

	def test_high_player_resolves_to_memory(self) -> None:
		# Memory definition out-scores the basic one when the player group is out of range.
		condition = Condition()
		condition.condition_type = ConditionType.deaths
		condition.player_group = PlayerGroup.non_allied_victory_players + 1
		self.assertEqual(Conditions.get_definition(condition).name, 'Memory')

	def test_masked_resolves_to_memory(self) -> None:
		condition = Condition()
		condition.condition_type = ConditionType.deaths
		condition.masked = Mask.enabled
		self.assertEqual(Conditions.get_definition(condition).name, 'Memory')

	def test_unknown_type_falls_back_to_raw(self) -> None:
		condition = Condition()
		condition.condition_type = 250
		self.assertEqual(Conditions.get_definition(condition).name, 'RawCondition')


class Test_Conditions_get_definition_named(unittest.TestCase):
	def test_found(self) -> None:
		definition = Conditions.get_definition_named('Always')
		assert definition is not None
		self.assertEqual(definition.name, 'Always')

	def test_not_found(self) -> None:
		self.assertIsNone(Conditions.get_definition_named('Nonexistent'))


class Test_Actions_get_definition(unittest.TestCase):
	def test_basic_by_action_type(self) -> None:
		action = Action()
		action.action_type = ActionType.victory
		self.assertEqual(Actions.get_definition(action).name, 'Victory')

	def test_set_deaths_resolves_to_basic_by_default(self) -> None:
		action = Action()
		action.action_type = ActionType.set_deaths
		self.assertEqual(Actions.get_definition(action).name, 'SetDeaths')

	def test_high_player_resolves_to_set_memory(self) -> None:
		action = Action()
		action.action_type = ActionType.set_deaths
		action.player_group = PlayerGroup.non_allied_victory_players + 1
		self.assertEqual(Actions.get_definition(action).name, 'SetMemory')

	def test_unknown_type_falls_back_to_raw(self) -> None:
		action = Action()
		action.action_type = 250
		self.assertEqual(Actions.get_definition(action).name, 'RawAction')


class Test_Actions_get_definition_named(unittest.TestCase):
	def test_found(self) -> None:
		definition = Actions.get_definition_named('Victory')
		assert definition is not None
		self.assertEqual(definition.name, 'Victory')

	def test_not_found(self) -> None:
		self.assertIsNone(Actions.get_definition_named('Nonexistent'))


class Test_matches_scoring(unittest.TestCase):
	def test_basic_matches_on_type(self) -> None:
		definition = Actions.get_definition_named('Victory')
		assert definition is not None
		action = Action()
		action.action_type = ActionType.victory
		self.assertEqual(definition.matches(action), Matches.low)

	def test_basic_no_match_on_other_type(self) -> None:
		definition = Actions.get_definition_named('Victory')
		assert definition is not None
		action = Action()
		action.action_type = ActionType.defeat
		self.assertEqual(definition.matches(action), Matches.no)

	def test_memory_outscores_basic(self) -> None:
		basic = Actions.get_definition_named('SetDeaths')
		memory = Actions.get_definition_named('SetMemory')
		assert basic is not None and memory is not None
		action = Action()
		action.action_type = ActionType.set_deaths
		action.masked = Mask.enabled
		self.assertGreater(memory.matches(action), basic.matches(action))

	def test_raw_always_matches_low(self) -> None:
		definition = Actions.get_definition_named('RawAction')
		assert definition is not None
		self.assertEqual(definition.matches(Action()), 1)


class Test_definition_help(unittest.TestCase):
	def test_help_lists_parameters_and_description(self) -> None:
		definition = Actions.get_definition_named('DisplayTextMessage')
		assert definition is not None
		help_text = definition.help()
		self.assertTrue(help_text.startswith('DisplayTextMessage(String, Display)'))
		self.assertIn('Display `String` for current player when `Display`.', help_text)
		self.assertIn('String:', help_text)
		self.assertIn('Display:', help_text)

	def test_help_numbers_duplicate_parameter_types(self) -> None:
		# Transmission has two Time parameters, so they are numbered Time(1)/Time(2).
		definition = Actions.get_definition_named('Transmission')
		assert definition is not None
		help_text = definition.help()
		self.assertIn('Time(1)', help_text)
		self.assertIn('Time(2)', help_text)

	def test_help_for_parameterless_action(self) -> None:
		definition = Actions.get_definition_named('Victory')
		assert definition is not None
		self.assertEqual(definition.help(), 'Victory()\n    End scenario in victory for current player.')

	def test_help_substitutes_single_parameter(self) -> None:
		definition = Actions.get_definition_named('Wait')
		assert definition is not None
		help_text = definition.help()
		self.assertTrue(help_text.startswith('Wait(Time)'))
		self.assertIn('Wait for `Time` milliseconds.', help_text)


class Test_description_placeholders(unittest.TestCase):
	# Every parameter index should be referenced by a `{n}` placeholder, and no
	# placeholder should point past the parameter list (the Raw* definitions use a
	# generic description with no placeholders and are exempt).
	def _check(self, registry: list) -> None:
		import re as _re
		for definition in registry:
			if not definition.parameters or not _re.search(r'\{\d+\}', definition.description):
				continue
			refs = set(int(m) for m in _re.findall(r'\{(\d+)\}', definition.description))
			expected = set(range(len(definition.parameters)))
			with self.subTest(definition=definition.name):
				self.assertEqual(refs, expected)

	def test_conditions(self) -> None:
		self._check(Conditions.definitions_registry)

	def test_actions(self) -> None:
		self._check(Actions.definitions_registry)
