
from __future__ import annotations

from .Callback import Callback

class EditedState:
    def __init__(self, edited: bool = False) -> None:
        self._edited = edited
        self.sub_states: list[EditedState] = []
        self.callback: Callback[bool] = Callback()

    @property
    def is_edited(self) -> bool:
        edited = self._edited
        for sub_state in self.sub_states:
            edited |= sub_state.is_edited
        return edited

    def mark_edited(self, edited: bool = True) -> None:
        self._edited = edited
        self.callback(self.is_edited)

    def add_sub_state(self, edited_state: EditedState) -> None:
        self.sub_states.append(edited_state)
        edited_state.callback += self.update_sub_states

    def sub_state(self) -> EditedState:
        edited_state = EditedState()
        self.add_sub_state(edited_state)
        return edited_state

    def remove_sub_state(self, edited_state: EditedState) -> None:
        if not edited_state in self.sub_states:
            return
        self.sub_states.remove(edited_state)
        self.update_sub_states(False)

    def update_sub_states(self, _: bool) -> None:
        self.callback(self.is_edited)
