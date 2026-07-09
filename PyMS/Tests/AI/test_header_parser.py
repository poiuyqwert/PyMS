
from . import utils

from ...FileFormats.AIBIN.CodeHandlers.AIHeaderSourceCodeParser import AIHeaderSourceCodeParser

from ...Utilities.PyMSError import PyMSError

import unittest

class Test_AIHeaderSourceCodeParser(unittest.TestCase):
	def test_unknown_header_command_raises_pymserror(self) -> None:
		code = 'script TEST {\n\tbogus_command 0\n}\n'
		parse_context = utils.parse_context(code)
		parser = AIHeaderSourceCodeParser()
		with self.assertRaises(PyMSError) as error_context:
			_ = parser.parse(parse_context)
		self.assertIn("Unknown script header command 'bogus_command'", str(error_context.exception))
