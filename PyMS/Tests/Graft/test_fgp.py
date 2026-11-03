from .utils import button_bytes, fgp_chunk, fgp_file
from ...FileFormats.Graft import FGP, FGPUnit, Button, StatInfo, UnitsGraft, UpgradesGraft, ParamKind
from ...Utilities.PyMSError import PyMSError

import struct
import unittest

MOVE = button_bytes(1, 228, 3, 9, enabled_string=664)
STOP = button_bytes(2, 229, 3, 10, enabled_string=665)

def _button_sets(*sets: tuple[int, list[bytes]]) -> bytes:
	data = struct.pack('<H', len(sets))
	for set_id, buttons in sets:
		data += struct.pack('<BB', set_id, len(buttons)) + b''.join(buttons)
	return fgp_chunk(b'Buts', data)

def _units(*units: tuple[int, int, int, tuple[int, int, int] | None]) -> bytes:
	data = struct.pack('<H', len(units))
	for unit_id, set_id, connected_unit, stat_info in units:
		data += struct.pack('<BBBHB', unit_id, 0, set_id, connected_unit, stat_info is not None)
		if stat_info is not None:
			data += struct.pack('<BBB', *stat_info)
	return fgp_chunk(b'Unit', data)

def _requirements(tag: bytes, *scripts: tuple[int, list[int], bool]) -> bytes:
	data = struct.pack('<H', len(scripts))
	for entry_id, words, used in scripts:
		data += struct.pack(f'<BB{len(words)}HB', entry_id, len(words), *words, used)
	return fgp_chunk(tag, data)

def _names(*nodes: tuple[int, bool, str]) -> bytes:
	data = struct.pack('<I', len(nodes))
	for entry_id, is_folder, name in nodes:
		data += struct.pack('<iBI', entry_id, is_folder, 0) + name.encode('latin-1') + b'\x00'
	return fgp_chunk(b'SUni', data)

class Test_Load(unittest.TestCase):
	def test_reads_chunks(self) -> None:
		data = fgp_file(
			fgp_chunk(b'XtRa', b'ignored'),
			_button_sets((0, [MOVE, STOP]), (5, [])),
			_units((0, 1, 0xFFFF, (0, 1, 0)), (1, 0, 3, None)),
			_requirements(b'UntR', (0, [0xFF05, 0xFFFF], True), (1, [0xFFFF], False)),
			_requirements(b'UpgR', (2, [0xFF1F, 0xFFFF, 0xFF20, 0xFFFF, 0xFF21, 0xFFFF], True)),
			_names((-1, True, 'Folder'), (0, False, 'My Marine'), (3, False, 'Caf\xe9')),
		)
		fgp = FGP()
		self.assertEqual(fgp.load(data), [])
		self.assertEqual(fgp.button_sets, {0: [Button.unpack(MOVE), Button.unpack(STOP)], 5: []})
		self.assertEqual(fgp.units, [FGPUnit(0, 0, 0xFFFF, StatInfo(0, 1, 0)), FGPUnit(1, None, 3, None)])
		self.assertEqual(fgp.requirements, {
			UnitsGraft: {0: [0xFF05, 0xFFFF], 1: None},
			UpgradesGraft: {2: [0xFF1F, 0xFFFF, 0xFF20, 0xFFFF, 0xFF21, 0xFFFF]},
		})
		self.assertEqual(fgp.names, {ParamKind.unit: {0: 'My Marine', 3: 'Caf\xe9'}})

	def test_extended_unit_ids(self) -> None:
		fgp = FGP()
		warnings = fgp.load(fgp_file(_units((200, 0, 0xFFFF, None), (255, 0, 0xFFFF, None), (2, 0, 0xFFFF, None), (10, 0, 0xFFFF, None))))
		self.assertEqual([unit.unit_id for unit in fgp.units], [200, 255, 258, 266])
		self.assertEqual(len(warnings), 1)
		self.assertIn('Extended unit IDs detected', warnings[0].warning)

	def test_extended_requirement_ids(self) -> None:
		fgp = FGP()
		warnings = fgp.load(fgp_file(_requirements(b'UntR', (5, [0xFFFF], True), (5, [0xFF05, 0xFFFF], True))))
		self.assertEqual(fgp.requirements[UnitsGraft], {5: [0xFFFF], 261: [0xFF05, 0xFFFF]})
		self.assertEqual(len(warnings), 1)
		self.assertIn('Extended IDs detected in the unit requirements', warnings[0].warning)

	def test_unsupported_version(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			FGP().load(fgp_file(version=b'1.15.0'))
		self.assertIn('Unsupported FireGraft project version `1.15.0`', str(cm.exception))

	def test_missing_version(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			FGP().load(_units())
		self.assertIn('Unsupported FireGraft project version `None`', str(cm.exception))

	def test_truncated_chunk(self) -> None:
		# A button set of 1 button, without the data for its button
		data = fgp_file(fgp_chunk(b'Buts', struct.pack('<HBB', 1, 0, 1) + b'\x00'))
		with self.assertRaises(PyMSError) as cm:
			FGP().load(data)
		self.assertIn('Unsupported FireGraft project, could possibly be invalid or corrupt', str(cm.exception))
