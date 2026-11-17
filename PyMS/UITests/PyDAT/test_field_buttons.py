from .utils import PyDATTestCase

from ...Utilities import UIKit as UI
from ...Utilities import Assets

class Test_PyDAT_field_buttons(PyDATTestCase):
	def test_field_buttons_have_their_own_tooltips(self) -> None:
		# The Jump To, Find Matches, and Find Icon buttons beside the fields each have a tooltip,
		# and aren't inside a frame with the field's tooltip (which would show over the button too)
		gui = self.make_pydat()
		images = {str(Assets.get_image(name)): name for name in ('jump', 'matches', 'find')}
		buttons: list[UI.Button] = []
		widgets: list[UI.Misc] = [gui]
		while widgets:
			widget = widgets.pop()
			widgets.extend(widget.winfo_children())
			if isinstance(widget, UI.Button) and str(widget.cget('image')) in images:
				buttons.append(widget)
		# 29 Jump To, 2 Find Matches, and 4 Find Icon buttons
		self.assertEqual(len(buttons), 35)
		for button in buttons:
			with self.subTest(button=str(button)):
				self.assertIsInstance(getattr(button, '_tooltip_Tooltip', None), UI.Tooltip)
				parent: UI.Misc | None = button.master
				while parent is not None:
					self.assertIsNone(getattr(parent, '_tooltip_Tooltip', None), f'{parent} has a tooltip')
					parent = parent.master
