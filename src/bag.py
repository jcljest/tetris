from __future__ import annotations
import math
import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple
from .piece import Piece



class SevenBag:
    def __init__(self):
        self.bag: List[str] = []

    def next(self) -> str:
        if not self.bag:
            self.bag = ["I", "J", "L", "O", "S", "T", "Z"]
            random.shuffle(self.bag)
        return self.bag.pop()

