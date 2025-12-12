
from __future__ import annotations
import sys
from .sound_manager import SoundManager
from .bag import SevenBag
from .board import Board
from .config import COLORS, SCORES, SHAPES, CONFIG
from .input_manager import InputManager
from .piece import Piece
from .renderer import Renderer
import pygame

class Tetris:
    def __init__(self):
        self.cols, self.rows, self.cell = CONFIG["COLS"], CONFIG["ROWS"], CONFIG["CELL"]
        self.width, self.height = self.cols * self.cell, self.rows * self.cell
        pygame.init()
        pygame.display.set_caption("Pygame Tetris")
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen, self.cell)
        self.sounds = SoundManager("assets", sounds={"ping": "ping.mp3"})

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

        self.inputs = InputManager(
            CONFIG,
            on_move=self._move,
            on_rotate=self._rotate,
            on_hard_drop=self._hard_drop,
            on_toggle_pause=self.toggle_pause,
            on_restart=self.restart,
            on_quit=self.quit,
            is_paused=lambda: self.paused,
            is_game_over=lambda: self.game_over,
        )

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
        self.sounds.play("ping")
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
    def toggle_pause(self):
        self.paused = not self.paused

    def restart(self):
        self.__init__()

    def quit(self):
        pygame.quit(); sys.exit(0)

    # ----------------------- update & draw -------------------
    def update(self, dt_ms: int):
        if self.paused or self.game_over:
            return
        now = pygame.time.get_ticks()
        self.inputs.update(now)
        if self.inputs.soft_drop_active:
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
                    self.quit()
                else:
                    self.inputs.handle_event(e)
            self.update(dt)
            self.draw()
