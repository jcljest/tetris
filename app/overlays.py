# app/overlays.py
from __future__ import annotations
from typing import Protocol, Dict, List, Optional, Tuple
import pygame

class Overlay(Protocol):
    id: str
    def handle_event(self, e: pygame.event.Event) -> bool: ...
    def draw(self, screen: pygame.Surface) -> None: ...

class OverlayHost:
    """Simple overlay stack; top-most overlay handles input and draws."""
    def __init__(self, registry: Dict[str, Overlay]):
        self._stack: List[Overlay] = []
        self._registry = registry

    @property
    def active(self) -> bool:
        return len(self._stack) > 0

    def push(self, overlay_id: str):
        self._stack.append(self._registry[overlay_id])

    def pop(self):
        if self._stack:
            self._stack.pop()

    def clear(self):
        self._stack.clear()

    def handle_event(self, e: pygame.event.Event) -> bool:
        if not self._stack:
            return False
        return self._stack[-1].handle_event(e)

    def draw(self, screen: pygame.Surface) -> None:
        for ov in self._stack:
            ov.draw(screen)


# --- Concrete overlays ---

def _dim(screen: pygame.Surface, alpha: int = 140):
    w, h = screen.get_size()
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    screen.blit(s, (0, 0))

class PauseOverlay:
    id = "pause"
    def __init__(self, font_small: pygame.font.Font, font_big: pygame.font.Font):
        self.font_small = font_small
        self.font_big = font_big

    def handle_event(self, e: pygame.event.Event) -> bool:
        # Let App decide to toggle pause; we only swallow inputs while active
        return True  # consume all events while paused

    def draw(self, screen: pygame.Surface) -> None:
        _dim(screen, 150)
        msg1 = self.big("PAUSED")
        msg2 = self.small("Press P to resume")
        self.center(screen, msg1, dy=-20)
        self.center(screen, msg2, dy=20)

    # helpers
    def small(self, text): return self.font_small.render(text, True, (240,240,240))
    def big(self, text):   return self.font_big.render(text, True, (240,240,240))
    def center(self, screen, surf, dy=0):
        r = surf.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + dy))
        screen.blit(surf, r)

class GameOverOverlay:
    id = "game_over"
    def __init__(self, font_small: pygame.font.Font, font_big: pygame.font.Font, on_restart):
        self.font_small = font_small
        self.font_big = font_big
        self.on_restart = on_restart  # callback to App.reset_game

    def handle_event(self, e: pygame.event.Event) -> bool:
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_r:
                self.on_restart()
                return True
            if e.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return True
        return True  # swallow all

    def draw(self, screen: pygame.Surface) -> None:
        _dim(screen, 180)
        msg1 = self.big("GAME OVER")
        msg2 = self.small("Press R to restart  |  ESC to quit")
        self.center(screen, msg1, dy=-20)
        self.center(screen, msg2, dy=20)

    # helpers
    def small(self, text): return self.font_small.render(text, True, (240,240,240))
    def big(self, text):   return self.font_big.render(text, True, (240,240,240))
    def center(self, screen, surf, dy=0):
        r = surf.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + dy))
        screen.blit(surf, r)
