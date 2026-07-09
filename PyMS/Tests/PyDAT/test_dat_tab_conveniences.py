
from ...PyDAT.DATTabConveniences import DATTabConveniences
from ...Utilities.utils import float_to_str
from ...Utilities import UIKit as UI

import unittest
from unittest.mock import Mock
from typing import cast, TYPE_CHECKING
if TYPE_CHECKING:
	from ...PyDAT.Delegates import MainDelegate


def _conv(ticks_per_second: int) -> DATTabConveniences:
	conv = DATTabConveniences()
	delegate = Mock()
	delegate.data_context.ticks_per_second = ticks_per_second
	conv.delegate = cast('MainDelegate', delegate)
	return conv


class Test_update_ticks(unittest.TestCase):
	def test_multiplies_seconds_by_ticks_per_second(self) -> None:
		var = Mock()
		_conv(24).update_ticks(2, cast(UI.IntegerVar, var))
		var.set.assert_called_once_with(48)

	def test_truncates_fractional_result(self) -> None:
		# Fractional seconds truncate toward zero via int().
		var = Mock()
		_conv(10).update_ticks(cast(int, 1.99), cast(UI.IntegerVar, var))
		var.set.assert_called_once_with(19)


class Test_update_time(unittest.TestCase):
	def test_divides_ticks_by_ticks_per_second(self) -> None:
		var = Mock()
		_conv(24).update_time(48, cast(UI.FloatVar, var))
		var.set.assert_called_once_with('2')
		self.assertIs(var.check, False)

	def test_formats_fractional_seconds(self) -> None:
		var = Mock()
		_conv(15).update_time(22, cast(UI.FloatVar, var))
		var.set.assert_called_once_with(float_to_str(22 / 15))


class Test_round_trip(unittest.TestCase):
	def test_whole_seconds_round_trip(self) -> None:
		for tps in (6, 15, 24):
			for seconds in (1, 3, 10):
				with self.subTest(tps=tps, seconds=seconds):
					ticks_var = Mock()
					_conv(tps).update_ticks(seconds, cast(UI.IntegerVar, ticks_var))
					ticks = ticks_var.set.call_args.args[0]
					time_var = Mock()
					_conv(tps).update_time(ticks, cast(UI.FloatVar, time_var))
					self.assertEqual(time_var.set.call_args.args[0], str(seconds))
