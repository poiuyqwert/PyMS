
from ..harness import UITestCase

from ...PySPK.PySPK import PySPK
from ...FileFormats import SPK
from ...FileFormats.Palette import Palette

# These tests drive PySPK through its public command methods and the stars/palette
# tab widgets, asserting on both widget state and the model. Outside-world
# boundaries — file dialogs, message boxes, the layer-count dialog, and the SPK
# parser — are stubbed per test so nothing blocks or touches disk. The harness
# already neutralizes settings I/O, analytics, the update check, and the tracer.


def make_image(width: int = 2, height: int = 2) -> SPK.SPKImage:
	image = SPK.SPKImage()
	image.width = width
	image.height = height
	image.pixels = [[1] * width for _ in range(height)]
	return image


def _star(image: SPK.SPKImage, x: int, y: int) -> SPK.SPKStar:
	star = SPK.SPKStar(image)
	star.x = x
	star.y = y
	return star


class PySPKTestCase(UITestCase):
	def open_pyspk(self) -> PySPK:
		gui = self.make_window(PySPK)
		# The star palette normally loads from an MPQ during `initialize()`; a
		# default (all black) palette keeps image rendering self-contained.
		gui.platform_wpe = Palette()
		return gui

	def with_layers_of_stars(self, layers: int = 1, stars_per_layer: int = 3) -> PySPK:
		gui = self.open_pyspk()
		gui.new()
		image = make_image()
		assert gui.spk is not None
		gui.spk.images.append(image)
		for l in range(layers):
			gui.add_layer()
			for i in range(stars_per_layer):
				gui.spk.layers[l].stars.append(_star(image, 10 * (i + 1), 10 * (i + 1)))
		gui.update_stars()
		self.pump(gui)
		return gui
