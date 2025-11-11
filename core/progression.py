# core/progression.py
class ProgressionTracker:
    def __init__(self): self.score = 0; self.level = 0; self.lines = 0
    def on_lines_cleared(self, n, rules: RuleSet):
        if n:
            self.lines += n
            self.score += rules.score(n, self.level)
            new_level = self.lines // 10
            leveled = new_level != self.level
            self.level = new_level
            return leveled
        return False
