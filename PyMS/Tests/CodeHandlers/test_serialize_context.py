
from ...Utilities.CodeHandlers.SerializeContext import SerializeContext

import unittest, io


def make_context() -> tuple[SerializeContext, io.StringIO]:
	output = io.StringIO()
	return SerializeContext(output), output


class Test_Write(unittest.TestCase):
	def test_plain_write(self) -> None:
		ctx, output = make_context()
		ctx.write('hello')
		self.assertEqual(output.getvalue(), 'hello')

	def test_no_indent_at_level_zero(self) -> None:
		ctx, output = make_context()
		ctx.write('a\nb')
		self.assertEqual(output.getvalue(), 'a\nb')


class Test_Indent(unittest.TestCase):
	def test_indents_following_lines(self) -> None:
		ctx, output = make_context()
		ctx.indent()
		# The first write after a newline gets the indent; interior newlines too.
		ctx.write('a\nb\n')
		self.assertEqual(output.getvalue(), 'a\n    b\n')

	def test_force_indent_indents_first_line(self) -> None:
		ctx, output = make_context()
		ctx.indent()
		ctx.write('x', force_indent=True)
		self.assertEqual(output.getvalue(), '    x')

	def test_nested_indent_levels(self) -> None:
		ctx, output = make_context()
		ctx.indent(2)
		ctx.write('a\nb')
		self.assertEqual(output.getvalue(), 'a\n        b')

	def test_trailing_newline_is_not_indented(self) -> None:
		# A trailing newline with no following content must not leave dangling
		# indentation whitespace.
		ctx, output = make_context()
		ctx.indent()
		ctx.write('a\n')
		self.assertEqual(output.getvalue(), 'a\n')


class Test_Dedent(unittest.TestCase):
	def test_dedent_reduces_level(self) -> None:
		ctx, output = make_context()
		ctx.indent(2)
		ctx.dedent()
		ctx.write('a\nb')
		self.assertEqual(output.getvalue(), 'a\n    b')

	def test_dedent_does_not_go_below_zero(self) -> None:
		ctx, output = make_context()
		ctx.dedent()
		ctx.dedent()
		ctx.write('a\nb')
		self.assertEqual(output.getvalue(), 'a\nb')


if __name__ == '__main__':
	unittest.main()
