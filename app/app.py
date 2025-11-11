# app/app.py
from __future__ import annotations
import pygame

from mods.loader import load_manifest
from render.renderer import Renderer
from render.painters import BoardPainter, PiecePainter, HudPainter
from render.theme_default import DefaultTheme

from core.board_rect import RectBoard
from core.rules_default import DefaultRuleSet
from core.shapes import SrsShapeSet
from core.bag import SevenBag
from core.controller import PieceController
from core.progression import ProgressionTracker
from core.repeater import InputRepeater
from core.config import CONFIG
from core.match import Match

from app.overlays import OverlayHost, PauseOverlay, GameOverOverlay


class App:
    def __init__(self, manifest_path=None):
        pygame.init()

        # --- Config ---
        self.cols   = CONFIG["COLS"]
        self.rows   = CONFIG["ROWS"]
        self.cell   = CONFIG["CELL"]
        self.margin = CONFIG["MARGIN"]

        # --- Timing ---
        self.clock = pygame.time.Clock()
        self.fps = CONFIG.get("FPS", 60)

        # --- Screen ---
        self.screen = pygame.display.set_mode((self.cols*self.cell, self.rows*self.cell))
        pygame.display.set_caption("Moddable Tetris")

        # --- Theme & Mods ---
        self.theme = DefaultTheme()
        mods = load_manifest(manifest_path) if manifest_path else {}
        self.rules  = mods.get("rules",  DefaultRuleSet())
        self.shapes = mods.get("shapes", SrsShapeSet())
        self.bag    = mods.get("bag", SevenBag(self.shapes))

        # --- Core services ---
        self.board      = RectBoard(self.cols, self.rows)
        self.controller = PieceController(self.board, self.rules, self.shapes)
        self.prog       = ProgressionTracker()
        self.repeater   = InputRepeater(das_ms=CONFIG["DAS_MS"], arr_ms=CONFIG["ARR_MS"])

        # --- Renderer ---
        self.renderer = Renderer(
            self.theme,
            BoardPainter(self.theme, self.cell),
            PiecePainter(self.theme, self.cell),
            HudPainter(self.theme)
        )

        # --- Match ---
        self.match = Match(
            board=self.board,
            bag=self.bag,
            shapes=self.shapes,
            rules=self.rules,
            controller=self.controller,
            prog=self.prog,
            color_for_kind=self.theme.color_for_kind
        )

        # --- Fonts for overlays ---
        self.font_small = pygame.font.SysFont("Inter", 18)
        self.font_big   = pygame.font.SysFont("Inter", 36)

        # --- Overlay callbacks wired into Pause/GameOver overlays ---
        def _resume():
            self.overlays.pop("pause")
            if getattr(self.match, "paused", False):
                self.match.toggle_pause()

        def _quit():
            pygame.event.post(pygame.event.Event(pygame.QUIT))

        # --- Overlays ---
        self.overlays = OverlayHost({
            "pause":     PauseOverlay(self.font_small, self.font_big, _resume, _quit),
            "game_over": GameOverOverlay(self.font_small, self.font_big, on_restart=self.reset_game),
        })

    def quit_app(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def reset_game(self):
        # rebuild state
        self.board      = RectBoard(self.cols, self.rows)
        self.controller = PieceController(self.board, self.rules, self.shapes)
        self.prog       = ProgressionTracker()
        self.match = Match(
            board=self.board,
            bag=self.bag,
            shapes=self.shapes,
            rules=self.rules,
            controller=self.controller,
            prog=self.prog,
            color_for_kind=self.theme.color_for_kind
        )
        # clear overlays if any
        self.overlays.clear()

    def run(self):
        running = True
        while running:
            dt_ms = self.clock.tick(self.fps)
            now_ms = pygame.time.get_ticks()

            # -------- events --------
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                    continue

                # overlays get first chance
                if self.overlays.active and self.overlays.handle_event(e):
                    continue

                # pause toggle
                if e.type == pygame.KEYDOWN and e.key in (pygame.K_p, pygame.K_ESCAPE):
                    if self.overlays.has("pause"):
                        self.overlays.pop("pause")
                    else:
                        self.overlays.push("pause")
                    if hasattr(self.match, "toggle_pause"):
                        self.match.toggle_pause()
                    continue

                # basic controls (adapt to your input router if you have one)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_LEFT:  self.match.move_left()
                    if e.key == pygame.K_RIGHT: self.match.move_right()
                    if e.key == pygame.K_DOWN:  self.match.soft_drop_step()
                    if e.key == pygame.K_UP:    self.match.rotate_cw()
                    if e.key == pygame.K_z:     self.match.rotate_ccw()
                    if e.key == pygame.K_SPACE: self.match.hard_drop()

            # -------- update --------
            if hasattr(self.repeater, "update"):
                self.repeater.update(dt_ms)
            if hasattr(self.match, "update"):
                self.match.update(now_ms)
            elif hasattr(self.match, "tick"):
                self.match.tick()

            # trigger game over overlay once
            if getattr(self.match, "game_over", False) and not self.overlays.top_is("game_over"):
                self.overlays.push("game_over")

            # -------- draw --------
            pv = self.match.piece_view() if hasattr(self.match, "piece_view") else None
            self.renderer.draw(
                self.screen,
                self.board,
                pv,
                self.prog.score,
                self.prog.level,
                self.prog.lines,
                getattr(self.match, "paused", False),
                getattr(self.match, "game_over", False),
            )

            # overlays last
            self.overlays.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
