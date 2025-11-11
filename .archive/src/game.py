
from __future__ import annotations
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import pygame

from bag import SevenBag
from board import Board
from config import COLORS, SCORES, CONFIG
from piece import Piece
from renderer import Renderer
from overlays import OverlayManager, ModeSelectOverlay

# ----------------------------- CONTROLS ------------------------------
@dataclass(frozen=True)
class Controls:
    left: int
    right: int
    down: int
    rot_cw: int
    rot_ccw: int
    hard_drop: int

ARROWS = Controls(
    left=pygame.K_LEFT, right=pygame.K_RIGHT, down=pygame.K_DOWN,
    rot_cw=pygame.K_UP, rot_ccw=pygame.K_z, hard_drop=pygame.K_SPACE
)
WASD = Controls(
    left=pygame.K_a, right=pygame.K_d, down=pygame.K_s,
    rot_cw=pygame.K_w, rot_ccw=pygame.K_q, hard_drop=pygame.K_f
)

# ----------------------------- PLAYER STATE --------------------------
@dataclass
class PlayerState:
    name: str
    controls: Controls
    cols: int
    rows: int
    cell: int
    offset: int = 0

    board: Board = field(init=False)
    bag: SevenBag = field(init=False)
    cur: Optional[Piece] = field(init=False, default=None)

    score: int = 0
    level: int = 0
    lines: int = 0
    fall_ms: int = field(init=False)
    last_fall: int = 0
    alive: bool = True

    # input repeat
    left_held: bool = False
    right_held: bool = False
    down_held: bool = False
    lr_first_time: Dict[str, int] = field(default_factory=lambda: {"left": 0, "right": 0})
    lr_last_repeat: Dict[str, int] = field(default_factory=lambda: {"left": 0, "right": 0})

    def __post_init__(self):
        self.board = Board(self.cols, self.rows)
        self.bag = SevenBag()
        self.fall_ms = CONFIG["BASE_FALL_MS"]
        self.spawn()

    # ---------- per-player helpers ----------
    def spawn(self):
        k = self.bag.next()
        color = COLORS[k]
        p = Piece(k, self.cols // 2, 1, 0, color)
        if not self.board.valid(p):
            self.alive = False
            self.cur = None
        else:
            self.cur = p

    def rotate(self, dr: int):
        if not self.cur or not self.alive:
            return
        if self.cur.kind == "O":
            return
        candidate = self.cur.rotated(dr)
        # naive wall kicks
        for dx in [0, -1, 1, -2, 2]:
            test = Piece(candidate.kind, candidate.x + dx, candidate.y, candidate.rot, candidate.color)
            if self.board.valid(test):
                self.cur = test
                return

    def move(self, dx: int, dy: int) -> bool:
        if not self.cur or not self.alive:
            return False
        test = Piece(self.cur.kind, self.cur.x + dx, self.cur.y + dy, self.cur.rot, self.cur.color)
        if self.board.valid(test):
            self.cur = test
            return True
        return False

    def hard_drop(self):
        if not self.cur or not self.alive:
            return
        dy = self.board.drop_distance(self.cur)
        if dy > 0:
            self.cur.y += dy
        self.lock()

    def lock(self):
        if not self.cur or not self.alive:
            return
        cleared = self.board.lock(self.cur)
        if cleared:
            self.lines += cleared
            self.score += SCORES.get(cleared, 0) * (self.level + 1)
            new_level = self.lines // 10
            if new_level != self.level:
                self.level = new_level
                self.fall_ms = max(60, int(CONFIG["BASE_FALL_MS"] * (CONFIG["LVL_ACCEL"] ** self.level)))
        self.spawn()

    def handle_lr_auto(self, now_ms: int):
        if not self.alive:
            return
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
            moved = self.move(dx, 0)
            self.lr_last_repeat[side] = now_ms if moved else now_ms

# ----------------------------- GAME ----------------------------------
class Tetris:
    def __init__(self):
        self.cols, self.rows, self.cell = CONFIG["COLS"], CONFIG["ROWS"], CONFIG["CELL"]
        # layout: [margin] board P1 [margin] board P2 [margin]
        self.margin_px = self.cell * 2
        total_board_w = self.cols * self.cell
        self.width = total_board_w * 2 + self.margin_px * 3
        self.height = self.rows * self.cell

        pygame.init()
        pygame.display.set_caption("Pygame Tetris — Two Player")
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen, self.cell)
        # --- overlays ---
        self.ui = OverlayManager()
        # fonts for overlay (reuse renderer fonts if you prefer)
        self.big = pygame.font.SysFont("Inter, Menlo, Consolas, Arial", 28, bold=True)
        self.small = pygame.font.SysFont("Inter, Menlo, Consolas, Arial", 18)
        self.ui.push(ModeSelectOverlay(self.big, self.small))

        # build players with offsets
        offsets = [
            self.margin_px,
            self.margin_px + total_board_w + self.margin_px,
        ]
        self.players: List[PlayerState] = [
            PlayerState("P1", controls=ARROWS, cols=self.cols, rows=self.rows, cell=self.cell, offset=offsets[0]),
            PlayerState("P2", controls=WASD, cols=self.cols, rows=self.rows, cell=self.cell, offset=offsets[1]),
        ]

        self.paused = False
        self.game_over = False

    # ----------------------- input handling -----------------
    def _handle_keydown(self, e: pygame.event.Event):

        # first give the overlay a chance
        res = self.ui.handle_event(e)
        if res and getattr(res, "done", False):
            # apply selection
            n = res.payload.get("players", 2)
            if n == 1:
                # keep P1, disable P2
                self.players[1].alive = False
                # optionally gray out P2 board or leave it empty
            else:
                # ensure both enabled and (optionally) reset
                for p in self.players:
                    if not p.alive:
                        p.alive = True
                        p.spawn()
            return  # overlay absorbed input

        # if overlay is active & modal, block gameplay input
        if self.ui.is_modal():
            return


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

        # route to owning player by controls
        for p in self.players:
            c = p.controls
            if e.key == c.rot_cw:
                p.rotate(1); return
            if e.key == c.rot_ccw:
                p.rotate(-1); return
            if e.key == c.hard_drop:
                p.hard_drop(); return
            if e.key == c.left:
                p.left_held = True
                p.lr_first_time["left"] = pygame.time.get_ticks()
                p.lr_last_repeat["left"] = 0
                p.move(-1, 0); return
            if e.key == c.right:
                p.right_held = True
                p.lr_first_time["right"] = pygame.time.get_ticks()
                p.lr_last_repeat["right"] = 0
                p.move(1, 0); return
            if e.key == c.down:
                p.down_held = True
                p.move(0, 1); return

    def _handle_keyup(self, e: pygame.event.Event):
        if self.ui.is_modal():  # block gameplay keyups while modal
            return
        
        for p in self.players:
            c = p.controls
            if e.key == c.left:
                p.left_held = False
            elif e.key == c.right:
                p.right_held = False
            elif e.key == c.down:
                p.down_held = False

    # ----------------------- update & draw -------------------
    def update(self, dt_ms: int):

        # let overlay animate (e.g., blinking, timers)
        self.ui.update(dt_ms)

        if self.paused or self.game_over or self.ui.is_modal():
            return

        if self.paused or self.game_over:
            return
        now = pygame.time.get_ticks()

        alive_count = 0
        for p in self.players:
            if not p.alive:
                continue
            alive_count += 1
            p.handle_lr_auto(now)
            if p.down_held:
                if now - p.last_fall > max(40, p.fall_ms // 15):
                    if not p.move(0, 1):
                        p.lock()
                    p.last_fall = now
            else:
                if now - p.last_fall > p.fall_ms:
                    if not p.move(0, 1):
                        p.lock()
                    p.last_fall = now

        if alive_count == 0:
            self.game_over = True

    def draw(self):
        # clear background once
        self.screen.fill(COLORS["bg"])
        # per player board, piece, ghost, HUD
        for p in self.players:
            # board
            self.renderer.draw_board(p.board, p.offset)
            # dynamic pieces
            if p.alive and p.cur:
                self.renderer.draw_ghost(p.cur, p.board, p.offset)
                self.renderer.draw_piece(p.cur, p.offset)
            # HUD near top-left of each board
            self.renderer.hud(
                name=p.name, score=p.score, level=p.level, lines=p.lines,
                paused=self.paused, game_over=not p.alive,
                offset_x=p.offset
            )

        # overall game over message centered
        if self.game_over:
            self.renderer.center_text("MATCH OVER — Press R to restart")

        # --- draw overlay on top ---
        self.ui.draw(self.screen)

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
