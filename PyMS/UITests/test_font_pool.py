
from unittest import mock

from .harness import UITestCase

from ..Utilities import UIKit as UI

import tkinter.font as _Fonts

from typing import Any


class TestFontPool(UITestCase):
	# Fonts are interned by their resolved Tcl name: constructing an equivalent font
	# returns the same instance, so the underlying named font is created and
	# configured exactly once and shared. Re-creating an equivalent font would
	# re-apply its spec to the shared named font, invalidating Tk's font metrics and
	# forcing a slow re-resolution. Interning is what keeps a tab full of
	# `Font.default().bolded()` labels cheap to lay out.

	def test_equivalent_fonts_are_the_same_instance(self) -> None:
		self.make_window(UI.MainWindow)
		self.assertIs(UI.Font.default(), UI.Font.default())
		self.assertIs(UI.Font.default().bolded(), UI.Font.default().bolded())
		self.assertIs(
			UI.Font(family='Helvetica', size=10, bold=True),
			UI.Font(family='Helvetica', size=10, bold=True),
		)

	def test_distinct_fonts_are_not_interned(self) -> None:
		self.make_window(UI.MainWindow)
		self.assertIsNot(UI.Font.default(), UI.Font.default().bolded())
		self.assertIsNot(
			UI.Font(family='Helvetica', size=10),
			UI.Font(family='Helvetica', size=12),
		)

	def test_equivalent_font_initializes_the_tcl_font_only_once(self) -> None:
		self.make_window(UI.MainWindow)
		# The harness clears the pool before each test, so the first construction is
		# the one that creates the Tcl font and the second must reuse it.
		calls = []
		original_init = _Fonts.Font.__init__
		def counting_init(self: _Fonts.Font, *args: Any, **kwargs: Any) -> None:
			calls.append(1)
			original_init(self, *args, **kwargs)
		with mock.patch.object(_Fonts.Font, '__init__', counting_init):
			first = UI.Font(family='Courier', size=9, bold=True)
			second = UI.Font(family='Courier', size=9, bold=True)
		self.assertIs(first, second)
		self.assertEqual(len(calls), 1)
