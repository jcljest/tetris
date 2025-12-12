import math
import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Union
from .board import Board

import pygame
from .config import COLORS
from .piece import Piece

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

    def _cell(self, x: int, y: int, color: Tuple[int,int,int], alpha: Union[int,None]=None):
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