# core/match.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List, Tuple, Optional

from .bag import PieceGenerator
from .shapes import ShapeSet
from .rules import RuleSet
from .board import BoardProtocol
from .piece import Piece
from .controller import PieceController
from .progression import ProgressionTracker

RGB = Tuple[int, int, int]

ColorForKind = Callable[[str], RGB]   # e.g., theme.color_for_kind

@dataclass(frozen=True)
class PieceView:
    """Render-only view: absolute blocks + color for current frame."""
    kind: str
    color: RGB
    blocks: List[Tuple[int, int]]

class Match:
    """
    Owns: current piece, next queue, gravity timing, game-over.
    Depends on pure interfaces; no pygame here.
    """
    def __init__(
        self,
        board: BoardProtocol,
        bag: PieceGenerator,
        shapes: ShapeSet,
        rules: RuleSet,
        controller: PieceController,
        prog: ProgressionTracker,
        color_for_kind: Optional[ColorForKind] = None,
        spawn_y: int = 0,
    ) -> None:
        self.board = board
        self.bag = bag
        self.shapes = shapes
        self.rules = rules
        self.ctrl = controller
        self.prog = prog
        self.color_for_kind = color_for_kind or (lambda k: (200, 200, 200))
        self.spawn_y = spawn_y

        self.queue: List[str] = []
        self.cur: Optional[Piece] = None
        self.game_over = False
        self.paused = False

        self._last_fall_ms = 0

        # bootstrap with a few upcoming pieces and the first current piece
        self._ensure_queue(5)
        self._spawn_initial()

    # ---------- public, polled by App ----------

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def update(self, now_ms: int) -> None:
        """Gravity tick; call once per frame with a monotonic ms clock."""
        if self.paused or self.game_over or self.cur is None:
            return
        interval = self.rules.fall_interval_ms(self.prog.level)
        if now_ms - self._last_fall_ms >= interval:
            if not self._soft_fall_step():
                self._lock_and_continue()
            self._last_fall_ms = now_ms

    # ---------- input-intent methods (called by InputRouter/App) ----------

    def move_left(self) -> None:
        self._try_shift(-1, 0)

    def move_right(self) -> None:
        self._try_shift(1, 0)

    def soft_drop_step(self) -> None:
        """One manual soft-drop step (repeat via InputRepeater)."""
        if not self._soft_fall_step():
            self._lock_and_continue()

    def rotate_cw(self) -> None:
        self._try_rotate(+1)

    def rotate_ccw(self) -> None:
        self._try_rotate(-1)

    def hard_drop(self) -> None:
        if self.cur is None: return
        dropped, cleared = self._hard_drop_and_lock()
        # update progression/level/score
        self._on_lines_cleared(cleared)
        self._spawn_next_or_game_over()

    # ---------- rendering helpers ----------

    def piece_view(self) -> Optional[PieceView]:
        """Build a render-only view (absolute coords + color)."""
        if self.cur is None: return None
        blocks = [(self.cur.x + dx, self.cur.y + dy) for (dx, dy) in self.shapes.offsets(self.cur.kind, self.cur.rot)]
        return PieceView(self.cur.kind, self.cur.color, blocks)

    def ghost_blocks(self) -> List[Tuple[int, int]]:
        pv = self.piece_view()
        if pv is None: return []
        # drop distance using BoardProtocol.drop_distance; expects piece-like with .blocks
        # Adaptor: a tiny object exposing .blocks attribute
        tmp = type("PV", (), {"blocks": pv.blocks})
        dy = self.board.drop_distance(tmp)
        return [(x, y + dy) for (x, y) in pv.blocks]

    # ---------- internals ----------

    def _ensure_queue(self, target_len: int) -> None:
        while len(self.queue) < target_len:
            self.queue.append(self.bag.next())

    def _spawn_initial(self) -> None:
        self._spawn_from_queue()
        # small nudge so kicks fit, if you prefer
        if self.cur: 
            self.cur = Piece(self.cur.kind, self.cur.x, max(self.spawn_y, 0), self.cur.rot, self.cur.color)
            if not self.board.valid(self._as_board_piece(self.cur)):
                self.game_over = True

    def _spawn_from_queue(self) -> None:
        self._ensure_queue(5)
        kind = self.queue.pop(0)
        color = self.color_for_kind(kind)
        x = self.board.cols // 2
        y = self.spawn_y
        self.cur = Piece(kind, x, y, 0, color)

    def _spawn_next_or_game_over(self) -> None:
        self._spawn_from_queue()
        if not self.board.valid(self._as_board_piece(self.cur)):
            self.game_over = True

    def _try_shift(self, dx: int, dy: int) -> None:
        if self.cur is None: return
        test = self.cur.moved(dx, dy)
        if self.board.valid(self._as_board_piece(test)):
            self.cur = test

    def _try_rotate(self, dr: int) -> None:
        if self.cur is None: return
        cand = self.cur.rotated(dr)
        # wall kicks via RuleSet
        for kick_dx in self.rules.kick_table(cand.kind, self.cur.rot, cand.rot):
            test = cand.moved(kick_dx, 0)
            if self.board.valid(self._as_board_piece(test)):
                self.cur = test
                return

    def _soft_fall_step(self) -> bool:
        """Return True if moved down; False if blocked."""
        if self.cur is None: return False
        test = self.cur.moved(0, 1)
        if self.board.valid(self._as_board_piece(test)):
            self.cur = test
            return True
        return False

    def _hard_drop_and_lock(self) -> Tuple[Piece, int]:
        """Return (final_piece, cleared_lines)."""
        if self.cur is None: return None, 0  # type: ignore
        # max drop
        pv = self.piece_view()
        if pv is None: return self.cur, 0
        tmp = type("PV", (), {"blocks": pv.blocks})
        dy = self.board.drop_distance(tmp)
        self.cur = self.cur.moved(0, dy)
        cleared = self.board.lock(self._as_board_piece(self.cur))
        return self.cur, cleared

    def _lock_and_continue(self) -> None:
        _, cleared = self._hard_drop_and_lock()
        self._on_lines_cleared(cleared)
        self._spawn_next_or_game_over()

    def _on_lines_cleared(self, n: int) -> None:
        leveled = self.prog.on_lines_cleared(n, self.rules)
        # (optional) react to level-ups here

    # ---- board-piece adapter ----
    def _as_board_piece(self, p: Piece):
        """
        Many Board implementations expect an object with a `.blocks` attribute
        (precomputed absolute coords). Build that on the fly from shapes.
        """
        blocks = [(p.x + dx, p.y + dy) for (dx, dy) in self.shapes.offsets(p.kind, p.rot)]
        return type("BP", (), {"blocks": blocks, "color": p.color})
