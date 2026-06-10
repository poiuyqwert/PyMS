
from .utils import make_chk, make_chk_with_version
from ...FileFormats.CHK.Sections.CHKSectionMRGN import CHKSectionMRGN, CHKLocation
from ...FileFormats.CHK.Sections.CHKSectionVER import CHKSectionVER

import unittest


def _location(chk) -> CHKLocation:
	location = CHKLocation(chk)
	location.start = [10, 20]
	location.end = [30, 40]
	location.name = 3
	location.elevation = CHKLocation.ALL_GROUND
	return location


class Test_CHKLocation(unittest.TestCase):
	def test_round_trip(self) -> None:
		chk = make_chk()
		location = _location(chk)
		data = location.save_data()
		self.assertEqual(len(data), 20)
		reloaded = CHKLocation(chk)
		reloaded.load_data(data)
		self.assertEqual(reloaded.start, [10, 20])
		self.assertEqual(reloaded.end, [30, 40])
		self.assertEqual(reloaded.name, 3)
		self.assertEqual(reloaded.elevation, CHKLocation.ALL_GROUND)
		self.assertEqual(reloaded.save_data(), data)

	def test_in_use(self) -> None:
		chk = make_chk()
		self.assertFalse(CHKLocation(chk).in_use())
		self.assertTrue(_location(chk).in_use())

	def test_normalized_coords(self) -> None:
		chk = make_chk()
		location = CHKLocation(chk)
		location.start = [50, 60]
		location.end = [10, 20]
		self.assertEqual(location.normalized_coords(), (10, 20, 50, 60))

	def test_clear(self) -> None:
		location = _location(make_chk())
		location.clear()
		self.assertFalse(location.in_use())


class Test_CHKSectionMRGN(unittest.TestCase):
	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionMRGN(chk)
		section.locations = [_location(chk), _location(chk)]
		data = section.save_data()
		self.assertEqual(len(data), 40)
		reloaded = CHKSectionMRGN(make_chk())
		reloaded.load_data(data)
		self.assertEqual(len(reloaded.locations), 2)
		self.assertEqual(reloaded.save_data(), data)

	def test_process_data_pads_to_broodwar_count(self) -> None:
		chk = make_chk_with_version(CHKSectionVER.BW)
		section = CHKSectionMRGN(chk)
		section.load_data(b'')
		section.process_data()
		self.assertEqual(len(section.locations), 255)

	def test_process_data_pads_to_vanilla_count(self) -> None:
		chk = make_chk_with_version(CHKSectionVER.SC100)
		section = CHKSectionMRGN(chk)
		section.load_data(b'')
		section.process_data()
		self.assertEqual(len(section.locations), 64)

	def test_decompile(self) -> None:
		chk = make_chk_with_version(CHKSectionVER.BW)
		section = CHKSectionMRGN(chk)
		section.locations = [_location(chk)]
		self.assertTrue(section.decompile().startswith('MRGN:'))
