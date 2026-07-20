
from ...PyMOD import Source

import unittest

class Test_source_detection(unittest.TestCase):
	def test_aiscript_requires_an_exact_name(self) -> None:
		self.assertEqual(Source.AIScript.matches('aiscript.bin'), 1)
		self.assertEqual(Source.AIScript.matches('aiscriptxbin'), 0)
		self.assertEqual(Source.AIScript.matches('aiscript_bin'), 0)
		self.assertEqual(Source.AIScript.matches('aiscript.bin.bak'), 0)

	def test_iscript_requires_an_exact_name(self) -> None:
		self.assertEqual(Source.IScript.matches('iscript.bin'), 1)
		self.assertEqual(Source.IScript.matches('iscriptxbin'), 0)
		self.assertEqual(Source.IScript.matches('iscript_bin'), 0)
		self.assertEqual(Source.IScript.matches('iscript.bin.bak'), 0)
		self.assertEqual(Source.IScript.matches('aiscript.bin'), 0)

	def test_grp_requires_a_named_grp_extension(self) -> None:
		self.assertEqual(Source.GRP.matches('marine.grp'), 1)
		self.assertEqual(Source.GRP.matches('.grp'), 0)
		self.assertEqual(Source.GRP.matches('marine.grp.bak'), 0)

	def test_tbl_requires_a_named_tbl_extension(self) -> None:
		self.assertEqual(Source.TBL.matches('stat_txt.tbl'), 1)
		self.assertEqual(Source.TBL.matches('.tbl'), 0)

	def test_dat_requires_an_exact_file_name(self) -> None:
		self.assertEqual(Source.DAT.matches('units.dat'), 1)
		self.assertEqual(Source.DAT.matches('sfxdata.dat'), 1)
		self.assertEqual(Source.DAT.matches('custom.dat'), 0)
		self.assertEqual(Source.DAT.matches('UNITS.DAT'), 0)
		self.assertEqual(Source.DAT.matches('units.dat.bak'), 0)
		self.assertEqual(Source.DAT.matches('.dat'), 0)

	def test_lo_requires_a_named_lo_extension(self) -> None:
		for extension in ('loa', 'lob', 'lod', 'lof', 'log', 'lol', 'loo', 'los', 'lou', 'lox'):
			self.assertEqual(Source.LO.matches(f'marine.{extension}'), 1, f'`marine.{extension}` should match')
		self.assertEqual(Source.LO.matches('.loa'), 0)
		self.assertEqual(Source.LO.matches('marine.loa.bak'), 0)
		self.assertEqual(Source.LO.matches('marine.lo'), 0)
		self.assertEqual(Source.LO.matches('marine.lot'), 0)

	def test_pcx_requires_a_named_pcx_extension(self) -> None:
		self.assertEqual(Source.PCX.matches('tfontgam.pcx'), 1)
		self.assertEqual(Source.PCX.matches('.pcx'), 0)
		self.assertEqual(Source.PCX.matches('tfontgam.pcx.bak'), 0)

	def test_mpq_matches_the_extension(self) -> None:
		self.assertEqual(Source.MPQ.matches('mod.mpq'), 1)
		self.assertEqual(Source.MPQ.matches('mod.mpq.bak'), 0)

	def test_folder_and_file_never_match(self) -> None:
		self.assertEqual(Source.Folder.matches('anything'), 0)
		self.assertEqual(Source.File.matches('anything.grp'), 0)
