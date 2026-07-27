
import unittest

from ...PyTILE.Placeability import Placeability

from ...FileFormats.Tileset.Tileset import Tileset
from ...FileFormats.Tileset.CV5 import CV5Group

from ...Utilities.PyMSError import PyMSError


def _doodad_group(doodad_id: int, width: int, height: int) -> CV5Group:
	group = CV5Group()
	group.type = CV5Group.TYPE_DOODAD
	group.doodad_dddata_id = doodad_id
	group.doodad_width = width
	group.doodad_height = height
	return group

def _tileset(groups: list[CV5Group]) -> Tileset:
	tileset = Tileset()
	tileset.new_file()
	for group in groups:
		tileset.cv5.add_group(group)
	return tileset


class Test_Doodad_Layout(unittest.TestCase):
	def test_contiguous_groups_produce_layout(self) -> None:
		tileset = _tileset([_doodad_group(0, 1, 1), _doodad_group(5, 2, 2), _doodad_group(5, 2, 2)])
		self.assertEqual(Placeability.doodad_layout(tileset, 5), (1, 2, 2))

	def test_unknown_doodad_id_is_an_error(self) -> None:
		tileset = _tileset([_doodad_group(0, 1, 1)])
		with self.assertRaises(PyMSError) as cm:
			Placeability.doodad_layout(tileset, 5)
		self.assertIn('no MegaTile Groups with Doodad ID', str(cm.exception))

	def test_zero_width_is_an_error(self) -> None:
		tileset = _tileset([_doodad_group(5, 0, 1)])
		with self.assertRaises(PyMSError) as cm:
			Placeability.doodad_layout(tileset, 5)
		self.assertIn('invalid size', str(cm.exception))

	def test_oversized_dimensions_are_an_error(self) -> None:
		tileset = _tileset([_doodad_group(5, 17, 1)])
		with self.assertRaises(PyMSError) as cm:
			Placeability.doodad_layout(tileset, 5)
		self.assertIn('invalid size', str(cm.exception))

	def test_missing_rows_are_an_error(self) -> None:
		tileset = _tileset([_doodad_group(5, 2, 2)])
		with self.assertRaises(PyMSError) as cm:
			Placeability.doodad_layout(tileset, 5)
		self.assertIn('MegaTile Groups but only', str(cm.exception))

	def test_non_contiguous_rows_are_an_error(self) -> None:
		tileset = _tileset([_doodad_group(5, 2, 2), _doodad_group(7, 1, 1), _doodad_group(5, 2, 2)])
		with self.assertRaises(PyMSError) as cm:
			Placeability.doodad_layout(tileset, 5)
		self.assertIn('contiguous MegaTile Groups', str(cm.exception))

	def test_doodad_id_outside_placeability_data_is_an_error(self) -> None:
		tileset = _tileset([_doodad_group(600, 1, 1)])
		with self.assertRaises(PyMSError) as cm:
			Placeability.doodad_layout(tileset, 600)
		self.assertIn('no placeability data', str(cm.exception))
