# core/shapes.py
from typing import Dict, List, Tuple

Offset = Tuple[int, int]

class ShapeSet:
    """Protocol-like base for typing only."""
    def kinds(self) -> List[str]: ...
    def offsets(self, kind: str, rot: int) -> List[Offset]: ...
    def rotations(self, kind: str) -> int: ...

class SrsShapeSet(ShapeSet):
    """SRS piece definitions: offsets per rotation."""
    def __init__(self):
        # fmt: off
        self._shapes: Dict[str, List[List[Offset]]] = {
            "I": [[(-1,0),(0,0),(1,0),(2,0)], [(1,-1),(1,0),(1,1),(1,2)],
                  [(-1,1),(0,1),(1,1),(2,1)], [(0,-1),(0,0),(0,1),(0,2)]],
            "O": [[(0,0),(1,0),(0,1),(1,1)]]*4,
            "T": [[(0,0),(-1,0),(1,0),(0,1)], [(0,0),(0,-1),(0,1),(1,0)],
                  [(0,0),(-1,0),(1,0),(0,-1)], [(0,0),(0,-1),(0,1),(-1,0)]],
            "S": [[(0,0),(-1,0),(0,1),(1,1)], [(0,0),(0,1),(1,0),(1,-1)],
                  [(0,0),(-1,0),(0,1),(1,1)], [(0,0),(0,1),(1,0),(1,-1)]],
            "Z": [[(0,0),(1,0),(0,1),(-1,1)], [(0,0),(0,1),(-1,0),(-1,-1)],
                  [(0,0),(1,0),(0,1),(-1,1)], [(0,0),(0,1),(-1,0),(-1,-1)]],
            "J": [[(0,0),(-1,0),(-1,1),(1,0)], [(0,0),(0,-1),(0,1),(1,1)],
                  [(0,0),(-1,0),(1,0),(1,-1)], [(0,0),(0,-1),(0,1),(-1,-1)]],
            "L": [[(0,0),(1,0),(-1,0),(1,1)], [(0,0),(0,-1),(0,1),(1,-1)],
                  [(0,0),(1,0),(-1,0),(-1,-1)], [(0,0),(0,-1),(0,1),(1,1)]],
        }
        # fmt: on

    def kinds(self) -> List[str]:
        return list(self._shapes.keys())

    def rotations(self, kind: str) -> int:
        return len(self._shapes[kind])

    def offsets(self, kind: str, rot: int) -> List[Offset]:
        rot %= self.rotations(kind)
        return self._shapes[kind][rot]
