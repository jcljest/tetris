CONFIG = {
    "COLS": 10,
    "ROWS": 20,
    "CELL": 32,  # pixel size of one cell
    "FPS": 60,
    # Gravity timing in milliseconds at level 0. Gets faster with level.
    "BASE_FALL_MS": 800,
    # Each level reduces the fall time by this percentage (clamped)
    "LVL_ACCEL": 0.9,  # 10% faster each level
    # DAS (delayed auto shift) and ARR (auto repeat rate) in ms for LR keys
    "DAS_MS": 160,
    "ARR_MS": 40,
}

# NES-like scoring (scaled by (level+1))
SCORES = {1: 40, 2: 100, 3: 300, 4: 1200}

# Colors (RGB)
COLORS = {
    "bg": (16, 18, 20),
    "grid": (32, 36, 40),
    "ghost": (85, 85, 85),
    "text": (230, 238, 245),
    # Tetromino colors
    "I": (80, 227, 230),
    "J": (36, 95, 223),
    "L": (223, 173, 36),
    "O": (223, 217, 36),
    "S": (80, 230, 123),
    "T": (158, 36, 223),
    "Z": (230, 80, 80),
}

# Tetromino shape definitions via rotation states as (x,y) offsets
# Each piece is defined around a reference (piece.x, piece.y) in grid coords.
# Rotation system: simple 4-state with naive wall kicks [-1, 1, -2, 2]
SHAPES = {
    "I": [
        [( -1, 0), (0, 0), (1, 0), (2, 0)],
        [( 1, -1), (1, 0), (1, 1), (1, 2)],
        [(-1, 1), (0, 1), (1, 1), (2, 1)],
        [( 0, -1), (0, 0), (0, 1), (0, 2)],
    ],
    "J": [
        [(-1, 0), (0, 0), (1, 0), (-1, 1)],
        [(0, -1), (0, 0), (0, 1), (1, -1)],
        [(-1, 0), (0, 0), (1, 0), (1, -1)],
        [(0, -1), (0, 0), (0, 1), (-1, 1)],
    ],
    "L": [
        [(-1, 0), (0, 0), (1, 0), (1, 1)],
        [(0, -1), (0, 0), (0, 1), (1, 1)],
        [(-1, -1), (-1, 0), (0, 0), (1, 0)],
        [(-1, -1), (0, -1), (0, 0), (0, 1)],
    ],
    "O": [
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
    ],
    "S": [
        [(-1, 1), (0, 1), (0, 0), (1, 0)],
        [(0, -1), (0, 0), (1, 0), (1, 1)],
        [(-1, 1), (0, 1), (0, 0), (1, 0)],
        [(0, -1), (0, 0), (1, 0), (1, 1)],
    ],
    "T": [
        [(-1, 0), (0, 0), (1, 0), (0, 1)],
        [(0, -1), (0, 0), (0, 1), (1, 0)],
        [(-1, 0), (0, 0), (1, 0), (0, -1)],
        [(0, -1), (0, 0), (0, 1), (-1, 0)],
    ],
    "Z": [
        [(-1, 0), (0, 0), (0, 1), (1, 1)],
        [(1, -1), (1, 0), (0, 0), (0, 1)],
        [(-1, 0), (0, 0), (0, 1), (1, 1)],
        [(1, -1), (1, 0), (0, 0), (0, 1)],
    ],
}

