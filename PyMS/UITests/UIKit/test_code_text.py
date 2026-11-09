
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
