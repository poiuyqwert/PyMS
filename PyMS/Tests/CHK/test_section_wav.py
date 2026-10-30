
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionWAV import CHKSectionWAV

import unittest


class Test_CHKSectionWAV(unittest.TestCase):
	def test_default_paths(self) -> None:
		self.assertEqual(CHKSectionWAV(make_chk()).paths, [0] * 512)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionWAV(chk)
		section.paths[0] = 12
		section.paths[511] = 34
		reloaded = CHKSectionWAV(chk)
		data = section.save_data()
		self.assertEqual(len(data), 2048)
		reloaded.load_data(data)
		self.assertEqual(reloaded.paths[0], 12)
		self.assertEqual(reloaded.paths[511], 34)
		self.assertEqual(reloaded.save_data(), data)

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionWAV(make_chk()).decompile().startswith('WAV :'))
