from __future__ import annotations
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional

import pygame


class SoundManager:
    """
    Small façade around pygame's mixer subsystem. Aims to keep every sound concern
    (initialisation, caching, playback, volume toggling) inside a single module so
    other parts of the game can simply call `sounds.play("line_clear")` without
    knowing how audio assets are managed.
    """

    def __init__(
        self,
        asset_root: str | Path,
        *,
        sounds: Optional[Mapping[str, str]] = None,
        volume: float = 0.4,
        enabled: bool = True,
    ):
        """
        Parameters
        ----------
        asset_root:
            Folder where sound files live relative to the project.
        sounds:
            Optional mapping of logical names to filenames (within asset_root).
        volume:
            Default mixer volume for each loaded clip (0.0 - 1.0).
        enabled:
            Allows the entire audio layer to be toggled off (for headless runs).
        """
        self.asset_root = Path(asset_root)
        self.enabled = enabled
        self._volume = max(0.0, min(1.0, volume))
        self._cache: Dict[str, pygame.mixer.Sound] = {}

        # Mixer init is idempotent; guard to avoid throwing if already initialised.
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        if sounds:
            self.load_many(sounds.items())

    def load(self, name: str, filename: str):
        """Load a single sound asset into the cache."""
        sound = pygame.mixer.Sound((self.asset_root / filename).as_posix())
        sound.set_volume(self._volume)
        self._cache[name] = sound

    def load_many(self, items: Iterable[tuple[str, str]]):
        for name, filename in items:
            self.load(name, filename)

    def set_volume(self, volume: float):
        """Update volume for future loads and currently cached sounds."""
        self._volume = max(0.0, min(1.0, volume))
        for snd in self._cache.values():
            snd.set_volume(self._volume)

    def mute(self):
        self.enabled = False

    def unmute(self):
        self.enabled = True

    def toggle(self):
        self.enabled = not self.enabled

    def play(self, name: str):
        """Play a cached sound by logical name."""
        if not self.enabled:
            return
        sound = self._cache.get(name)
        if sound:
            sound.play()

    def stop(self, name: str):
        if name in self._cache:
            self._cache[name].stop()

    def stop_all(self):
        pygame.mixer.stop()
