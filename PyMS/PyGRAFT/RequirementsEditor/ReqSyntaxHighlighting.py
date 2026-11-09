
from ..Config import PyGRAFTConfig

from ...FileFormats.Graft.CodeHandlers import GraftLanguage

from ...Utilities import UIKit as UI

import re

def build_syntax_highlighting(highlights: PyGRAFTConfig.Code.Highlights, language: type[GraftLanguage]) -> UI.SyntaxHighlighting:
	# The highlighting of a requirement script's commands, which differ by the language of the file
	cmd_names = [re.escape(cmd_def.name) for cmd_def in language.commands()]
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
						description='The style of the operators: ( ) ,',
						highlight_style=highlights.operator
					),
					pattern=r'[(),]'
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
