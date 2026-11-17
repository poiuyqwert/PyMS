from .utils import PyGRAFTTestCase

from ...FileFormats.Graft import Button
from ...FileFormats.Graft.CodeHandlers import ButtonCodeCommands
from ...PyGRAFT.Tabs import ButtonSetsTab
from ...Utilities import UIKit as UI
from ...Utilities import Assets

from typing import cast

class Test_PyGRAFT_field_buttons(PyGRAFTTestCase):
	def test_field_buttons_have_their_own_tooltips(self) -> None:
		# The Jump To and Find Icon buttons beside the fields each have a tooltip,
		# and aren't inside a frame with the field's tooltip (which would show over the button too)
		gui = self.open_pygraft()
		# A button whose condition and action both have a Jump To button
		tab = cast(ButtonSetsTab, self.display_tab(gui, 'Button Sets'))
		gui.buttons_data.graft.button_sets[0].buttons = [Button(condition=ButtonCodeCommands.CanUpgrade.function_index, action=ButtonCodeCommands.Train.function_index)]
		tab.editor.builder_view.load(0, '')
		self.pump(gui)
		images = {str(Assets.get_image(name)): name for name in ('jump', 'find')}
		buttons: list[UI.Button] = []
		widgets: list[UI.Misc] = [gui]
		while widgets:
			widget = widgets.pop()
			widgets.extend(widget.winfo_children())
			if isinstance(widget, UI.Button) and str(widget.cget('image')) in images:
				buttons.append(widget)
		# At least the Button Cards' 2 Jump To buttons, the Builder's condition and action Jump To buttons, the Builder's Find Icon button,
		# and the Jump To button of the requirement opcodes with a parameter
		self.assertGreater(len(buttons), 5)
		for button in buttons:
			with self.subTest(button=str(button)):
				self.assertIsInstance(getattr(button, '_tooltip_Tooltip', None), UI.Tooltip)
				parent: UI.Misc | None = button.master
				while parent is not None:
					self.assertIsNone(getattr(parent, '_tooltip_Tooltip', None), f'{parent} has a tooltip')
					parent = parent.master
