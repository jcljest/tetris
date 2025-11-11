# core/progression.py
from __future__ import annotations
from typing import TYPE_CHECKING

# type-only imports to avoid circular dependencies
if TYPE_CHECKING:
    from core.rules import RuleSet


class ProgressionTracker:
    """Tracks score, level, and lines cleared."""

    def __init__(self):
        self.score = 0
        self.level = 0
        self.lines = 0

    def on_lines_cleared(self, n: int, rules: "RuleSet") -> bool:
        """
        Called after lines are cleared.
        Updates score, line total, and level.
        Returns True if level increased.
        """
        if n <= 0:
            return False

        # add score based on ruleset
        self.score += rules.score(n, self.level)

        # increase total cleared lines
        self.lines += n

        # simple level-up rule: +1 every 10 lines
        old_level = self.level
        self.level = self.lines // 10

        return self.level > old_level
