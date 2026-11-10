
from ..harness import UITestCase

from ...Utilities import UIKit as UI
from ...Utilities.Config import HighlightStyle, Style


class Test_CodeText_InactiveSelectBackground(UITestCase):
	def make_text(self, selection_style: Style) -> tuple[UI.CodeText, HighlightStyle]:
		window = self.make_window(UI.MainWindow)
		text = UI.CodeText(window)
		text.pack(fill=UI.BOTH, expand=1)
		text.text.config(background='#FFFFFF')
		highlight_style = HighlightStyle(selection_style)
		text.set_syntax_highlighting(UI.SyntaxHighlighting(
			syntax_components=(),
			highlight_components=(
				UI.HighlightComponent(
					name='Selection',
					description='Selected text',
					highlight_style=highlight_style,
					tag='sel'
				),
			)
		))
		self.pump(window)
		return text, highlight_style

	def expected_blend(self, text: UI.CodeText, color: str, background: str) -> str:
		channels = (((a + b) // 2) >> 8 for a, b in zip(text.winfo_rgb(color), text.winfo_rgb(background)))
		return '#' + ''.join(f'{channel:02X}' for channel in channels)

	def test_inactive_selection_is_selection_color_half_blended_into_background(self) -> None:
		text, _ = self.make_text(Style(background='#FF0000'))
		self.assertEqual(text.text.cget('inactiveselectbackground'), '#FF7F7F')

	def test_inactive_selection_follows_selection_style_updates(self) -> None:
		text, highlight_style = self.make_text(Style(background='#FF0000'))
		highlight_style.style.background = '#0000FF'
		text.update_highlight_styles()
		self.assertEqual(text.text.cget('inactiveselectbackground'), '#7F7FFF')

	def test_inactive_selection_uses_widget_select_background_without_style_background(self) -> None:
		text, _ = self.make_text(Style())
		expected = self.expected_blend(text, text.text.cget('selectbackground'), '#FFFFFF')
		self.assertEqual(text.text.cget('inactiveselectbackground'), expected)


class Test_CodeText_UpdateHighlightStyles(UITestCase):
	def make_text(self, style: Style) -> tuple[UI.CodeText, HighlightStyle]:
		window = self.make_window(UI.MainWindow)
		text = UI.CodeText(window)
		text.pack(fill=UI.BOTH, expand=1)
		highlight_style = HighlightStyle(style)
		text.set_syntax_highlighting(UI.SyntaxHighlighting(
			syntax_components=(),
			highlight_components=(
				UI.HighlightComponent(
					name='Keyword',
					description='Keywords',
					highlight_style=highlight_style
				),
			)
		))
		self.pump(window)
		return text, highlight_style

	def test_tag_bindings_are_kept(self) -> None:
		# Tooltips bind to highlight tags, so restyling must not remove them
		text, _ = self.make_text(Style(foreground='#FF0000'))
		text.text.tag_bind('Keyword', UI.Cursor.Enter(), lambda _: None)
		text.update_highlight_styles()
		self.assertTrue(text.text.tk.call(str(text.text), 'tag', 'bind', 'Keyword'))

	def test_tagged_ranges_are_kept(self) -> None:
		text, _ = self.make_text(Style(foreground='#FF0000'))
		text.insert('1.0', 'word')
		text.tag_add('Keyword', '1.0', '1.4')
		text.update_highlight_styles()
		self.assertEqual([str(index) for index in text.tag_ranges('Keyword')], ['1.0', '1.4'])

	def test_options_the_style_no_longer_sets_are_cleared(self) -> None:
		text, highlight_style = self.make_text(Style(foreground='#FF0000', background='#00FF00', bold=True))
		self.assertEqual(text.text.tag_cget('Keyword', 'foreground'), '#FF0000')
		highlight_style.style.foreground = None
		highlight_style.style.background = None
		highlight_style.style.bold = False
		text.update_highlight_styles()
		self.assertEqual(text.text.tag_cget('Keyword', 'foreground'), '')
		self.assertEqual(text.text.tag_cget('Keyword', 'background'), '')
		self.assertEqual(text.text.tag_cget('Keyword', 'font'), '')

	def test_changed_options_are_applied(self) -> None:
		text, highlight_style = self.make_text(Style(foreground='#FF0000'))
		highlight_style.style.foreground = '#0000FF'
		text.update_highlight_styles()
		self.assertEqual(text.text.tag_cget('Keyword', 'foreground'), '#0000FF')


class Test_CodeText_LinesColors(UITestCase):
	def make_text(self, background: str, foreground: str) -> UI.CodeText:
		window = self.make_window(UI.MainWindow)
		text = UI.CodeText(window)
		text.pack(fill=UI.BOTH, expand=1)
		text.text.config(background=background, foreground=foreground)
		text.update_lines_colors()
		self.pump(window)
		return text

	def brightness(self, text: UI.CodeText, color: str) -> int:
		return sum(text.winfo_rgb(color))

	def test_lines_background_is_darkened_text_background(self) -> None:
		text = self.make_text('#FFFFFF', '#000000')
		self.assertEqual(text.lines.cget('background'), '#E6E6E6')

	def test_lines_foreground_is_text_foreground_half_blended_into_lines_background(self) -> None:
		text = self.make_text('#FFFFFF', '#000000')
		self.assertEqual(text.lines.cget('foreground'), '#737373')

	def test_lines_background_is_darker_than_dark_text_background(self) -> None:
		text = self.make_text('#2B2B2B', '#BBBBBB')
		self.assertLess(self.brightness(text, text.lines.cget('background')), self.brightness(text, '#2B2B2B'))

	def test_lines_colors_follow_text_colors_on_highlight_style_update(self) -> None:
		text = self.make_text('#FFFFFF', '#000000')
		text.set_syntax_highlighting(UI.SyntaxHighlighting(
			syntax_components=(),
			highlight_components=(
				UI.HighlightComponent(
					name='Keyword',
					description='Keywords',
					highlight_style=HighlightStyle(Style(foreground='#FF0000'))
				),
			)
		))
		text.text.config(background='#000000', foreground='#FFFFFF')
		text.update_highlight_styles()
		self.assertEqual(text.lines.cget('background'), '#000000')
		self.assertEqual(text.lines.cget('foreground'), '#7F7F7F')


class Test_CodeText_LineNumbers(UITestCase):
	def make_text(self, code: str) -> UI.CodeText:
		window = self.make_window(UI.MainWindow)
		text = UI.CodeText(window)
		text.pack(fill=UI.BOTH, expand=1)
		text.load(code)
		self.pump(window)
		return text

	def assertLineNumbers(self, text: UI.CodeText, count: int) -> None:
		self.assertEqual(text.get('1.0', UI.END).count('\n'), count)
		numbers = [int(number) for number in text.lines.get('1.0', 'end -1c').split('\n')]
		self.assertEqual(numbers, list(range(1, count + 1)))

	def test_line_numbers_match_loaded_text(self) -> None:
		text = self.make_text('\n'.join(['a'] * 10))
		self.assertLineNumbers(text, 10)

	def test_line_numbers_follow_every_inserted_line(self) -> None:
		text = self.make_text('\n'.join(['a'] * 10))
		for count in range(11, 14):
			text.insert('end -1c', '\nb')
			self.assertLineNumbers(text, count)

	def test_line_numbers_follow_deleted_lines_after_inserting(self) -> None:
		text = self.make_text('\n'.join(['a'] * 10))
		text.insert('end -1c', '\nb\nc')
		self.assertLineNumbers(text, 12)
		text.delete('1.0', '2.0')
		self.assertLineNumbers(text, 11)
		text.delete('1.0', '4.0')
		self.assertLineNumbers(text, 8)

	def test_line_numbers_follow_undo_and_redo(self) -> None:
		text = self.make_text('\n'.join(['a'] * 10))
		text.insert('end -1c', '\nb')
		text.edit_separator()
		text.insert('end -1c', '\nc')
		self.assertLineNumbers(text, 12)
		text.edit_undo()
		self.assertLineNumbers(text, 11)
		text.edit_redo()
		self.assertLineNumbers(text, 12)
