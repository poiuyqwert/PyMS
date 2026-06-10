
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionCOLR import CHKSectionCOLR

import struct
import unittest


class Test_CHKSectionCOLR(unittest.TestCase):
	def test_default_colors(self) -> None:
		section = CHKSectionCOLR(make_chk())
		self.assertEqual(section.colors, CHKSectionCOLR.DEFAULT_COLORS)

	def test_init_copies_default_colors(self) -> None:
		# Mutating an instance must not affect the shared class-level defaults.
		section = CHKSectionCOLR(make_chk())
		section.colors[0] = CHKSectionCOLR.BLACK
		self.assertEqual(CHKSectionCOLR.DEFAULT_COLORS[0], CHKSectionCOLR.RED)

	def test_round_trip(self) -> None:
		chk = make_chk()
		colors = [7, 6, 5, 4, 3, 2, 1, 0]
		section = CHKSectionCOLR(chk)
		section.colors = colors
		reloaded = CHKSectionCOLR(chk)
		reloaded.load_data(section.save_data())
		self.assertEqual(reloaded.colors, colors)
		self.assertEqual(reloaded.save_data(), struct.pack('<8B', *colors))

	def test_color_name_and_palette(self) -> None:
		self.assertEqual(CHKSectionCOLR.COLOR_NAME(CHKSectionCOLR.RED), 'Red')
		self.assertEqual(CHKSectionCOLR.COLOR_NAME(99), 'Unknown')
		self.assertEqual(CHKSectionCOLR.PALETTE_INDICES(CHKSectionCOLR.WHITE), 255)

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionCOLR(make_chk()).decompile().startswith('COLR:'))
