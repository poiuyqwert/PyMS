
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionERA import CHKSectionERA

import struct
import unittest


class Test_CHKSectionERA(unittest.TestCase):
	def test_default_is_badlands(self) -> None:
		self.assertEqual(CHKSectionERA(make_chk()).tileset, CHKSectionERA.BADLANDS)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionERA(chk)
		section.tileset = CHKSectionERA.JUNGLE
		reloaded = CHKSectionERA(chk)
		reloaded.load_data(section.save_data())
		self.assertEqual(reloaded.tileset, CHKSectionERA.JUNGLE)
		self.assertEqual(reloaded.save_data(), struct.pack('<H', CHKSectionERA.JUNGLE))

	def test_tileset_name_and_file(self) -> None:
		self.assertEqual(CHKSectionERA.TILESET_NAME(CHKSectionERA.JUNGLE), 'Jungle')
		self.assertEqual(CHKSectionERA.TILESET_FILE(CHKSectionERA.JUNGLE), 'jungle')

	def test_tileset_name_wraps(self) -> None:
		# Out-of-range tilesets wrap modulo the tileset count.
		self.assertEqual(CHKSectionERA.TILESET_NAME(CHKSectionERA.TWILIGHT + 1), 'Badlands')

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionERA(make_chk()).decompile().startswith('ERA :'))
