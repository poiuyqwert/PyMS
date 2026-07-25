
from __future__ import annotations

from ...Utilities import Config
from ...Utilities import UIKit as UI
from ...Utilities.UIKit.Widgets.Extensions import WindowExtensions

import unittest
from typing import cast, overload


class StubWindow(WindowExtensions):
	"""A window stand-in implementing everything `WindowGeometry` touches, without a Tk root.

	While maximized, `geometry()` reports the zoomed size at the pre-maximize position (matching
	Tk on Windows); the true restored geometry is only reported after `wm_state('normal')`.
	"""

	def __init__(self, *,
		geometry: str = '800x600+150+120',
		restored_geometry: str | None = None,
		resizable: tuple[bool, bool] = (True, True),
		min_size: tuple[int, int] = (1, 1),
		screen_size: tuple[int, int] = (1366, 768),
		vroot: tuple[int, int, int, int] = (0, 0, 1366, 768),
		maximized: bool = False
	) -> None:
		# Deliberately no `super().__init__()` — no Tk methods are ever reached
		self._geometry = geometry
		self._restored_geometry = restored_geometry
		self._resizable = resizable
		self._min_size = min_size
		self._screen_size = screen_size
		self._vroot = vroot
		self._maximized = maximized
		self.applied_geometries: list[str] = []
		self.wm_state_calls: list[str] = []

	@overload
	def resizable(self, width: None = None, height: None = None) -> tuple[bool, bool]: ...
	@overload
	def resizable(self, width: bool, height: bool) -> None: ...
	def resizable(self, width: bool | None = None, height: bool | None = None) -> tuple[bool, bool] | None:
		if width is None or height is None:
			return self._resizable
		self._resizable = (width, height)
		return None

	@overload
	def minsize(self, width: None = None, height: None = None) -> tuple[int, int]: ...
	@overload
	def minsize(self, width: int, height: int) -> None: ...
	def minsize(self, width: int | None = None, height: int | None = None) -> tuple[int, int] | None:
		if width is None or height is None:
			return self._min_size
		self._min_size = (width, height)
		return None

	@overload
	def geometry(self, newGeometry: None = None) -> str: ...
	@overload
	def geometry(self, newGeometry: str) -> None: ...
	def geometry(self, newGeometry: str | None = None) -> str | None:
		if newGeometry is None:
			return self._geometry
		self.applied_geometries.append(newGeometry)
		if UI.Geometry.parse(newGeometry) is not None:
			self._geometry = newGeometry
		elif (adjust := UI.GeometryAdjust.parse(newGeometry)) and adjust.pos is not None:
			current = UI.Geometry.parse(self._geometry)
			assert current is not None
			current.pos = adjust.pos
			self._geometry = current.text
		return None

	@overload
	def wm_state(self, newstate: None = None) -> str: ...
	@overload
	def wm_state(self, newstate: str = ...) -> None: ...
	def wm_state(self, newstate: str | None = None) -> str | None:
		if newstate is None:
			return 'zoomed' if self._maximized else 'normal'
		self.wm_state_calls.append(newstate)
		if newstate == 'normal' and self._maximized:
			self._maximized = False
			if self._restored_geometry is not None:
				self._geometry = self._restored_geometry
		elif newstate == 'zoomed':
			self._maximized = True
		return None

	def is_maximized(self) -> bool:
		return self._maximized

	def update_idletasks(self) -> None:
		pass

	def winfo_screenwidth(self) -> int:
		return self._screen_size[0]

	def winfo_screenheight(self) -> int:
		return self._screen_size[1]

	def winfo_vrootx(self) -> int:
		return self._vroot[0]

	def winfo_vrooty(self) -> int:
		return self._vroot[1]

	def winfo_vrootwidth(self) -> int:
		return self._vroot[2]

	def winfo_vrootheight(self) -> int:
		return self._vroot[3]


DUAL_MONITOR_VROOT = (-1920, 0, 3286, 1080)


def as_window(stub: StubWindow) -> UI.AnyWindow:
	return cast(UI.AnyWindow, stub)


class Test_WindowGeometry_decode(unittest.TestCase):
	def test_accepts_full_geometry(self) -> None:
		obj = Config.WindowGeometry()
		obj.decode('800x600+150+120')
		self.assertEqual(obj.encode(), '800x600+150+120')

	def test_accepts_maximized_suffix(self) -> None:
		obj = Config.WindowGeometry()
		obj.decode('800x600+150+120^')
		self.assertEqual(obj.encode(), '800x600+150+120^')

	def test_accepts_position_only(self) -> None:
		obj = Config.WindowGeometry()
		obj.decode('+150+120')
		self.assertEqual(obj.encode(), '+150+120')

	def test_rejects_garbage(self) -> None:
		obj = Config.WindowGeometry()
		obj.decode('garbage')
		self.assertIsNone(obj.encode())

	def test_rejects_non_string(self) -> None:
		obj = Config.WindowGeometry()
		obj.decode(42)
		self.assertIsNone(obj.encode())


