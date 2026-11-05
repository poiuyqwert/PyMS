
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
	def test_first_write_is_indented(self) -> None:
		ctx, output = make_context()
		ctx.indent()
		ctx.write('a')
		self.assertEqual(output.getvalue(), '    a')

	def test_indents_following_lines(self) -> None:
		ctx, output = make_context()
		ctx.indent()
		ctx.write('a\nb\n')
		ctx.write('c')
		self.assertEqual(output.getvalue(), '    a\n    b\n    c')

	def test_write_continuing_a_line_is_not_indented(self) -> None:
		ctx, output = make_context()
		ctx.indent()
		ctx.write('a')
		ctx.write('b\n')
		self.assertEqual(output.getvalue(), '    ab\n')

	def test_nested_indent_levels(self) -> None:
		ctx, output = make_context()
		ctx.indent(2)
		ctx.write('a\nb')
		self.assertEqual(output.getvalue(), '        a\n        b')

	def test_trailing_newline_is_not_indented(self) -> None:
		# A trailing newline with no following content must not leave dangling
		# indentation whitespace.
		ctx, output = make_context()
		ctx.indent()
		ctx.write('a\n')
		self.assertEqual(output.getvalue(), '    a\n')

	def test_blank_line_write_is_not_indented(self) -> None:
		ctx, output = make_context()
		ctx.indent()
		ctx.write('a\n')
		ctx.write('\n')
		ctx.write('b\n')
		self.assertEqual(output.getvalue(), '    a\n\n    b\n')

	def test_whitespace_only_line_write_is_not_indented(self) -> None:
		ctx, output = make_context()
		ctx.indent()
		ctx.write(' \n')
		ctx.write('b')
		self.assertEqual(output.getvalue(), ' \n    b')

	def test_interior_blank_lines_are_not_indented(self) -> None:
		ctx, output = make_context()
		ctx.indent()
		ctx.write('a\n\n \nb')
		self.assertEqual(output.getvalue(), '    a\n\n \n    b')

	def test_empty_write_keeps_line_start(self) -> None:
		ctx, output = make_context()
		ctx.indent()
		ctx.write('a\n')
		ctx.write('')
		ctx.write('b')
		self.assertEqual(output.getvalue(), '    a\n    b')


class Test_Dedent(unittest.TestCase):
	def test_dedent_reduces_level(self) -> None:
		ctx, output = make_context()
		ctx.indent(2)
		ctx.dedent()
		ctx.write('a\nb')
		self.assertEqual(output.getvalue(), '    a\n    b')

	def test_line_after_dedent_is_indented_at_new_level(self) -> None:
		ctx, output = make_context()
		ctx.indent(2)
		ctx.write('a\n')
		ctx.dedent()
		ctx.write('b')
		self.assertEqual(output.getvalue(), '        a\n    b')

	def test_dedent_does_not_go_below_zero(self) -> None:
		ctx, output = make_context()
		ctx.dedent()
		ctx.dedent()
		ctx.write('a\nb')
		self.assertEqual(output.getvalue(), 'a\nb')


if __name__ == '__main__':
	unittest.main()
