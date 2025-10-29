"""
Tetris in Pygame — single file, no assets
Tested design: 10x20 grid, 7-bag randomizer, soft/hard drop,
rotate with basic wall kicks, scoring, levels, pause & game over.

Controls
- Left/Right: move
- Down: soft drop (faster)
- Up / X: rotate clockwise
- Z: rotate counter-clockwise
- Space: hard drop
- P: pause
- R: restart (on game over)
- Esc: quit

Tune the constants in CONFIG to adjust look/feel.
"""
from __future__ import annotations
import math
import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple

import pygame

# ----------------------------- CONFIG ---------------------------------
CONFIG = {
    "COLS": 10,
    "ROWS": 20,
    "CELL": 32,  # pixel size of one cell
    "FPS": 60,
    # Gravity timing in milliseconds at level 0. Gets faster with level.
    "BASE_FALL_MS": 800,
    # Each level reduces the fall time by this percentage (clamped)
    "LVL_ACCEL": 0.9,  # 10% faster each level
    # DAS (delayed auto shift) and ARR (auto repeat rate) in ms for LR keys
    "DAS_MS": 160,
    "ARR_MS": 40,
}

# NES-like scoring (scaled by (level+1))
SCORES = {1: 40, 2: 100, 3: 300, 4: 1200}

# Colors (RGB)
COLORS = {
    "bg": (16, 18, 20),
    "grid": (32, 36, 40),
    "ghost": (85, 85, 85),
    "text": (230, 238, 245),
    # Tetromino colors
    "I": (80, 227, 230),
    "J": (36, 95, 223),
    "L": (223, 173, 36),
    "O": (223, 217, 36),
    "S": (80, 230, 123),
    "T": (158, 36, 223),
    "Z": (230, 80, 80),
}

# Tetromino shape definitions via rotation states as (x,y) offsets
# Each piece is defined around a reference (piece.x, piece.y) in grid coords.
# Rotation system: simple 4-state with naive wall kicks [-1, 1, -2, 2]
SHAPES = {
    "I": [
        [( -1, 0), (0, 0), (1, 0), (2, 0)],
        [( 1, -1), (1, 0), (1, 1), (1, 2)],
        [(-1, 1), (0, 1), (1, 1), (2, 1)],
        [( 0, -1), (0, 0), (0, 1), (0, 2)],
    ],
    "J": [
        [(-1, 0), (0, 0), (1, 0), (-1, 1)],
        [(0, -1), (0, 0), (0, 1), (1, -1)],
        [(-1, 0), (0, 0), (1, 0), (1, -1)],
        [(0, -1), (0, 0), (0, 1), (-1, 1)],
    ],
    "L": [
        [(-1, 0), (0, 0), (1, 0), (1, 1)],
        [(0, -1), (0, 0), (0, 1), (1, 1)],
        [(-1, -1), (-1, 0), (0, 0), (1, 0)],
        [(-1, -1), (0, -1), (0, 0), (0, 1)],
    ],
    "O": [
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
    ],
    "S": [
        [(-1, 1), (0, 1), (0, 0), (1, 0)],
        [(0, -1), (0, 0), (1, 0), (1, 1)],
        [(-1, 1), (0, 1), (0, 0), (1, 0)],
        [(0, -1), (0, 0), (1, 0), (1, 1)],
    ],
    "T": [
        [(-1, 0), (0, 0), (1, 0), (0, 1)],
        [(0, -1), (0, 0), (0, 1), (1, 0)],
        [(-1, 0), (0, 0), (1, 0), (0, -1)],
        [(0, -1), (0, 0), (0, 1), (-1, 0)],
    ],
    "Z": [
        [(-1, 0), (0, 0), (0, 1), (1, 1)],
        [(1, -1), (1, 0), (0, 0), (0, 1)],
        [(-1, 0), (0, 0), (0, 1), (1, 1)],
        [(1, -1), (1, 0), (0, 0), (0, 1)],
    ],
}

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

# ----------------------------- GAME LOGIC ------------------------------
class SevenBag:
    def __init__(self):
        self.bag: List[str] = []

    def next(self) -> str:
        if not self.bag:
            self.bag = ["I", "J", "L", "O", "S", "T", "Z"]
            random.shuffle(self.bag)
        return self.bag.pop()

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

