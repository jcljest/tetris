# app/app.py
import pygame
from mods.loader import load_manifest
from render.renderer import Renderer
from render.painters import BoardPainter, PiecePainter, HudPainter
from render.theme_default import DefaultTheme
from core.board_rect import RectBoard
from core.controller import PieceController
from core.progression import ProgressionTracker
from core.repeater import InputRepeater

class App:
    def __init__(self, manifest_path=None):
        pygame.init()
        # screen bootstrap
        self.screen = pygame.display.set_mode((cols*cell, rows*cell))
        theme = DefaultTheme()  # or from manifest
        # load rules/shapes/bag from manifest or defaults
        mods = load_manifest(manifest_path) if manifest_path else {}
        rules  = mods.get("rules", DefaultRuleSet())
        shapes = mods.get("shapes", SrsShapeSet())
        bag    = mods.get("bag", SevenBag())

        self.board = RectBoard(cols, rows)
        self.controller = PieceController(self.board, rules, shapes)
        self.prog = ProgressionTracker()
        self.repeater = InputRepeater(das_ms=160, arr_ms=40)
        self.renderer = Renderer(theme,
                                 BoardPainter(theme, cell),
                                 PiecePainter(theme, cell),
                                 HudPainter(theme))

        # Match owns current piece, spawn, game over
        self.match = Match(bag, shapes)

    def run(self):
        # loop: poll input → repeater → controller → progression → render
        ...
