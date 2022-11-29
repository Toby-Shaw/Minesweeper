from typing import Tuple
import numpy as np

graphic_dt = np.dtype(
    [   
        ("ch", np.int32),  #Unicode
        ("fg", "3B"),   #Foreground
        ('bg', "3B"),   #Background
    ]
)

tile_dt = np.dtype(
    [
        ('revealed', np.bool),
        ('flagged', np.bool),
        ('explosive', np.bool),
        ('numbomb', np.int32),
        ('light', graphic_dt)
    ]
)

def new_tile(
    *, revealed: bool, flagged: bool, explosive: bool, numbomb: int,
        light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]
    ) -> np.ndarray:
    """Helper Function to make a tile with associated attributes"""
    return np.array((revealed, flagged, explosive, numbomb, light), dtype=tile_dt)

SHROUD = np.array((ord(' '), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)

safe = new_tile(
    revealed = False,
    flagged = False,
    explosive = False,
    numbomb = 0,
    light=(ord('-'), (255, 255, 255), (130, 110, 50))
)
bomb = new_tile(
    revealed = False,
    flagged = False,
    explosive = True,
    numbomb = 0,
    light=(ord('\\'), (255, 255, 255), (130, 110, 50))
)
