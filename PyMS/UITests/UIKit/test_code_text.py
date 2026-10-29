
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
