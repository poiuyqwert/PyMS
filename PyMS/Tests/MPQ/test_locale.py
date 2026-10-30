import unittest

from ...FileFormats.MPQ.MPQ import MPQLocale
from ...FileFormats.MPQ.PQmpq.MPQ import MPQLocale as PQmpqLocale

# MPQ locales are Windows language identifiers (LCIDs)
EXPECTED_LCIDS = {
	'neutral': 0x000,
	'chinese': 0x404,
	'czech': 0x405,
	'german': 0x407,
	'english': 0x409,
	'spanish': 0x40A,
	'french': 0x40C,
	'italian': 0x410,
	'japanese': 0x411,
	'korean': 0x412,
	'polish': 0x415,
	'portuguese': 0x416,
	'russian': 0x419,
	'english_uk': 0x809,
}

class Test_MPQLocale(unittest.TestCase):
	def test_locales_are_windows_lcids(self) -> None:
		for locale_class in (MPQLocale, PQmpqLocale):
			for name, lcid in EXPECTED_LCIDS.items():
				with self.subTest(locale_class=locale_class.__module__, name=name):
					self.assertEqual(getattr(locale_class, name), lcid)
