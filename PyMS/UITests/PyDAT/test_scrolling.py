
from .utils import PyDATTestCase

from ...PyDAT.PyDAT import PyDAT
from ...PyDAT.Tabs.UnitTabs.AIActionsUnitsTab import AIActionsUnitsTab
from ...Utilities import UIKit as UI

from unittest import mock

from typing import cast


class Test_PyDAT_scrolling(PyDATTestCase):
	def setUp(self) -> None:
		super().setUp()
		# `_wheel` moves the clock past the latch time, so each wheel event starts a new gesture
		self.now = 0.0
		patcher = mock.patch('PyMS.Utilities.UIKit.MouseWheel.monotonic', side_effect=lambda: self.now)
		patcher.start()
		self.addCleanup(patcher.stop)

	def _units_subtab(self, gui: PyDAT, name: str) -> UI.Misc:
		units_tab = gui.dattabs.active
		assert units_tab is not None
		subtab = cast(UI.Notebook, getattr(units_tab, 'dattabs')).display(name)
		self.pump(gui)
		return subtab

	def _scroll_view(self, widget: UI.Misc) -> UI.ScrollView:
		view: UI.Misc | None = widget
		while view is not None and not isinstance(view, UI.ScrollView):
			view = view.master
		assert view is not None
		return view

	def _canvas(self, view: UI.ScrollView | UI.FlowView) -> UI.Canvas:
		# The canvas scrolling the view's content
		return next(child for child in view.winfo_children() if isinstance(child, UI.Canvas))

	def _wheel(self, widget: UI.Misc, delta: int) -> None:
		self.now += 1
		widget.event_generate(UI.Mouse.Scroll(), delta=delta)
		self.pump(widget)

	def _ai_actions(self) -> tuple[PyDAT, AIActionsUnitsTab, UI.ScrollView]:
		# The force values need the weapons DAT, which these tests don't load; the text is filled in directly instead
		patcher = mock.patch.object(AIActionsUnitsTab, 'build_force_values')
		patcher.start()
		self.addCleanup(patcher.stop)
		gui = self.with_new_dat('Units')
		gui.geometry('800x400')
		self.pump(gui)
		ai_tab = cast(AIActionsUnitsTab, self._units_subtab(gui, 'AI Actions'))
		text = ai_tab.force_value_text
		text.config(state=UI.NORMAL)
		text.insert('1.0', '\n'.join(f'line {n}' for n in range(100)))
		text.config(state=UI.DISABLED)
		self.pump(gui)
		return (gui, ai_tab, self._scroll_view(text))

	def test_wheel_over_force_values_scrolls_only_the_text(self) -> None:
		_, ai_tab, scroll_view = self._ai_actions()
		self._wheel(ai_tab.force_value_text, -120)
		self.assertGreater(ai_tab.force_value_text.yview()[0], 0)
		self.assertEqual(self._canvas(scroll_view).yview()[0], 0)

	def test_wheel_over_force_values_at_its_end_scrolls_the_page(self) -> None:
		_, ai_tab, scroll_view = self._ai_actions()
		ai_tab.force_value_text.yview_moveto(1)
		self.pump(ai_tab)
		self._wheel(ai_tab.force_value_text, -120)
		self.assertGreater(self._canvas(scroll_view).yview()[0], 0)

	def test_tab_shown_again_still_scrolls(self) -> None:
		gui, ai_tab, scroll_view = self._ai_actions()
		self._units_subtab(gui, 'Basic')
		self._units_subtab(gui, 'AI Actions')
		label_frame = scroll_view.content_view.winfo_children()[0]
		self._wheel(label_frame, -120)
		self.assertGreater(self._canvas(scroll_view).yview()[0], 0)
		self.assertEqual(ai_tab.force_value_text.yview()[0], 0)
