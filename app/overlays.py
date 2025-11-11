# app/overlays.py
from __future__ import annotations
from typing import Protocol, Dict, List, Optional
import pygame

# ---------- Protocol ----------
class Overlay(Protocol):
    id: str
    def handle_event(self, e: pygame.event.Event) -> bool: ...
    def draw(self, screen: pygame.Surface) -> None: ...

# ---------- Host ----------
class OverlayHost:
    """
    Simple overlay stack. The top-most overlay:
      - gets first crack at events (handle_event)
      - draws last (on top)
    Push/pop by key (registered in the ctor).
    """
    def __init__(self, registry: Dict[str, Overlay]):
        self._stack: List[Overlay] = []
        self._registry = registry

    @property
    def active(self) -> bool:
        return len(self._stack) > 0

    def push(self, overlay_id: str) -> None:
        ov = self._registry[overlay_id]
        # avoid duplicates: move to top if already present
        if ov in self._stack:
            self._stack.remove(ov)
        self._stack.append(ov)

    def pop(self, overlay_id: Optional[str] = None) -> None:
        if not self._stack:
            return
        if overlay_id is None:
            self._stack.pop()
            return
        ov = self._registry.get(overlay_id)
        if ov in self._stack:
            self._stack.remove(ov)

    def clear(self) -> None:
        self._stack.clear()

    # queries
    def has(self, overlay_id: str) -> bool:
        ov = self._registry.get(overlay_id)
        return ov in self._stack if ov else False

    def top_is(self, overlay_id: str) -> bool:
        if not self._stack: return False
        return self._stack[-1] is self._registry.get(overlay_id)

    # integration points
    def handle_event(self, e: pygame.event.Event) -> bool:
        if not self._stack:
            return False
        return self._stack[-1].handle_event(e)

    def draw(self, screen: pygame.Surface) -> None:
        for ov in self._stack:
            ov.draw(screen)

# ---------- helpers ----------
def _dim(surface: pygame.Surface, alpha: int = 160) -> None:
    """Darken the screen behind overlays."""
    s = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    surface.blit(s, (0, 0))

# ---------- Concrete Overlays ----------
class PauseOverlay:
    id = "pause"
    def __init__(self, font_small, font_big, on_resume, on_quit):
        self.font_small = font_small
        self.font_big = font_big
        self.on_resume = on_resume
        self.on_quit = on_quit

    def handle_event(self, e: pygame.event.Event) -> bool:
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_RETURN, pygame.K_SPACE):
                self.on_resume()
                return True
            if e.key == pygame.K_q:
                self.on_quit()
                return True
        return True  # swallow everything while paused

    def draw(self, screen: pygame.Surface) -> None:
        _dim(screen, 160)
        title = self.font_big.render("Paused", True, (240, 240, 240))
        hint  = self.font_small.render("ESC/Enter to resume — Q to quit", True, (220, 220, 220))
        self._center(screen, title, dy=-16)
        self._center(screen, hint, dy=18)

    def _center(self, screen, surf, dy=0):
        r = surf.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + dy))
        screen.blit(surf, r)

class GameOverOverlay:
    id = "game_over"
    def __init__(self, font_small, font_big, on_restart):
        self.font_small = font_small
        self.font_big = font_big
        self.on_restart = on_restart  # callback into App.reset_game

    def handle_event(self, e: pygame.event.Event) -> bool:
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                self.on_restart()
                return True
            if e.key in (pygame.K_ESCAPE, pygame.K_q):
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return True
        return True  # swallow all

    def draw(self, screen: pygame.Surface) -> None:
        _dim(screen, 180)
        msg1 = self.font_big.render("GAME OVER", True, (240, 240, 240))
        msg2 = self.font_small.render("R/Enter = Restart   |   ESC/Q = Quit", True, (220, 220, 220))
        self._center(screen, msg1, dy=-20)
        self._center(screen, msg2, dy=20)

    def _center(self, screen, surf, dy=0):
        r = surf.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + dy))
        screen.blit(surf, r)
