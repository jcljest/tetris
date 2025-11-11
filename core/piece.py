# core/piece.py
from dataclasses import dataclass
@dataclass(frozen=True)
class Piece:
    kind: str; x: int; y: int; rot: int; color: tuple[int,int,int]
    def blocks(self, shapes: ShapeSet):
        return [(self.x+dx, self.y+dy) for (dx,dy) in shapes.offsets(self.kind, self.rot)]
    def moved(self, dx, dy): return Piece(self.kind, self.x+dx, self.y+dy, self.rot, self.color)
    def rotated(self, dr):  return Piece(self.kind, self.x, self.y, (self.rot+dr) % 4, self.color)
