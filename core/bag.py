# core/bag.py
from typing import Protocol

class PieceGenerator(Protocol):
    def next(self) -> str: ...
