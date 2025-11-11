# render/painters.py
from __future__ import annotations
import pygame
from typing import Optional, Tuple, Iterable

from .theme import Theme
from core.board import BoardProtocol   # must expose BoardProtocol

RGB = Tuple[int, int, int]

class BoardPainter:
    def __init__(self, theme: Theme, cell: int = 24, margin: int = 12):
        self.theme = theme
        self.cell = cell
        self.margin = margin

    def draw(self, screen: pygame.Surface, board: BoardProtocol) -> None:
        bg = self.theme.bg_color
        grid = self.theme.grid_color
        cell = self.cell
        m = self.margin
        w = board.cols * cell
        h = board.rows * cell

        # background
        pygame.draw.rect(screen, bg, pygame.Rect(m, m, w, h))

        # grid
        for x in range(board.cols + 1):
            X = m + x * cell
            pygame.draw.line(screen, grid, (X, m), (X, m + h), 1)
        for y in range(board.rows + 1):
            Y = m + y * cell
            pygame.draw.line(screen, grid, (m, Y), (m + w, Y), 1)

        # locked cells
        for y in range(board.rows):
            for x in range(board.cols):
                c: Optional[RGB] = board.cell(x, y)  # BoardProtocol should provide this
                if c:
                    rect = pygame.Rect(m + x*cell + 1, m + y*cell + 1, cell-2, cell-2)
                    pygame.draw.rect(screen, c, rect)

class PiecePainter:
    def __init__(self, theme: Theme, cell: int = 24, margin: int = 12):
        self.theme = theme
        self.cell = cell
        self.margin = margin

    def _draw_blocks(self, screen: pygame.Surface, blocks: Iterable[Tuple[int,int]], color: RGB) -> None:
        cell = self.cell; m = self.margin
        for (x, y) in blocks:
            rect = pygame.Rect(m + x*cell + 1, m + y*cell + 1, cell-2, cell-2)
            pygame.draw.rect(screen, color, rect)

    def draw_current(self, screen: pygame.Surface, piece) -> None:
        # piece must expose .blocks (list of (x,y)) and .color
        self._draw_blocks(screen, piece.blocks, piece.color)

    def draw_ghost(self, screen: pygame.Surface, piece, board: BoardProtocol) -> None:
        # piece.blocks must be absolute coords; compute ghost with board.drop_distance
        dy = board.drop_distance(piece)
        ghost_blocks = [(x, y + dy) for (x, y) in piece.blocks]
        self._draw_blocks(screen, ghost_blocks, (150, 150, 150))

class HudPainter:
    def __init__(self, theme: Theme, origin_px=(320, 16)):
        self.theme = theme
        self.origin = origin_px

    def draw(self, screen: pygame.Surface, score: int, level: int, lines: int, paused: bool, over: bool) -> None:
        font = self.theme.get_small_font()
        big = self.theme.get_big_font()
        x, y = self.origin
        text = f"Score {score}  Level {level}  Lines {lines}"
        if paused: text += "  [PAUSED]"
        if over:   text += "  [GAME OVER]"
        surf = font.render(text, True, self.theme.palette["text"])
        screen.blit(surf, (x, y))
        if over:
            g = big.render("Press R to restart", True, self.theme.palette["text"])
            screen.blit(g, (x, y + 28))