# ----------------------------- RENDERING -------------------------------
class Renderer:
    def __init__(self, screen: pygame.Surface, cell: int):
        self.screen = screen
        self.cell = cell
        self.font = pygame.font.SysFont("Inter, Menlo, Consolas, Arial", 18)
        self.big = pygame.font.SysFont("Inter, Menlo, Consolas, Arial", 28, bold=True)

    def draw_board(self, board: Board):
        w, h = board.cols * self.cell, board.rows * self.cell
        pygame.draw.rect(self.screen, COLORS["bg"], (0, 0, w, h))
        # grid lines
        for x in range(board.cols + 1):
            pygame.draw.line(self.screen, COLORS["grid"], (x * self.cell, 0), (x * self.cell, h))
        for y in range(board.rows + 1):
            pygame.draw.line(self.screen, COLORS["grid"], (0, y * self.cell), (w, y * self.cell))
        # locked blocks
        for y in range(board.rows):
            for x in range(board.cols):
                c = board.grid[y][x]
                if c is not None:
                    self._cell(x, y, c)

    def _cell(self, x: int, y: int, color: Tuple[int,int,int], alpha: int|None=None):
        r = pygame.Rect(x * self.cell, y * self.cell, self.cell, self.cell)
        pygame.draw.rect(self.screen, color, r)
        # outline
        pygame.draw.rect(self.screen, (0,0,0), r, 2)

    def draw_piece(self, piece: Piece):
        for (x, y) in piece.blocks():
            self._cell(x, y, piece.color)

    def draw_ghost(self, piece: Piece, board: Board):
        dy = board.drop_distance(piece)
        ghost = Piece(piece.kind, piece.x, piece.y + dy, piece.rot, COLORS["ghost"])
        for (x, y) in ghost.blocks():
            r = pygame.Rect(x * self.cell + 4, y * self.cell + 4, self.cell - 8, self.cell - 8)
            pygame.draw.rect(self.screen, COLORS["ghost"], r, 2)

    def hud(self, score: int, level: int, lines: int, paused: bool, game_over: bool):
        texts = [
            f"Score: {score}",
            f"Level: {level}",
            f"Lines: {lines}",
        ]
        if paused:
            texts.append("PAUSED (P)")
        if game_over:
            texts.append("GAME OVER — R to restart")
        y = 8
        for t in texts:
            surf = self.font.render(t, True, COLORS["text"])
            self.screen.blit(surf, (8, y))
            y += surf.get_height() + 4

