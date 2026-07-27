
from unittest import mock

from typing import cast

from ..harness import UITestCase

from ...FileFormats import DialogBIN
from ...PyBIN.Config import PyBINConfig
from ...PyBIN.WidgetNode import WidgetNode
from ...PyBIN import WidgetSettings as widget_settings_module
from ...PyBIN.WidgetSettings import WidgetSettings

from ...Utilities import UIKit as UI
from ...Utilities.MPQHandler import MPQHandler


class _Delegate:
	def __init__(self) -> None:
		self.config = PyBINConfig()

	def get_bin(self) -> (DialogBIN.DialogBIN | None):
		return None

	def get_config(self) -> PyBINConfig:
		return self.config

	def get_mpqhandler(self) -> MPQHandler:
		raise AssertionError('MPQHandler is not used by these tests')

	def get_scr_enabled(self) -> bool:
		return False

	def mark_edited(self) -> None:
		pass

	def refresh_preview(self) -> None:
		pass

	def refresh_smks(self) -> None:
		pass

	def refresh_nodes(self) -> None:
		pass


class Test_WidgetSettings_Bounds(UITestCase):
	# In simple (non-Advanced) mode the Right/Bottom fields are hidden and
	# derived: editing Left/Width recalculates Right (right = left + width - 1),
	# and editing Top/Height recalculates Bottom (bottom = top + height - 1).
	# Each axis derives only its own field — a vertical edit must never touch
	# the horizontal fields, and vice versa.

	def make_dialog(self) -> WidgetSettings:
		window = self.make_window(UI.MainWindow)
		widget = DialogBIN.BINWidget(DialogBIN.BINWidget.TYPE_BUTTON)
		widget.x1 = 10
		widget.y1 = 20
		widget.width = 100
		widget.height = 40
		widget.x2 = 109
		widget.y2 = 59
		widget.responsive_x1 = 1
		widget.responsive_y1 = 2
		widget.responsive_width = 8
		widget.responsive_height = 10
		widget.responsive_x2 = 8
		widget.responsive_y2 = 11
		node = WidgetNode(mock.Mock(), widget)
		# `grab_wait` blocks on `wait_window` until the dialog closes; neutralize it
		# so construction returns and the test can drive the live dialog.
		with mock.patch.object(UI.WindowExtensions, 'grab_wait', lambda self: None):
			dialog = WidgetSettings(window, node, _Delegate())
		self.addCleanup(self._destroy, dialog)
		self.pump(dialog)
		return dialog

	def test_simple_mode_is_the_default(self) -> None:
		dialog = self.make_dialog()
		self.assertFalse(dialog.show_advanced.get())
		self.assertFalse(dialog.advanced_shown)

	def test_loading_derives_right_and_bottom_from_position_and_size(self) -> None:
		dialog = self.make_dialog()
		self.assertEqual(dialog.right.get(), 109)
		self.assertEqual(dialog.bottom.get(), 59)

	def test_editing_left_or_width_derives_right(self) -> None:
		dialog = self.make_dialog()
		dialog.left.set(30)
		self.assertEqual(dialog.right.get(), 129)
		dialog.width.set(50)
		self.assertEqual(dialog.right.get(), 79)
		# The vertical fields belong to the other axis and stay untouched.
		self.assertEqual(dialog.top.get(), 20)
		self.assertEqual(dialog.bottom.get(), 59)
		self.assertEqual(dialog.height.get(), 40)

	def test_editing_top_or_height_derives_bottom(self) -> None:
		dialog = self.make_dialog()
		dialog.top.set(35)
		self.assertEqual(dialog.bottom.get(), 74)
		dialog.height.set(20)
		self.assertEqual(dialog.bottom.get(), 54)
		# The horizontal fields belong to the other axis and stay untouched.
		self.assertEqual(dialog.left.get(), 10)
		self.assertEqual(dialog.right.get(), 109)
		self.assertEqual(dialog.width.get(), 100)

	def test_editing_responsive_top_or_height_derives_responsive_bottom(self) -> None:
		dialog = self.make_dialog()
		dialog.responsive_top.set(5)
		self.assertEqual(dialog.responsive_bottom.get(), 14)
		dialog.responsive_height.set(20)
		self.assertEqual(dialog.responsive_bottom.get(), 24)
		# The horizontal fields belong to the other axis and stay untouched.
		self.assertEqual(dialog.responsive_left.get(), 1)
		self.assertEqual(dialog.responsive_right.get(), 8)
		self.assertEqual(dialog.responsive_width.get(), 8)

	def test_editing_responsive_left_or_width_derives_responsive_right(self) -> None:
		dialog = self.make_dialog()
		dialog.responsive_left.set(3)
		self.assertEqual(dialog.responsive_right.get(), 10)
		dialog.responsive_width.set(6)
		self.assertEqual(dialog.responsive_right.get(), 8)
		# The vertical fields belong to the other axis and stay untouched.
		self.assertEqual(dialog.responsive_top.get(), 2)
		self.assertEqual(dialog.responsive_bottom.get(), 11)
		self.assertEqual(dialog.responsive_height.get(), 10)

	def test_advanced_mode_leaves_all_fields_independent(self) -> None:
		dialog = self.make_dialog()
		dialog.show_advanced.set(True)
		dialog.top.set(35)
		dialog.height.set(20)
		dialog.left.set(30)
		dialog.width.set(50)
		self.assertEqual(dialog.bottom.get(), 59)
		self.assertEqual(dialog.right.get(), 109)


