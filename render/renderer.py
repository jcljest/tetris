# render/renderer.py
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .theme_default import DefaultTheme as Theme

from .theme_default import DefaultTheme as Theme
from .painters import BoardPainter, PiecePainter, HudPainter

class Renderer:
    def __init__(self, theme: Theme, board_p: BoardPainter, piece_p: PiecePainter, hud_p: HudPainter):
        self.theme, self.bp, self.pp, self.hudp = theme, board_p, piece_p, hud_p
    
    
    
    def draw(self, screen, board, cur_piece, score, level, lines, paused, over):
        self.bp.draw(screen, board)
        if not over and cur_piece is not None:
            self.pp.draw_ghost(screen, cur_piece, board)
            self.pp.draw_current(screen, cur_piece)
        self.hudp.draw(screen, score, level, lines, paused, over)