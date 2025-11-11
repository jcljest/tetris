# core/board_rect.py
from typing import List, Optional, Tuple
from .board import BoardProtocol

RGB = Tuple[int, int, int]

class RectBoard(BoardProtocol):
    """
    Classic rectangular Tetris well. Stores RGB or None per cell.
    Coordinates: (0,0) is top-left cell; y increases downward.
    """
    cols: int
    rows: int

    def __init__(self, cols: int = 10, rows: int = 22) -> None:
        self.cols = cols
        self.rows = rows
        self._grid: List[List[Optional[RGB]]] = [
            [None for _ in range(cols)] for _ in range(rows)
        ]

    # ---- Query helpers ----
    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and 0 <= y < self.rows

    def empty_at(self, x: int, y: int) -> bool:
        return self.inside(x, y) and self._grid[y][x] is None

    def valid(self, piece) -> bool:
        """All blocks must be inside and empty."""
        for (bx, by) in piece.blocks:  # accepts either attr or method-backed adapter
            if not self.inside(bx, by):
                return False
            if self._grid[by][bx] is not None:
                return False
        return True

    # ---- Mutation ----
    def lock(self, piece) -> int:
        """
        Paint piece cells onto grid, then clear lines.
        Returns number of cleared lines.
        """
        color: RGB = getattr(piece, "color", (200, 200, 200))
        for (bx, by) in piece.blocks:
            if not self.inside(bx, by):
                # Out-of-bounds lock → treat as top-out; still guard index
                continue
            self._grid[by][bx] = color
        return self.clear_lines()

    def clear_lines(self) -> int:
        """Remove full rows, insert empty rows on top, return count."""
        keep: List[List[Optional[RGB]]] = [row for row in self._grid if any(cell is None for cell in row)]
        cleared = self.rows - len(keep)
        if cleared:
            empties = [[None for _ in range(self.cols)] for _ in range(cleared)]
            self._grid = empties + keep
        return cleared

    def drop_distance(self, piece) -> int:
        """
        Maximum dy >= 0 s.t. translating piece by (0,dy) remains valid.
        Brute-force downward sweep (fast enough for 60 FPS).
        """
        dy = 0
        while True:
            # build translated blocks once; we use piece.blocks as list of tuples.
            next_blocks = [(x, y + dy + 1) for (x, y) in piece.blocks]
            if all(self.inside(x, y) and self._grid[y][x] is None for (x, y) in next_blocks):
                dy += 1
                # continue loop
            else:
                break
        return dy

    # ---- Minimal view helpers for painters ----
    def cell(self, x: int, y: int) -> Optional[RGB]:
        """Return color at cell or None."""
        if not self.inside(x, y):
            return None
        return self._grid[y][x]

    def iter_rows(self):
        """Yield rows from top to bottom (for rendering)."""
        for y in range(self.rows):
            yield y, self._grid[y]
