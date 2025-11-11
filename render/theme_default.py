# render/theme_default.py
from typing import Mapping, Tuple, Any, Dict

RGB = Tuple[int, int, int]

class DefaultTheme:
    """
    Concrete Theme with a neutral palette and lazy font creation.
    Works even if pygame isn't imported at construction time.
    """
    palette: Mapping[str, RGB]
    font_small: Any
    font_big: Any
    grid_color: RGB
    bg_color: RGB

    def __init__(self, auto_fonts: bool = True, small_px: int = 16, big_px: int = 28) -> None:
        self.palette = {
            "bg":      (18, 18, 22),
            "grid":    (40, 40, 48),
            "ghost":   (120, 120, 120),
            "text":    (235, 235, 245),

            # Guideline-ish colors (tweak freely)
            "I": (0, 255, 255),
            "J": (0, 0, 255),
            "L": (255, 127, 0),
            "O": (255, 255, 0),
            "S": (0, 255, 0),
            "T": (160, 0, 240),
            "Z": (255, 0, 0),

            "empty":  (25, 25, 30),
            "board":  (30, 30, 36),
        }
        self.bg_color = self.palette["bg"]
        self.grid_color = self.palette["grid"]

        # Fonts are set lazily to avoid importing pygame at import time.
        self.font_small = None
        self.font_big = None
        if auto_fonts:
            self.ensure_fonts(small_px, big_px)

    def ensure_fonts(self, small_px: int = 16, big_px: int = 28) -> None:
        """Create default pygame fonts if available and not yet created."""
        try:
            import pygame
            if self.font_small is None:
                self.font_small = pygame.font.SysFont(None, small_px)
            if self.font_big is None:
                self.font_big = pygame.font.SysFont(None, big_px, bold=True)
        except Exception:
            # Keep fonts as None if pygame/font not ready; caller may inject later.
            pass

    # Convenience accessors that won't crash if fonts are missing:
    def get_small_font(self):
        if self.font_small is None:
            self.ensure_fonts()
        return self.font_small

    def get_big_font(self):
        if self.font_big is None:
            self.ensure_fonts()
        return self.font_big

    # Optional: help a painter pick piece color by kind
    def color_for_kind(self, kind: str) -> RGB:
        return self.palette.get(kind, (200, 200, 200))
