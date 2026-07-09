
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionUPRP import CHKSectionUPRP, CHKUnitProperties

import unittest


def _properties(chk) -> CHKUnitProperties:
	props = CHKUnitProperties(chk)
	props.owner = 4
	props.health = 75
	props.resources = 2000
	props.hangerUnits = 3
	return props


class Test_CHKUnitProperties(unittest.TestCase):
	def test_round_trip(self) -> None:
		chk = make_chk()
		props = _properties(chk)
		data = props.save_data()
		self.assertEqual(len(data), 20)
		reloaded = CHKUnitProperties(chk)
		reloaded.load_data(data)
		self.assertEqual(reloaded.owner, 4)
		self.assertEqual(reloaded.health, 75)
		self.assertEqual(reloaded.resources, 2000)
		self.assertEqual(reloaded.hangerUnits, 3)
		self.assertEqual(reloaded.save_data(), data)


class Test_CHKSectionUPRP(unittest.TestCase):
	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionUPRP(chk)
		section.properties = [_properties(chk), _properties(chk)]
		data = section.save_data()
		self.assertEqual(len(data), 40)
		reloaded = CHKSectionUPRP(make_chk())
		reloaded.load_data(data)
		self.assertEqual(len(reloaded.properties), 2)
		self.assertEqual(reloaded.save_data(), data)

	def test_empty_save(self) -> None:
		self.assertEqual(CHKSectionUPRP(make_chk()).save_data(), b'')

	def test_decompile(self) -> None:
		chk = make_chk()
		section = CHKSectionUPRP(chk)
		section.properties = [_properties(chk)]
		self.assertTrue(section.decompile().startswith('UPRP:'))
