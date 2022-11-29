from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from game_map import GameMap
from procgen import pop_clears, correct_char
from tcod import event as ev
import numpy as np

class Action:
    def perform(self, engine: Engine, entity: Entity = None) -> None:
        """Perform this action with the objects needed to determine its scope.

        `engine` is the scope this action is being performed in.

        `entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """ 
        raise NotImplementedError()

class EscapeAction(Action):
    def perform(self, engine: Engine, entity: Entity = None) -> None:
        raise SystemExit()

class MovementAction(Action):
    def __init__(self, dx: int, dy: int):
        super().__init__()

        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine, entity: Entity = None) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        entity.move(self.dx, self.dy)

class MouseAction(Action):
    def __init__(self, event, context, gamemap: GameMap):
        super().__init__()
        context.convert_event(event)
        self.tile_pos = event.tile
        self.gamemap = gamemap

    def perform(self, engine: Engine, entity: Entity = None) -> None:
        if self.tile_pos[1] < np.shape(self.gamemap.tiles)[1] and not self.gamemap.tiles[self.tile_pos]['explosive']:
            if not self.gamemap.tiles[self.tile_pos]['numbomb']:
                pop_clears(self.tile_pos, self.gamemap)
            else: self.gamemap.revealed[self.tile_pos] = True
        else: print('bomb')

class SpaceAction(Action):
    def __init__(self, event, context, gamemap):
        super().__init__()
        self.mouse_pos = ev.get_mouse_state()
        context.convert_event(self.mouse_pos)
        self.mouse_pos = self.mouse_pos.tile
        self.gamemap = gamemap
        
    def perform(self, engine, entity = None):
        if self.mouse_pos[1] < np.shape(self.gamemap.tiles)[1]:
            if not (self.gamemap.tiles[self.mouse_pos]['flagged']):
                self.gamemap.tiles[self.mouse_pos]['flagged'] = True
                self.gamemap.revealed[self.mouse_pos] = True
                self.gamemap.tiles[self.mouse_pos]['light'] = (ord('F'), (0, 0, 0), (130, 110, 50))
            else: 
                self.gamemap.tiles[self.mouse_pos]['flagged'] = False
                self.gamemap.revealed[self.mouse_pos] = False
                self.gamemap.tiles[self.mouse_pos]['light'] = (ord(
                    correct_char(self.mouse_pos, self.gamemap)), (255, 255, 255), (130, 110, 50))