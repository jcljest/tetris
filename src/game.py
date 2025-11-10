
from __future__ import annotations
import math
import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple
from bag import SevenBag
from board import Board
from config import COLORS, SCORES, SHAPES, CONFIG
from piece import Piece
from renderer import Renderer

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
            self._rotate(-1)
        elif e.key == pygame.K_z:
            self._rotate(1)
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