from __future__ import annotations
import numpy as np
from tcod.console import Console

import tile_types

from typing import Iterable
from entity import Entity

class GameMap:
    def __init__(self, width:int, height:int, entities: Iterable[Entity] = ()):
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.bomb, order="F")
        self.revealed = np.full((width, height), fill_value=False, order='F')
        self.explosive = np.full((width, height), fill_value=True, order='F')

    def render(self, console: Console) -> None:
        """If a tile is visible, draw with "light" colors, otherwise draw with SHROUD"""
        console.tiles_rgb[0:self.width, 0:self.height] = np.select(
            condlist = [self.revealed],
            choicelist = [self.tiles['light']],
            default = tile_types.SHROUD
        )
        for entity in self.entities:
            pass
            #console.print(entity.x, entity.y, entity.char, fg=entity.color)

