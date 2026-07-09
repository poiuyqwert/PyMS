
import unittest

from ...FileFormats import TBL
from ...FileFormats.AIBIN.AIScript import AIScript

from ...PyAI.Sort import Sort


def _script(script_id: str, string_id: int) -> AIScript:
	return AIScript(script_id, 0, string_id, AIScript.blank_entry_point(), False)


class Test_SortByString(unittest.TestCase):
	def test_orders_by_resolved_string(self) -> None:
		tbl = TBL.TBL()
		tbl.strings = ['zebra', 'apple', 'mango']
		zebra = _script('CCCC', string_id=0)
		apple = _script('BBBB', string_id=1)
		result = Sort.by_string([zebra, apple], tbl)
		self.assertEqual([h.id for h in result], ['BBBB', 'CCCC'])

	def test_out_of_range_string_id_does_not_crash(self) -> None:
		tbl = TBL.TBL()
		tbl.strings = ['zebra', 'apple']
		in_range = _script('BBBB', string_id=1)
		out_of_range = _script('AAAA', string_id=99)
		negative = _script('CCCC', string_id=-1)
		# Out-of-range IDs resolve to an empty key and sort first; no IndexError.
		result = Sort.by_string([in_range, out_of_range, negative], tbl)
		self.assertEqual([h.id for h in result], ['AAAA', 'CCCC', 'BBBB'])

	def test_without_tbl_sorts_by_string_id(self) -> None:
		first = _script('BBBB', string_id=1)
		second = _script('AAAA', string_id=5)
		result = Sort.by_string([second, first], None)
		self.assertEqual([h.id for h in result], ['BBBB', 'AAAA'])


if __name__ == '__main__':
	unittest.main()
