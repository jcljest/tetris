# core/config.py
"""
Central configuration for base game parameters.
This separates runtime wiring (App) from numeric/game constants.
"""

CONFIG = {
    # Geometry
    "COLS": 10,
    "ROWS": 22,
    "CELL": 24,       # pixels per cell
    "MARGIN": 12,

    # Timing
    "FPS": 60,
    "BASE_FALL_MS": 800,
    "LVL_ACCEL": 0.9,  # 10% faster each level
    "MIN_FALL_MS": 60,

    # Input (Delayed Auto Shift / Auto Repeat Rate)
    "DAS_MS": 160,
    "ARR_MS": 40,
}


# colors (default palette)
COLORS = {
    "bg": (16, 18, 20),
    "grid": (32, 36, 40),
    "ghost": (85, 85, 85),
    "text": (230, 238, 245),
    "I": (80, 227, 230),
    "J": (36, 95, 223),
    "L": (223, 173, 36),
    "O": (223, 217, 36),
    "S": (80, 230, 123),
    "T": (158, 36, 223),
    "Z": (230, 80, 80),
}
