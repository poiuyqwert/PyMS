from __future__ import annotations

from .JumpTarget import JumpTarget

from ..Utilities import UIKit as UI
from ..Utilities import Assets
from ..Utilities import Config

from dataclasses import dataclass
from typing import Protocol, cast

@dataclass(frozen=True)
class UsedByReference:
	# An entry that references the selected entry, and the text its row shows
	target: JumpTarget
	entry_id: int
	text: str

class UsedByDelegate(Protocol):
	def jump(self, target: JumpTarget, entry_id: int) -> None:
		...

# A collapsible list of the entries that reference the selected entry (double-click or Return on a row jumps to it)
class UsedByView(UI.Frame):
	def __init__(self, parent: UI.Misc, delegate: UsedByDelegate, show: Config.Boolean) -> None:
		super().__init__(parent)
		self.delegate = delegate
		# Whether the list is expanded, remembered between runs
		self.show = show
		self.references: list[UsedByReference] = []

		header = UI.Frame(self)
		self.collapse_button = UI.Button(header, image=Assets.get_image('arrow'), command=self.toggle)
		self.collapse_button.pack(side=UI.LEFT, padx=(0, 5))
		self.header_text = UI.StringVar()
		UI.Label(header, textvariable=self.header_text).pack(side=UI.LEFT)
		header.pack(side=UI.TOP, fill=UI.X)
		self.listbox = UI.ScrolledListbox(self, font=UI.Font.fixed(), width=1, height=6)
		self.listbox.bind(UI.Double.Click_Left(), lambda _: self.jump_to_selected())
		self.listbox.bind(UI.Key.Return(), lambda _: self.jump_to_selected())

		self.update_visibility()
		self.update_header()

	def update_header(self) -> None:
		text = f'Used By ({len(self.references)})'
		if self.show.value:
			text += ':'
		self.header_text.set(text)

	def update_visibility(self) -> None:
		if self.show.value:
			self.listbox.pack(side=UI.BOTTOM, fill=UI.X, padx=2, pady=2)
			self.collapse_button['image'] = Assets.get_image('arrow')
		else:
			self.listbox.pack_forget()
			self.collapse_button['image'] = Assets.get_image('arrowup')

	def toggle(self) -> None:
		self.show.value = not self.show.value
		self.update_visibility()
		self.update_header()

	def set_references(self, references: list[UsedByReference]) -> None:
		self.references = references
		self.listbox.delete(0, UI.END)
		if references:
			self.listbox.insert(UI.END, *(reference.text for reference in references))
		self.update_header()

	def jump_to_selected(self) -> None:
		selection = cast(list[int], self.listbox.curselection())
		if not selection or not 0 <= selection[0] < len(self.references):
			return
		reference = self.references[selection[0]]
		self.delegate.jump(reference.target, reference.entry_id)
