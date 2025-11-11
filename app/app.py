# app/app.py
from __future__ import annotations
import pygame

# --- imports you need in the composition root ---
from mods.loader import load_manifest

from render.renderer import Renderer
from render.painters import BoardPainter, PiecePainter, HudPainter
from render.theme_default import DefaultTheme  # concrete theme

from core.board_rect import RectBoard          # concrete board
from core.rules_default import DefaultRuleSet  # concrete rules
from core.shapes import SrsShapeSet            # concrete shapes
from core.bag import SevenBag                  # concrete piece generator
from core.controller import PieceController
from core.progression import ProgressionTracker
from core.repeater import InputRepeater
from core.config import CONFIG

from core.match import Match
from app.overlays import OverlayHost, PauseOverlay, GameOverOverlay

class App:
    def __init__(self, manifest_path=None):
        pygame.init()

        # Config
        self.cols   = CONFIG["COLS"]
        self.rows   = CONFIG["ROWS"]
        self.cell   = CONFIG["CELL"]
        self.margin = CONFIG["MARGIN"]

        # Screen
        self.screen = pygame.display.set_mode((self.cols*self.cell, self.rows*self.cell))
        pygame.display.set_caption("Moddable Tetris")

        # Theme (could come from manifest)
        self.theme = DefaultTheme()

        # Load mod manifest if available
        mods = load_manifest(manifest_path) if manifest_path else {}
        self.rules  = mods.get("rules",  DefaultRuleSet())
        self.shapes = mods.get("shapes", SrsShapeSet())
        self.bag = mods.get("bag", SevenBag(self.shapes))


        # Core game services
        self.board      = RectBoard(self.cols, self.rows)
        self.controller = PieceController(self.board, self.rules, self.shapes)
        self.prog       = ProgressionTracker()
        self.repeater   = InputRepeater(das_ms=CONFIG["DAS_MS"], arr_ms=CONFIG["ARR_MS"])

        # Renderer
        self.renderer = Renderer(
            self.theme,
            BoardPainter(self.theme, self.cell),
            PiecePainter(self.theme, self.cell),
            HudPainter(self.theme)
        )

        # Match (the game state machine)
        self.match = Match(
            board=self.board,
            bag=self.bag,
            shapes=self.shapes,
            rules=self.rules,
            controller=self.controller,
            prog=self.prog,
            color_for_kind=self.theme.color_for_kind  # gives nice colors
        )

        self.clock = pygame.time.Clock()

    def reset_game(self):
        # rebuild core services that hold state
        self.board      = RectBoard(self.cols, self.rows)
        self.controller = PieceController(self.board, self.rules, self.shapes)
        self.prog       = ProgressionTracker()
        # keep same repeater timing
        self.match = Match(
            board=self.board,
            bag=self.bag,
            shapes=self.shapes,
            rules=self.rules,
            controller=self.controller,
            prog=self.prog,
            color_for_kind=self.theme.color_for_kind
        )
        # clear overlays (e.g., came from Game Over)
        self.overlays.clear()


    def run(self):
        running = True
        while running:
            now = pygame.time.get_ticks()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_LEFT:  self.match.move_left()
                    if e.key == pygame.K_RIGHT: self.match.move_right()
                    if e.key == pygame.K_DOWN:  self.match.soft_drop_step()
                    if e.key == pygame.K_UP:    self.match.rotate_cw()
                    if e.key == pygame.K_z:     self.match.rotate_ccw()
                    if e.key == pygame.K_SPACE: self.match.hard_drop()
                    if e.key == pygame.K_p:     self.match.toggle_pause()

            self.match.update(now)
            pv = self.match.piece_view()
            ghost = self.match.ghost_blocks()

            self.renderer.draw(
                self.screen,
                self.board,
                pv, ghost,
                score=self.prog.score,
                level=self.prog.level,
                lines=self.prog.lines,
                paused=self.match.paused,
                game_over=self.match.game_over
            )

            self.clock.tick(CONFIG["FPS"])
        pygame.quit()
        