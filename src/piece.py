from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple
from .config import SHAPES





# ----------------------------- DATA TYPES ------------------------------
@dataclass
class Piece:
    kind: str
    x: int
    y: int
    rot: int = 0
    color: Tuple[int, int, int] = field(default_factory=lambda: (200, 200, 200))

    def blocks(self) -> List[Tuple[int, int]]:
        return [(self.x + dx, self.y + dy) for (dx, dy) in SHAPES[self.kind][self.rot]]

    def rotated(self, dr: int) -> "Piece":
        return Piece(self.kind, self.x, self.y, (self.rot + dr) % 4, self.color)
