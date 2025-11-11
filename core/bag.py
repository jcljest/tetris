# core/bag.py
import random
from typing import List
from .shapes import ShapeSet

class PieceGenerator:
    """Protocol-like base for typing only."""
    def next(self) -> str:
        raise NotImplementedError

class SevenBag(PieceGenerator):
    """Classic '7-bag' generator used in modern Tetris."""
    def __init__(self, shapes: ShapeSet):
        self.shapes = shapes
        self.bag: List[str] = []

    def _refill(self):
        self.bag = self.shapes.kinds().copy()
        random.shuffle(self.bag)

    def next(self) -> str:
        if not self.bag:
            self._refill()
        return self.bag.pop()
