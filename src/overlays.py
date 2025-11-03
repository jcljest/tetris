# overlays.py
from dataclasses import dataclass
import pygame

@dataclass
class OverlayResult:
    done: bool = False
    payload: dict = None

class Overlay:
    modal: bool = True  # block gameplay input/updates while shown
    def update(self, dt_ms: int): ...
    def draw(self, screen: pygame.Surface): ...
    def handle_event(self, e: pygame.event.Event) -> OverlayResult | None: ...

class ModeSelectOverlay(Overlay):
    def __init__(self, big_font: pygame.font.Font, small_font: pygame.font.Font):
        self.big = big_font
        self.small = small_font
        self.items = [("Single Player", {"players": 1}),
                      ("Two Player",    {"players": 2})]
        self.index = 0

    def update(self, dt_ms: int): pass

    def draw(self, screen: pygame.Surface):
        w, h = screen.get_size()
        # dim background
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill((0,0,0,160))
        screen.blit(s, (0,0))

        title = self.big.render("Select Mode", True, (240,240,240))
        screen.blit(title, title.get_rect(center=(w//2, h//2 - 80)))

        y = h//2 - 10
        for i, (label, _) in enumerate(self.items):
            txt = f"> {label} <" if i == self.index else label
            surf = self.small.render(txt, True, (255,255,255) if i==self.index else (200,200,200))
            screen.blit(surf, surf.get_rect(center=(w//2, y)))
            y += 36

        hint = self.small.render("↑/↓ to move • Enter to confirm", True, (210,210,210))
        screen.blit(hint, hint.get_rect(center=(w//2, h//2 + 110)))

    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                self.index = (self.index - 1) % len(self.items)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.index = (self.index + 1) % len(self.items)
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return OverlayResult(done=True, payload=self.items[self.index][1])
        return None
    

class OverlayManager:
    def __init__(self):
        self.stack: list[Overlay] = []

    def push(self, ov: Overlay): self.stack.append(ov)
    def pop(self): 
        if self.stack: self.stack.pop()
    def top(self) -> Overlay | None:
        return self.stack[-1] if self.stack else None

    def handle_event(self, e):
        if not self.stack: return None
        res = self.stack[-1].handle_event(e)
        if isinstance(res, OverlayResult) and res.done:
            self.pop()
        return res

    def update(self, dt_ms: int):
        if self.stack: self.stack[-1].update(dt_ms)

    def draw(self, screen):
        if self.stack: self.stack[-1].draw(screen)

    def is_modal(self) -> bool:
        return bool(self.stack and self.stack[-1].modal)