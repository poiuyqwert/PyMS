
from ..harness import UITestCase

from ...Utilities import UIKit as UI
from ...Utilities import Config


class _Host(UI.MainWindow):
	def __init__(self) -> None:
		UI.MainWindow.__init__(self)
		self.text = UI.CodeText(self)
		self.text.pack(fill=UI.BOTH, expand=1)


class Test_CodeText(UITestCase):
	def make_text(self, selection_background: str = '#C0C0C0') -> tuple[_Host, UI.HighlightComponent]:
		window = self.make_window(_Host)
		selection = UI.HighlightComponent(
			name='Selection',
			description='The style of selected text in the editor.',
			highlight_style=Config.HighlightStyle(default=Config.Style(background=selection_background)),
			tag='sel'
		)
		window.text.set_syntax_highlighting(UI.SyntaxHighlighting(
			syntax_components=(
				UI.SyntaxComponent(patterns=(UI.HighlightPattern(
					highlight=UI.HighlightComponent(
						name='Keyword',
						description='A keyword.',
						highlight_style=Config.HighlightStyle(default=Config.Style(foreground='#0000AA'))
					),
					pattern=r'\balpha\b'
				),)),
			),
			highlight_components=(selection,)
		))
		self.pump(window)
		return window, selection

	def test_selection_stays_visible_when_the_editor_is_unfocused(self) -> None:
		# Tk renders the `sel` tag with `inactiveselectbackground` when the text widget doesn't
		# have focus, so it has to match the configured selection color for a find match to
		# remain visible while the Find/Replace dialog holds focus.
		window, _ = self.make_text()
		self.assertEqual(window.text.text.cget('inactiveselectbackground'), '#C0C0C0')

	def test_selection_color_change_updates_unfocused_selection(self) -> None:
		window, selection = self.make_text()
		selection.highlight_style.style.background = '#FF8800'
		window.text.update_highlight_styles()
		self.pump(window)
		self.assertEqual(window.text.text.cget('inactiveselectbackground'), '#FF8800')

	def test_selection_falls_back_to_the_widget_default(self) -> None:
		# Without a configured selection background the widget's own selection color is used,
		# rather than Tk's washed out default for an unfocused selection.
		window = self.make_window(_Host)
		self.assertEqual(window.text.text.cget('inactiveselectbackground'), window.text.text.cget('selectbackground'))
