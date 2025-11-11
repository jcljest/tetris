# core/piece.py
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

# type-only import to avoid circular dependency
if TYPE_CHECKING:
    from core.shapes import ShapeSet


@dataclass(frozen=True)
class Piece:
    kind: str
    x: int
    y: int
    rot: int
    color: tuple[int, int, int]

    def blocks(self, shapes: "ShapeSet"):
        """Return absolute block coordinates using the ShapeSet."""
        return [(self.x + dx, self.y + dy) for (dx, dy) in shapes.offsets(self.kind, self.rot)]

    def moved(self, dx: int, dy: int) -> "Piece":
        """Return a new Piece moved by (dx, dy)."""
        return Piece(self.kind, self.x + dx, self.y + dy, self.rot, self.color)

    def rotated(self, dr: int) -> "Piece":
        """Return a new Piece rotated by dr (mod 4)."""
        return Piece(self.kind, self.x, self.y, (self.rot + dr) % 4, self.color)
