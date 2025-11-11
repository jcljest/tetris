# core/controller.py
from __future__ import annotations
from typing import TYPE_CHECKING

# Type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from core.board_rect import BoardProtocol
    from core.rules_default import RuleSet
    from core.shapes import ShapeSet


class PieceController:
    """Handles movement, rotation, and locking logic for a single piece."""

    def __init__(self, board: BoardProtocol, rules: RuleSet, shapes: ShapeSet):
        self.board = board
        self.rules = rules
        self.shapes = shapes

    def try_move(self, piece, dx: int = 0, dy: int = 0):
        """Attempt to move piece by dx, dy. Returns new piece if valid, else None."""
        test = piece.moved(dx, dy)
        return test if self.board.valid(test) else None

    def try_rotate(self, piece, dr: int):
        """Attempt to rotate piece with wall kicks; returns new piece if valid."""
        cand = piece.rotated(dr)
        for dx in self.rules.kick_table(cand.kind, piece.rot, cand.rot):
            test = cand.moved(dx, 0)
            if self.board.valid(test):
                return test
        return None

    def hard_drop_and_lock(self, piece, level: int):
        """
        Drop piece instantly, lock it into board, return (final_piece, cleared_lines, score).
        """
        dy = self.board.drop_distance(piece)
        dropped = piece.moved(0, dy)
        cleared = self.board.lock(dropped)
        score = self.rules.score(cleared, level) if cleared else 0
        return dropped, cleared, score
