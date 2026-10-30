
from .utils import PySPKTestCase

from ...PySPK.PySPK import PySPK, MouseEvent, ClickModifier
from ...Utilities import UIKit as UI

from typing import Any


def _event(**attrs: Any) -> UI.Event:
	event: UI.Event = UI.Event()
	for name, value in attrs.items():
		setattr(event, name, value)
	return event


class Test_PySPK_draw_placement(PySPKTestCase):
	def with_draw_ready(self) -> PySPK:
		gui = self.with_layers_of_stars(stars_per_layer=0)
		assert gui.spk is not None
		gui.selected_image = gui.spk.images[0]
		return gui

	def test_draw_centers_star_on_cursor(self) -> None:
		gui = self.with_draw_ready()
		assert gui.spk is not None
		gui.draw_event(_event(x=50, y=60), MouseEvent.up, ClickModifier.none)
		star = gui.spk.layers[0].stars[-1]
		# 2x2 image: centering on the cursor puts the top-left half a size up-left.
		self.assertEqual((star.x, star.y), (49, 59))

	def test_draw_near_origin_clamps_star_inside_layer(self) -> None:
		gui = self.with_draw_ready()
		assert gui.spk is not None
		gui.draw_event(_event(x=0, y=0), MouseEvent.up, ClickModifier.none)
		star = gui.spk.layers[0].stars[-1]
		self.assertEqual((star.x, star.y), (0, 0))

	def test_shift_draw_places_star_by_top_left_corner(self) -> None:
		# The Shift ghost preview anchors the star's top-left corner to the
		# cursor; the placed star must land where the ghost showed it.
		gui = self.with_draw_ready()
		assert gui.spk is not None
		gui.draw_event(_event(x=50, y=60), MouseEvent.up, ClickModifier.shift)
		star = gui.spk.layers[0].stars[-1]
		self.assertEqual((star.x, star.y), (50, 60))
