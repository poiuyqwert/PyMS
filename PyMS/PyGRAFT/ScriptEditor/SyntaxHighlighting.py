
from ..Config import PyGRAFTConfig

from ...Utilities import UIKit as UI

import re

from typing import Sequence

def build_syntax_highlighting(highlights: PyGRAFTConfig.Code.Highlights, command_names: Sequence[str], keywords: Sequence[str]) -> UI.SyntaxHighlighting:
	# The highlighting of a script, whose commands (and block keywords) and parameter keywords differ by what it's for
	cmd_names = [re.escape(name) for name in command_names]
	# A script without parameter keywords still has the style (so every script has the same styles), but it never matches
	keyword_pattern = '|'.join(re.escape(keyword) for keyword in keywords) or r'(?!)'
	return UI.SyntaxHighlighting(
		syntax_components=(
			UI.SyntaxComponent((
				UI.HighlightPattern(
					highlight=UI.HighlightComponent(
						name='Comment',
						description='The style of a comment.',
						highlight_style=highlights.comment
					),
					pattern=r'(?:#|;)[^\n]*$'
				),
			)),
			UI.SyntaxComponent((
				UI.HighlightPattern(
					highlight=UI.HighlightComponent(
						name='String',
						description='The style of a quoted name.',
						highlight_style=highlights.string
					),
					pattern=r"'[^'\n]*'|\"[^\"\n]*\""
				),
			)),
			UI.SyntaxComponent((
				r'\b',
				UI.HighlightPattern(
					highlight=UI.HighlightComponent(
						name='Command',
						description='The style of a command.',
						highlight_style=highlights.command
					),
					pattern='|'.join(cmd_names)
				),
				r'\b'
			)),
			UI.SyntaxComponent((
				r'\b',
				UI.HighlightPattern(
					highlight=UI.HighlightComponent(
						name='Keyword',
						description='The style of keywords.',
						highlight_style=highlights.keyword
					),
					pattern=keyword_pattern
				),
				r'\b'
			)),
			UI.SyntaxComponent((
				r'\b',
				UI.HighlightPattern(
					highlight=UI.HighlightComponent(
						name='Number',
						description='The style of a number.',
						highlight_style=highlights.number
					),
					pattern=r'0x[0-9a-fA-F]+|\d+'
				),
				r'\b'
			)),
			UI.SyntaxComponent((
				UI.HighlightPattern(
					highlight=UI.HighlightComponent(
						name='Operator',
						description='The style of the operators: ( ) { } ,',
						highlight_style=highlights.operator
					),
					pattern=r'[(){},]'
				),
			)),
			UI.SyntaxComponent((
				UI.HighlightPattern(
					highlight=UI.HighlightComponent(
						name='Newline',
						description='The style of newlines.',
						highlight_style=highlights.newline
					),
					pattern=r'\n'
				),
			)),
		),
		highlight_components=(
			UI.HighlightComponent(
				name='Selection',
				description='The style of selected text in the editor.',
				highlight_style=highlights.selection,
				tag='sel'
			),
			UI.HighlightComponent(
				name='Error',
				description='The style of highlighted errors in the editor.',
				highlight_style=highlights.error
			),
			UI.HighlightComponent(
				name='Warning',
				description='The style of highlighted warnings in the editor.',
				highlight_style=highlights.warning
			),
		)
	)
