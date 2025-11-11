# render/theme.py
from typing import Protocol, Tuple, Any, Mapping

RGB = Tuple[int,int,int]
class Theme(Protocol):
    palette: Mapping[str, RGB]
    font_small: Any
    font_big: Any
    grid_color: RGB
    bg_color: RGB
