from __future__ import annotations
from typing import Callable
import pygame


class InputManager:
    """
    Encapsulates keyboard handling, including DAS/ARR tracking for left/right and
    exposing whether soft drop is active. All piece actions are routed through
    callables supplied by the game so the input layer stays decoupled from game
    state.
    """

    def __init__(
        self,
        config: dict,
        *,
        on_move: Callable[[int, int], bool],
        on_rotate: Callable[[int], None],
        on_hard_drop: Callable[[], None],
        on_toggle_pause: Callable[[], None],
        on_restart: Callable[[], None],
        on_quit: Callable[[], None],
        is_paused: Callable[[], bool],
        is_game_over: Callable[[], bool],
    ):
        self.cfg = config
        self.on_move = on_move
        self.on_rotate = on_rotate
        self.on_hard_drop = on_hard_drop
        self.on_toggle_pause = on_toggle_pause
        self.on_restart = on_restart
        self.on_quit = on_quit
        self.is_paused = is_paused
        self.is_game_over = is_game_over

        self._down_held = False
        self.lr_state = {
            "left": {"held": False, "first": 0, "last_repeat": 0},
            "right": {"held": False, "first": 0, "last_repeat": 0},
        }

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
        elif event.type == pygame.KEYUP:
            self._handle_keyup(event)

    def _handle_keydown(self, e: pygame.event.Event):
        if e.key == pygame.K_ESCAPE:
            self.on_quit()
            return
        if e.key == pygame.K_p:
            self.on_toggle_pause()
            return
        if self.is_game_over():
            if e.key == pygame.K_r:
                self.on_restart()
            return
        if self.is_paused():
            return
        if e.key in (pygame.K_UP, pygame.K_x):
            self.on_rotate(-1)
        elif e.key == pygame.K_z:
            self.on_rotate(1)
        elif e.key == pygame.K_SPACE:
            self.on_hard_drop()
        elif e.key == pygame.K_LEFT:
            self._begin_lr("left")
            self.on_move(-1, 0)
        elif e.key == pygame.K_RIGHT:
            self._begin_lr("right")
            self.on_move(1, 0)
        elif e.key == pygame.K_DOWN:
            self._down_held = True
            self.on_move(0, 1)

    def _handle_keyup(self, e: pygame.event.Event):
        if e.key == pygame.K_LEFT:
            self._end_lr("left")
        elif e.key == pygame.K_RIGHT:
            self._end_lr("right")
        elif e.key == pygame.K_DOWN:
            self._down_held = False

    def _begin_lr(self, side: str):
        now = pygame.time.get_ticks()
        state = self.lr_state[side]
        state["held"] = True
        state["first"] = now
        state["last_repeat"] = 0

    def _end_lr(self, side: str):
        state = self.lr_state[side]
        state["held"] = False

    def update(self, now_ms: int):
        if self.is_paused() or self.is_game_over():
            return
        for side in ("left", "right"):
            state = self.lr_state[side]
            if not state["held"]:
                continue
            if now_ms - state["first"] < self.cfg["DAS_MS"]:
                continue
            last = state["last_repeat"]
            if last and (now_ms - last) < self.cfg["ARR_MS"]:
                continue
            dx = -1 if side == "left" else 1
            moved = self.on_move(dx, 0)
            state["last_repeat"] = now_ms if moved else now_ms

    @property
    def soft_drop_active(self) -> bool:
        return self._down_held
