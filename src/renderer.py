
import pygame
from typing import Tuple, Union
from board import Board
from config import COLORS
from piece import Piece

class Renderer:
    def __init__(self, screen: pygame.Surface, cell: int):
        self.screen = screen
        self.cell = cell
        self.font = pygame.font.SysFont("Inter, Menlo, Consolas, Arial", 18)
        self.big = pygame.font.SysFont("Inter, Menlo, Consolas, Arial", 28, bold=True)

    # All drawing supports an x-offset so we can place two boards side-by-side
    def draw_board(self, board: Board, offset_x: int = 0):
        w, h = board.cols * self.cell, board.rows * self.cell
        # board background panel
        pygame.draw.rect(self.screen, COLORS["bg"], (offset_x, 0, w, h))
        # grid lines
        for x in range(board.cols + 1):
            pygame.draw.line(self.screen, COLORS["grid"],
                             (offset_x + x * self.cell, 0),
                             (offset_x + x * self.cell, h))
        for y in range(board.rows + 1):
            pygame.draw.line(self.screen, COLORS["grid"],
                             (offset_x, y * self.cell),
                             (offset_x + w, y * self.cell))
        # locked blocks
        for y in range(board.rows):
            for x in range(board.cols):
                c = board.grid[y][x]
                if c is not None:
                    self._cell(x, y, c, None, offset_x)

    def _cell(self, x: int, y: int, color: Tuple[int,int,int], alpha: Union[int,None]=None, offset_x: int = 0):
        r = pygame.Rect(offset_x + x * self.cell, y * self.cell, self.cell, self.cell)
        pygame.draw.rect(self.screen, color, r)
        pygame.draw.rect(self.screen, (0,0,0), r, 2)

    def draw_piece(self, piece: Piece, offset_x: int = 0):
        for (x, y) in piece.blocks():
            self._cell(x, y, piece.color, None, offset_x)

    def draw_ghost(self, piece: Piece, board: Board, offset_x: int = 0):
        dy = board.drop_distance(piece)
        ghost = Piece(piece.kind, piece.x, piece.y + dy, piece.rot, COLORS["ghost"])
        for (x, y) in ghost.blocks():
            r = pygame.Rect(offset_x + x * self.cell + 4, y * self.cell + 4, self.cell - 8, self.cell - 8)
            pygame.draw.rect(self.screen, COLORS["ghost"], r, 2)

    def hud(self, name: str, score: int, level: int, lines: int, paused: bool, game_over: bool, offset_x: int = 0):
        texts = [
            f"{name}",
            f"Score: {score}",
            f"Level: {level}",
            f"Lines: {lines}",
        ]
        if paused:
            texts.append("PAUSED (P)")
        if game_over:
            texts.append("TOPPED OUT")
        y = 8
        for t in texts:
            surf = self.font.render(t, True, COLORS["text"])
            self.screen.blit(surf, (offset_x + 8, y))
            y += surf.get_height() + 4

    def center_text(self, msg: str):
        surf = self.big.render(msg, True, COLORS["text"])
        r = surf.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(surf, r)
