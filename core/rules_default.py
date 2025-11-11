# core/rules_default.py
from .rules import RuleSet

class DefaultRuleSet(RuleSet):
    def __init__(self, base_fall_ms=800, accel=0.9, min_ms=60):
        self.base = base_fall_ms; self.accel = accel; self.min = min_ms
        self._scores = {1: 40, 2: 100, 3: 300, 4: 1200}
    def score(self, cleared_lines, level): 
        return self._scores.get(cleared_lines, 0) * (level + 1)
    def fall_interval_ms(self, level):
        from math import pow
        return max(self.min, int(self.base * pow(self.accel, level)))
    def lock_delay_ms(self, level): 
        return 500  # placeholder; keep existing behavior (no explicit lock delay)
    def kick_table(self, kind, fr, to):
        # mirrors your naive kicks [0,-1,1,-2,2]
        return [0, -1, 1, -2, 2]
