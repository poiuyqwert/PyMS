
from ...PyBIN.WidgetSettings import WidgetSettings
from ...FileFormats.DialogBIN import BINWidget
from ...Utilities import UIKit as UI
from ...Utilities.utils import pack_flags

import unittest
from unittest.mock import Mock
from typing import cast


def _var(value: int = 0) -> UI.IntegerVar:
	var = Mock()
	var.get.return_value = value
	return cast(UI.IntegerVar, var)


def _settings(show_advanced: bool) -> WidgetSettings:
	settings = Mock()
	settings.show_advanced.get.return_value = show_advanced
	return cast(WidgetSettings, settings)


def _widget_flags() -> list[int]:
	return [v for k, v in vars(BINWidget).items() if k.startswith('FLAG_')]


class Test_calculate(unittest.TestCase):
	def test_basic_arithmetic(self) -> None:
		calc = _var()
		WidgetSettings.calculate(_settings(show_advanced=False), calc, _var(100), _var(5), 1, fix=2)
		cast(Mock, calc).set.assert_called_once_with(107)

	def test_negative_direction(self) -> None:
		calc = _var()
		WidgetSettings.calculate(_settings(show_advanced=False), calc, _var(100), _var(5), -1, fix=0)
		cast(Mock, calc).set.assert_called_once_with(95)

	def test_advanced_shown_allowed(self) -> None:
		calc = _var()
		WidgetSettings.calculate(_settings(show_advanced=True), calc, _var(10), _var(3), 1, fix=0, allow_advanced=True)
		cast(Mock, calc).set.assert_called_once_with(13)

	def test_advanced_shown_disallowed_skips(self) -> None:
		calc = _var()
		WidgetSettings.calculate(_settings(show_advanced=True), calc, _var(10), _var(3), 1, fix=0, allow_advanced=False)
		cast(Mock, calc).set.assert_not_called()


class Test_flag_packing(unittest.TestCase):
	def test_flag_constants_are_distinct_single_bits(self) -> None:
		flags = _widget_flags()
		self.assertEqual(len(flags), len(set(flags)))
		for flag in flags:
			with self.subTest(flag=flag):
				self.assertNotEqual(flag, 0)
				self.assertEqual(flag & (flag - 1), 0)

	def test_pack_flags_round_trip_over_all_bits(self) -> None:
		flags = _widget_flags()
		original = 0
		for flag in flags:
			original |= flag
		packed = pack_flags([(1 if original & flag else 0, flag) for flag in flags])
		self.assertEqual(packed, original)

	def test_pack_flags_subset(self) -> None:
		packed = pack_flags([
			(1, BINWidget.FLAG_VISIBLE),
			(0, BINWidget.FLAG_DISABLED),
			(1, BINWidget.FLAG_RESPONSIVE),
		])
		self.assertEqual(packed, BINWidget.FLAG_VISIBLE | BINWidget.FLAG_RESPONSIVE)