class Test_WindowGeometry_save_size(unittest.TestCase):
	def test_stores_geometry(self) -> None:
		stub = StubWindow(geometry='800x600+150+120')
		obj = Config.WindowGeometry()
		obj.save_size(as_window(stub))
		self.assertEqual(obj.encode(), '800x600+150+120')
		self.assertEqual(stub.wm_state_calls, [])

	def test_maximized_stores_restored_geometry_with_flag(self) -> None:
		stub = StubWindow(geometry='1366x709+150+120', restored_geometry='800x600+150+120', maximized=True)
		obj = Config.WindowGeometry()
		obj.save_size(as_window(stub))
		self.assertEqual(obj.encode(), '800x600+150+120^')
		self.assertEqual(stub.wm_state_calls, ['normal'])

	def test_non_resizable_stores_position_only(self) -> None:
		stub = StubWindow(geometry='800x600+150+120', resizable=(False, False))
		obj = Config.WindowGeometry()
		obj.save_size(as_window(stub))
		self.assertEqual(obj.encode(), '+150+120')


class Test_WindowGeometry_load_size(unittest.TestCase):
	def test_maximized_value_not_passed_to_tk(self) -> None:
		stub = StubWindow()
		obj = Config.WindowGeometry()
		obj.decode('800x600+150+120^')
		obj.load_size(as_window(stub))
		for applied in stub.applied_geometries:
			self.assertNotIn('^', applied)
		self.assertIn('zoomed', stub.wm_state_calls)

	def test_maximized_value_single_axis_resizable_does_not_zoom(self) -> None:
		stub = StubWindow(resizable=(True, False))
		obj = Config.WindowGeometry()
		obj.decode('800x600+150+120^')
		obj.load_size(as_window(stub))
		for applied in stub.applied_geometries:
			self.assertNotIn('^', applied)
		self.assertNotIn('zoomed', stub.wm_state_calls)

	def test_maximized_value_non_resizable_applies_position_only(self) -> None:
		stub = StubWindow(resizable=(False, False))
		obj = Config.WindowGeometry()
		obj.decode('800x600+150+120^')
		obj.load_size(as_window(stub))
		self.assertEqual(stub.applied_geometries, ['+150+120'])
		self.assertNotIn('zoomed', stub.wm_state_calls)

	def test_preserves_position_on_other_monitor(self) -> None:
		stub = StubWindow(vroot=DUAL_MONITOR_VROOT)
		obj = Config.WindowGeometry()
		obj.decode('800x600+-1900+50')
		obj.load_size(as_window(stub))
		self.assertEqual(stub.applied_geometries, ['800x600+-1900+50'])

	def test_keeps_size_larger_than_primary_within_desktop(self) -> None:
		stub = StubWindow(vroot=DUAL_MONITOR_VROOT)
		obj = Config.WindowGeometry()
		obj.decode('1000x1000+-1500+10')
		obj.load_size(as_window(stub))
		self.assertEqual(stub.applied_geometries, ['1000x1000+-1500+10'])

	def test_keeps_size_at_saved_position(self) -> None:
		stub = StubWindow()
		obj = Config.WindowGeometry()
		obj.decode('1366x709+150+120')
		obj.load_size(as_window(stub))
		self.assertEqual(stub.applied_geometries, ['1366x709+150+120'])

	def test_position_on_detached_monitor_restored_fully_visible(self) -> None:
		# Saved while a second monitor was attached to the left; loaded with only the primary
		stub = StubWindow()
		obj = Config.WindowGeometry()
		obj.decode('640x480+-1870+50')
		obj.load_size(as_window(stub))
		self.assertEqual(stub.applied_geometries, ['640x480+0+50'])

	def test_position_past_desktop_edge_restored_fully_visible(self) -> None:
		stub = StubWindow()
		obj = Config.WindowGeometry()
		obj.decode('800x600+5000+50')
		obj.load_size(as_window(stub))
		self.assertEqual(stub.applied_geometries, ['800x600+566+50'])

	def test_position_only_applies_position(self) -> None:
		stub = StubWindow(resizable=(False, False))
		obj = Config.WindowGeometry()
		obj.decode('+250+260')
		obj.load_size(as_window(stub))
		self.assertEqual(stub.applied_geometries, ['+250+260'])

	def test_without_saved_geometry_centers_default_size(self) -> None:
		stub = StubWindow()
		obj = Config.WindowGeometry(default_size=UI.Size(550, 430))
		obj.load_size(as_window(stub))
		self.assertEqual(stub.applied_geometries, ['550x430+408+169'])