# ----------------------------- GAME ------------------------------------
class Tetris:
    def __init__(self):
        self.cols, self.rows, self.cell = CONFIG["COLS"], CONFIG["ROWS"], CONFIG["CELL"]
        self.width, self.height = self.cols * self.cell, self.rows * self.cell
        pygame.init()
        pygame.display.set_caption("Pygame Tetris")
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen, self.cell)

        self.board = Board(self.cols, self.rows)
        self.bag = SevenBag()
        self.score = 0
        self.level = 0
        self.lines = 0
        self.paused = False
        self.game_over = False

        self.cur = self._spawn()
        self.fall_ms = CONFIG["BASE_FALL_MS"]
        self.last_fall = 0

        # movement repeat
        self.left_held = False
        self.right_held = False
        self.down_held = False
        self.lr_first_time = {"left": 0, "right": 0}
        self.lr_last_repeat = {"left": 0, "right": 0}

    # ----------------------- helpers -----------------------
    def _spawn(self) -> Piece:
        k = self.bag.next()
        color = COLORS[k]
        # spawn near top; y=0 or -? We'll spawn at row 0 with offsets designed
        p = Piece(k, self.cols // 2, 0, 0, color)
        # nudge up a bit so rotation states fit
        p.y = 1
        if not self.board.valid(p):
            self.game_over = True
        return p

    def _rotate(self, dr: int):
        if self.cur.kind == "O":
            return
        candidate = self.cur.rotated(dr)
        # wall kicks
        for dx in [0, -1, 1, -2, 2]:
            test = Piece(candidate.kind, candidate.x + dx, candidate.y, candidate.rot, candidate.color)
            if self.board.valid(test):
                self.cur = test
                return

    def _move(self, dx: int, dy: int) -> bool:
        test = Piece(self.cur.kind, self.cur.x + dx, self.cur.y + dy, self.cur.rot, self.cur.color)
        if self.board.valid(test):
            self.cur = test
            return True
        return False

    def _hard_drop(self):
        dy = self.board.drop_distance(self.cur)
        if dy > 0:
            self.cur.y += dy
        self._lock()

    def _lock(self):
        cleared = self.board.lock(self.cur)
        if cleared:
            self.lines += cleared
            self.score += SCORES.get(cleared, 0) * (self.level + 1)
            # Level every 10 lines
            new_level = self.lines // 10
            if new_level != self.level:
                self.level = new_level
                self.fall_ms = max(60, int(CONFIG["BASE_FALL_MS"] * (CONFIG["LVL_ACCEL"] ** self.level)))
        self.cur = self._spawn()

    # ----------------------- input handling -----------------
    def _handle_keydown(self, e: pygame.event.Event):
        if e.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit(0)
        if e.key == pygame.K_p:
            self.paused = not self.paused
            return
        if self.game_over:
            if e.key == pygame.K_r:
                self.__init__()
            return
        if self.paused:
            return
        if e.key in (pygame.K_UP, pygame.K_x):
            self._rotate(1)
        elif e.key == pygame.K_z:
            self._rotate(-1)
        elif e.key == pygame.K_SPACE:
            self._hard_drop()
        elif e.key == pygame.K_LEFT:
            self.left_held = True
            self.lr_first_time["left"] = pygame.time.get_ticks()
            self.lr_last_repeat["left"] = 0
            self._move(-1, 0)
        elif e.key == pygame.K_RIGHT:
            self.right_held = True
            self.lr_first_time["right"] = pygame.time.get_ticks()
            self.lr_last_repeat["right"] = 0
            self._move(1, 0)
        elif e.key == pygame.K_DOWN:
            self.down_held = True
            self._move(0, 1)

    def _handle_keyup(self, e: pygame.event.Event):
        if e.key == pygame.K_LEFT:
            self.left_held = False
        elif e.key == pygame.K_RIGHT:
            self.right_held = False
        elif e.key == pygame.K_DOWN:
            self.down_held = False

    def _handle_lr_auto(self, now_ms: int):
        for side, held in (("left", self.left_held), ("right", self.right_held)):
            if not held:
                continue
            first_time = self.lr_first_time[side]
            last_repeat = self.lr_last_repeat[side]
            if now_ms - first_time < CONFIG["DAS_MS"]:
                continue
            if last_repeat and (now_ms - last_repeat) < CONFIG["ARR_MS"]:
                continue
            dx = -1 if side == "left" else 1
            moved = self._move(dx, 0)
            self.lr_last_repeat[side] = now_ms if moved else now_ms  # still throttle

    # ----------------------- update & draw -------------------
    def update(self, dt_ms: int):
        if self.paused or self.game_over:
            return
        now = pygame.time.get_ticks()
        self._handle_lr_auto(now)
        if self.down_held:
            # faster soft drop
            if now - self.last_fall > max(40, self.fall_ms // 15):
                if not self._move(0, 1):
                    self._lock()
                self.last_fall = now
        else:
            if now - self.last_fall > self.fall_ms:
                if not self._move(0, 1):
                    self._lock()
                self.last_fall = now

    def draw(self):
        self.renderer.draw_board(self.board)
        if not self.game_over:
            self.renderer.draw_ghost(self.cur, self.board)
            self.renderer.draw_piece(self.cur)
        self.renderer.hud(self.score, self.level, self.lines, self.paused, self.game_over)
        pygame.display.flip()

    # ----------------------- main loop -----------------------
    def run(self):
        while True:
            dt = self.clock.tick(CONFIG["FPS"])
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit(0)
                elif e.type == pygame.KEYDOWN:
                    self._handle_keydown(e)
                elif e.type == pygame.KEYUP:
                    self._handle_keyup(e)
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Tetris().run()
