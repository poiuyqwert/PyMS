
from .utils import make_chk_with_version
from ...FileFormats.CHK.CHKRequirements import CHKRequirements
from ...FileFormats.CHK.Sections.CHKSectionVER import CHKSectionVER

import unittest


class Test_CHKRequirements(unittest.TestCase):
	def test_vers_expand_from_bitmask(self) -> None:
		req = CHKRequirements(CHKRequirements.VER_BROODWAR, CHKRequirements.MODE_ALL)
		self.assertEqual(req.vers, [CHKSectionVER.BW])

	def test_all_vers(self) -> None:
		req = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
		self.assertEqual(req.vers, [CHKSectionVER.SC100, CHKSectionVER.SC104, CHKSectionVER.BW])

	def test_vanilla_hybrid_vers(self) -> None:
		req = CHKRequirements(CHKRequirements.VER_VANILLA_HYBRID, CHKRequirements.MODE_ALL)
		self.assertEqual(req.vers, [CHKSectionVER.SC100, CHKSectionVER.SC104])

	def test_none_vers(self) -> None:
		req = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)
		self.assertEqual(req.vers, [])

	def test_is_required_when_version_and_mode_match(self) -> None:
		chk = make_chk_with_version(CHKSectionVER.BW)
		req = CHKRequirements(CHKRequirements.VER_BROODWAR, CHKRequirements.MODE_ALL)
		self.assertTrue(req.is_required(chk, CHKRequirements.MODE_MELEE))

	def test_is_not_required_when_version_excluded(self) -> None:
		chk = make_chk_with_version(CHKSectionVER.SC104)
		req = CHKRequirements(CHKRequirements.VER_BROODWAR, CHKRequirements.MODE_ALL)
		self.assertFalse(req.is_required(chk, CHKRequirements.MODE_ALL))

	def test_is_not_required_when_mode_excluded(self) -> None:
		chk = make_chk_with_version(CHKSectionVER.BW)
		req = CHKRequirements(CHKRequirements.VER_BROODWAR, CHKRequirements.MODE_MELEE)
		self.assertFalse(req.is_required(chk, CHKRequirements.MODE_UMS))
