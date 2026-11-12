
from ..harness import UITestCase

from ...Utilities import UIKit as UI
from ...Utilities import Assets

import os
from typing import Any
from unittest import mock


class _Host(UI.MainWindow):
	def __init__(self) -> None:
		UI.MainWindow.__init__(self)


def _icon_files(icons: tuple[Any, ...] | list[Any]) -> list[str]:
	return [os.path.basename(icon.cget('file')) for icon in icons]

def _expected_files(name: str) -> list[str]:
	return [f'{name}-{size}.gif' for size in (256, 128, 64, 48, 32, 16)]


class Test_LookupIcons(UITestCase):
	def test_returns_every_size_largest_first(self) -> None:
		self.make_window(_Host)
		icons = Assets.lookup_icons('PyDAT')
		self.assertEqual(_icon_files(icons), _expected_files('PyDAT'))
		self.assertEqual([(icon.width(), icon.height()) for icon in icons], [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])

	def test_unknown_name_returns_no_icons(self) -> None:
		self.make_window(_Host)
		self.assertEqual(Assets.lookup_icons('PyNotAProgram'), [])


class Test_SetIcon(UITestCase):
	def _set_icon(self, window: _Host, name: str, side_effect: Any = None) -> list[tuple[bool, list[str]]]:
		# Each call as (default, icon file names)
		with mock.patch.object(UI.MainWindow, 'wm_iconphoto', autospec=True, side_effect=side_effect) as iconphoto:
			window.set_icon(name)
		return [(call.args[1], _icon_files(call.args[2:])) for call in iconphoto.call_args_list]

	def test_applies_program_icons_as_default(self) -> None:
		window = self.make_window(_Host)
		calls = self._set_icon(window, 'PyDAT')
		self.assertEqual(calls, [(True, _expected_files('PyDAT'))])

	def test_program_without_icons_falls_back_to_pyms_icons(self) -> None:
		window = self.make_window(_Host)
		# Real Tk rejects `wm iconphoto` with no images, which triggers the fallback
		window.set_icon('PyNotAProgram')
		self.assertEqual(self.take_traced_errors(), [])
		calls = self._set_icon(window, 'PyNotAProgram', side_effect=[UI.TclError('wrong # args'), None])
		self.assertEqual(calls, [(True, []), (True, _expected_files('PyMS'))])
		self.assertEqual(self.take_traced_errors(), [])

	def test_failure_to_apply_any_icon_is_traced(self) -> None:
		window = self.make_window(_Host)
		self._set_icon(window, 'PyDAT', side_effect=UI.TclError('icon failure'))
		errors = self.take_traced_errors()
		self.assertEqual(len(errors), 1)
		self.assertIn('icon failure', errors[0])
