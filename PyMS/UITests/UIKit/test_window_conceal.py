
from ..harness import UITestCase

from ...Utilities import UIKit as UI
from ...Utilities.PyMSDialog import PyMSDialog


class _Host(UI.MainWindow):
	def __init__(self) -> None:
		UI.MainWindow.__init__(self)


class _GeometryDialog(PyMSDialog):
	GEOMETRY = '300x150+120+130'

	def __init__(self, parent: UI.Misc) -> None:
		self.alpha_during_setup: float | None = None
		PyMSDialog.__init__(self, parent, 'Test', grabwait=False)

	def widgetize(self) -> (UI.Misc | None):
		UI.Frame(self, width=200, height=100).pack()
		return None

	def setup_complete(self) -> None:
		# Stands in for a `WindowGeometry.load_size` call restoring a saved geometry
		self.alpha_during_setup = float(self.attributes('-alpha'))
		self.geometry(_GeometryDialog.GEOMETRY)


class _MinSizeDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc) -> None:
		PyMSDialog.__init__(self, parent, 'Test', grabwait=False, set_min_size=(True,True))

	def widgetize(self) -> (UI.Misc | None):
		UI.Frame(self, width=200, height=100).pack()
		return None


class Test_WindowConceal(UITestCase):
	def test_dialog_is_invisible_until_setup_completes_and_shows_at_final_geometry(self) -> None:
		window = self.make_window(_Host)
		dialog = _GeometryDialog(window)
		self.pump(window)
		self.assertEqual(dialog.alpha_during_setup, 0.0)
		self.assertEqual(float(dialog.attributes('-alpha')), 1.0)
		self.assertEqual(dialog.geometry(), _GeometryDialog.GEOMETRY)

	def test_min_size_matches_natural_size(self) -> None:
		window = self.make_window(_Host)
		dialog = _MinSizeDialog(window)
		self.pump(window)
		self.assertEqual(dialog.minsize(), (dialog.winfo_reqwidth(), dialog.winfo_reqheight()))

	def test_reveal_is_idempotent(self) -> None:
		window = self.make_window(_Host)
		dialog = _GeometryDialog(window)
		self.pump(window)
		dialog.reveal()
		dialog.reveal()
		self.assertEqual(float(dialog.attributes('-alpha')), 1.0)
