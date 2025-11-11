# app/input_router.py
from typing import Protocol

class InputDevice(Protocol):
    def poll(self) -> list[str]: ...  # ["MOVE_LEFT", "ROT_CW", "HARD_DROP", ...]

class KeyboardDevice:
    def __init__(self, keymap): self.keymap = keymap
    def poll(self):
        actions = []
        for e in pygame.event.get():
            # map to actions without touching game state
            ...
        return actions
