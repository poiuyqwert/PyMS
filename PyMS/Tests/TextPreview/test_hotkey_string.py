from ...Utilities.TextPreview.HotkeyString import HotkeyString, TooltipCosts, TooltipKind
from ...Utilities.TextPreview.Layout import InlineImage
from ...Utilities.DataContext import DataContext, IconFrame, Race
from ...FileFormats.Images import Bounds

import unittest
from typing import cast

class _StubDataContext:
	# Icons as `('icon', frame)`, with the frame number as their width
	def __init__(self, missing: tuple[IconFrame, ...] = (), strings: dict[int, str] | None = None) -> None:
		self.missing = missing
		self.strings = strings or {}

	def stat_txt_raw_string(self, string_id: int) -> str | None:
		return self.strings.get(string_id)

	def get_icon(self, frame: IconFrame) -> tuple[object, Bounds] | None:
		if frame in self.missing:
			return None
		return (('icon', frame), Bounds(x_min=0, y_min=0, x_max=int(frame) + 10, y_max=12))

def _data_context(missing: tuple[IconFrame, ...] = (), strings: dict[int, str] | None = None) -> DataContext:
	return cast(DataContext, _StubDataContext(missing, strings))

def _describe(runs: list[str | InlineImage]) -> list[str | IconFrame]:
	# The text of the runs, with their icons as their frames
	return [cast(tuple[str, IconFrame], run.image)[1] if isinstance(run, InlineImage) else run for run in runs]

class Test_Parse(unittest.TestCase):
	def test_hotkey_kind_and_text(self) -> None:
		self.assertEqual(HotkeyString.parse('m\x01Train Marine'), HotkeyString('m', TooltipKind.unit, 'Train Marine'))
		self.assertEqual(HotkeyString.parse('m\x00Move'), HotkeyString('m', TooltipKind.none, 'Move'))

	def test_not_a_hotkey_string(self) -> None:
		self.assertIsNone(HotkeyString.parse('m'))
		self.assertIsNone(HotkeyString.parse('Terran Marine'))

	def test_stops_at_null(self) -> None:
		self.assertEqual(HotkeyString.parse('m\x01Train\x00Marine').text, 'Train') # type: ignore[union-attr]
		self.assertEqual(HotkeyString.parse('m\x01Train\x00Marine', stop_at_null=False).text, 'Train\x00Marine') # type: ignore[union-attr]

class Test_TooltipRuns(unittest.TestCase):
	def test_no_cost_line_without_a_cost_kind(self) -> None:
		runs = HotkeyString('m', TooltipKind.none, 'Move').tooltip_runs(TooltipCosts(minerals=50), _data_context())
		self.assertEqual(runs, ['Move'])

	def test_unit_costs(self) -> None:
		costs = TooltipCosts(minerals=150, gas=100, supply=2, race=Race.terran)
		runs = HotkeyString('m', TooltipKind.unit, 'Train Tank').tooltip_runs(costs, _data_context())
		self.assertEqual(_describe(runs), ['Train Tank', '\n\x02', IconFrame.minerals, '150 ', IconFrame.terran_gas, '100 ', IconFrame.terran_supply, '2'])

	def test_costs_of_0_are_not_shown(self) -> None:
		costs = TooltipCosts(minerals=50, gas=0, supply=1, race=Race.terran)
		runs = HotkeyString('m', TooltipKind.unit, 'Train SCV').tooltip_runs(costs, _data_context())
		self.assertEqual(_describe(runs), ['Train SCV', '\n\x02', IconFrame.minerals, '50 ', IconFrame.terran_supply, '1'])
		costs = TooltipCosts(minerals=150, gas=None, supply=0, race=Race.terran)
		runs = HotkeyString('b', TooltipKind.unit, 'Build Barracks').tooltip_runs(costs, _data_context())
		self.assertEqual(_describe(runs), ['Build Barracks', '\n\x02', IconFrame.minerals, '150'])

	def test_no_cost_line_when_every_cost_is_0(self) -> None:
		runs = HotkeyString('m', TooltipKind.unit, 'Train').tooltip_runs(TooltipCosts(minerals=0, gas=0, supply=0), _data_context())
		self.assertEqual(runs, ['Train'])
		runs = HotkeyString('t', TooltipKind.spell, 'Storm').tooltip_runs(TooltipCosts(), _data_context())
		self.assertEqual(runs, ['Storm'])

	def test_upgrade_costs(self) -> None:
		costs = TooltipCosts(minerals=100, gas=100, next_level=1)
		runs = HotkeyString('a', TooltipKind.upgrade, 'Upgrade').tooltip_runs(costs, _data_context())
		self.assertEqual(_describe(runs), ['Upgrade', '\nNext Level: 1', '\n\x02', IconFrame.minerals, '100 ', IconFrame.zerg_gas, '100'])

	def test_next_level_label_is_from_stat_txt(self) -> None:
		costs = TooltipCosts(minerals=100, next_level=2)
		runs = HotkeyString('a', TooltipKind.upgrade, 'Upgrade').tooltip_runs(costs, _data_context(strings={HotkeyString.NEXT_LEVEL_STRING: 'Niveau:\x00'}))
		self.assertEqual(runs[1], '\nNiveau: 2')

	def test_no_next_level_without_a_level(self) -> None:
		costs = TooltipCosts(minerals=100, gas=100)
		runs = HotkeyString('a', TooltipKind.upgrade, 'Upgrade').tooltip_runs(costs, _data_context())
		self.assertEqual(_describe(runs), ['Upgrade', '\n\x02', IconFrame.minerals, '100 ', IconFrame.zerg_gas, '100'])

	def test_spell_energy(self) -> None:
		runs = HotkeyString('t', TooltipKind.spell, 'Storm').tooltip_runs(TooltipCosts(energy=75, race=Race.protoss), _data_context())
		self.assertEqual(_describe(runs), ['Storm', '\n\x02', IconFrame.protoss_energy, '75'])

	def test_tech_costs(self) -> None:
		for kind in (TooltipKind.tech, TooltipKind.unit_resources):
			runs = HotkeyString('t', kind, 'Research').tooltip_runs(TooltipCosts(minerals=150, gas=50), _data_context())
			self.assertEqual(_describe(runs), ['Research', '\n\x02', IconFrame.minerals, '150 ', IconFrame.zerg_gas, '50'])

	def test_placeholder_costs_without_costs(self) -> None:
		runs = HotkeyString('m', TooltipKind.unit, 'Train').tooltip_runs(None, _data_context())
		self.assertEqual(_describe(runs)[2:], [IconFrame.minerals, '200 ', IconFrame.zerg_gas, '100 ', IconFrame.zerg_supply, '2'])

	def test_missing_icons_are_left_out(self) -> None:
		runs = HotkeyString('t', TooltipKind.spell, 'Storm').tooltip_runs(TooltipCosts(energy=75), _data_context(missing=(IconFrame.zerg_energy,)))
		self.assertEqual(runs, ['Storm', '\n\x02', '75'])

	def test_icons_advance_past_their_content(self) -> None:
		runs = HotkeyString('t', TooltipKind.spell, 'Storm').tooltip_runs(TooltipCosts(energy=75), _data_context())
		icon = runs[2]
		assert isinstance(icon, InlineImage)
		self.assertEqual((icon.width, icon.height), (IconFrame.zerg_energy + 11, 12))
