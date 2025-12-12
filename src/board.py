from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple
from .piece import Piece

class Board:
    def __init__(self, cols: int, rows: int):
        self.cols = cols
        self.rows = rows
        self.grid: List[List[Tuple[int,int,int] | None]] = [
            [None for _ in range(cols)] for _ in range(rows)
        ]

    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and 0 <= y < self.rows

    def empty_at(self, x: int, y: int) -> bool:
        return self.inside(x, y) and self.grid[y][x] is None

    def valid(self, piece: Piece) -> bool:
        for (x, y) in piece.blocks():
            if not self.inside(x, y):
                return False
            if self.grid[y][x] is not None:
                return False
        return True

    def lock(self, piece: Piece) -> int:
        for (x, y) in piece.blocks():
            if 0 <= y < self.rows:
                self.grid[y][x] = piece.color
        return self.clear_lines()

    def clear_lines(self) -> int:
        new_rows = [row for row in self.grid if any(cell is None for cell in row)]
        cleared = self.rows - len(new_rows)
        if cleared:
            self.grid = [[None for _ in range(self.cols)] for _ in range(cleared)] + new_rows
        return cleared

    def drop_distance(self, piece: Piece) -> int:
        dy = 0
        test = Piece(piece.kind, piece.x, piece.y, piece.rot, piece.color)
        while True:
            test.y += 1
            if not self.valid(test):
                break
            dy += 1
        return dy