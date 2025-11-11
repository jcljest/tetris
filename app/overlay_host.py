# app/overlay_host.py
from typing import Protocol

class Overlay(Protocol):
    id: str
    def draw(self, screen): ...
    def handle(self, action: str): ...

class OverlayHost:
    def __init__(self, registry: dict[str, type[Overlay]]):
        self._reg = registry
        self._stack: list[Overlay] = []
    def push(self, overlay_id: str):
        self._stack.append(self._reg[overlay_id]())
