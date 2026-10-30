
from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning, PyMSWarnList

import unittest


class Test_PyMSError_repr(unittest.TestCase):
	def test_basic_error(self) -> None:
		self.assertEqual(repr(PyMSError('Parse', 'bad thing')), 'Parse Error: bad thing')

	def test_includes_line_and_code(self) -> None:
		error = PyMSError('Parse', 'bad thing', line=4, code='some code')
		self.assertEqual(repr(error), 'Parse Error: bad thing\n    Line 5: some code')

	def test_line_without_code(self) -> None:
		error = PyMSError('Parse', 'bad thing', line=4)
		self.assertEqual(repr(error), 'Parse Error: bad thing\n    Line 5')

	def test_str_matches_repr(self) -> None:
		error = PyMSError('Parse', 'bad thing', line=4, code='c')
		self.assertEqual(str(error), repr(error))

	def test_includes_warnings(self) -> None:
		warning = PyMSWarning(warn_type='Style', warning='watch out')
		error = PyMSError('Parse', 'bad thing', warnings=[warning])
		self.assertEqual(repr(error), 'Parse Error: bad thing\nStyle Warning: watch out')

	def test_no_legacy_repr_method(self) -> None:
		self.assertFalse(hasattr(PyMSError('Parse', 'x'), 'repr'))


class Test_PyMSWarning_repr(unittest.TestCase):
	def test_basic_warning(self) -> None:
		self.assertEqual(repr(PyMSWarning(warn_type='Style', warning='watch out')), 'Style Warning: watch out')

	def test_includes_id(self) -> None:
		warning = PyMSWarning(warn_type='Style', warning='watch out', warn_id='abc')
		self.assertEqual(repr(warning), 'Style Warning (abc): watch out')

	def test_includes_line_and_code(self) -> None:
		warning = PyMSWarning(warn_type='Style', warning='watch out', line=2, code='code')
		self.assertEqual(repr(warning), 'Style Warning: watch out\n    Line 3: code')

	def test_includes_sub_warnings(self) -> None:
		sub = PyMSWarning(warn_type='Style', warning='sub')
		warning = PyMSWarning(warn_type='Style', warning='main', sub_warnings=[sub])
		self.assertEqual(repr(warning), 'Style Warning: main\nStyle Warning: sub')

	def test_no_legacy_repr_method(self) -> None:
		self.assertFalse(hasattr(PyMSWarning(warn_type='Style', warning='x'), 'repr'))


class Test_PyMSWarnList_repr(unittest.TestCase):
	def test_joins_warnings_with_newlines(self) -> None:
		warnings = [PyMSWarning(warn_type='Style', warning='one'), PyMSWarning(warn_type='Style', warning='two')]
		self.assertEqual(repr(PyMSWarnList(warnings)), 'Style Warning: one\nStyle Warning: two')
