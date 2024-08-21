
from __future__ import annotations

from enum import StrEnum

from ..Utilities.CodeHandlers import Formatters

class BlockFormat(StrEnum):
	hyphens = 'hyphens'
	colon = 'colon'

	@staticmethod
	def all() -> list[BlockFormat]:
		return [
			BlockFormat.hyphens,
			BlockFormat.colon,
		]

	@property
	def label(self) -> str:
		match self:
			case BlockFormat.hyphens:
				return 'Hyphens     --block--'
			case BlockFormat.colon:
				return 'Colon       :block'

	@property
	def formatter(self) -> Formatters.BlockFormatter:
		match self:
			case BlockFormat.hyphens:
				return Formatters.HyphenBlockFormatter()
			case BlockFormat.colon:
				return Formatters.ColonBlockFormatter()

class CommandFormat(StrEnum):
	flat = 'flat'
	parens = 'parens'

	@staticmethod
	def all() -> list[CommandFormat]:
		return [
			CommandFormat.flat,
			CommandFormat.parens,
		]

	@property
	def label(self) -> str:
		match self:
			case CommandFormat.flat:
				return 'Flat        wait 1'
			case CommandFormat.parens:
				return 'Parens      wait(1)'

	@property
	def formatter(self) -> Formatters.CommandFormatter:
		match self:
			case CommandFormat.flat:
				return Formatters.FlatCommandFormatter()
			case CommandFormat.parens:
				return Formatters.ParensCommandFormatter()

class CommentFormat(StrEnum):
	hash = 'hash'
	semicolon = 'semicolon'

	@staticmethod
	def all() -> list[CommentFormat]:
		return [
			CommentFormat.hash,
			CommentFormat.semicolon,
		]

	@property
	def label(self) -> str:
		match self:
			case CommentFormat.hash:
				return 'Hash        # comment'
			case CommentFormat.semicolon:
				return 'Semicolon   ; comment'

	@property
	def formatter(self) -> Formatters.CommentFormatter:
		match self:
			case CommentFormat.hash:
				return Formatters.HashCommentFormatter()
			case CommentFormat.semicolon:
				return Formatters.SemicolonCommentFormatter()