class _FindImageDelegate(_Delegate):
	def get_mpqhandler(self) -> MPQHandler:
		return cast(MPQHandler, mock.Mock(spec=MPQHandler))


class Test_WidgetSettings_FindImage(UITestCase):
	# The browse button beside the string field opens an MPQ browser for a PCX
	# image: selecting a file places its MPQ path into the string field, while
	# cancelling the browse leaves the field untouched.

	def make_dialog(self) -> WidgetSettings:
		window = self.make_window(UI.MainWindow)
		widget = DialogBIN.BINWidget(DialogBIN.BINWidget.TYPE_IMAGE)
		node = WidgetNode(mock.Mock(), widget)
		# `grab_wait` blocks on `wait_window` until the dialog closes; neutralize it
		# so construction returns and the test can drive the live dialog.
		with mock.patch.object(UI.WindowExtensions, 'grab_wait', lambda self: None):
			dialog = WidgetSettings(window, node, _FindImageDelegate())
		self.addCleanup(self._destroy, dialog)
		self.pump(dialog)
		return dialog

	def test_selected_image_path_replaces_string(self) -> None:
		dialog = self.make_dialog()
		dialog.string.set('old\\path.pcx')
		with mock.patch.object(widget_settings_module, 'MPQSelect') as select:
			select.return_value.file = 'MPQ:glue\\title\\title.pcx'
			dialog.find_image()
		self.assertEqual(dialog.string.get(), 'glue\\title\\title.pcx')

	def test_browse_uses_widget_image_configs(self) -> None:
		dialog = self.make_dialog()
		config = dialog.delegate.get_config()
		with mock.patch.object(widget_settings_module, 'MPQSelect') as select:
			select.return_value.file = None
			dialog.find_image()
		self.assertIs(select.call_args.kwargs['history_config'], config.edit.widget.mpq_select_history)
		self.assertIs(select.call_args.kwargs['window_geometry_config'], config.windows.edit.widget.mpq_select)

	def test_cancelled_browse_keeps_string(self) -> None:
		dialog = self.make_dialog()
		dialog.string.set('old\\path.pcx')
		with mock.patch.object(widget_settings_module, 'MPQSelect') as select:
			select.return_value.file = None
			dialog.find_image()
		self.assertEqual(dialog.string.get(), 'old\\path.pcx')
