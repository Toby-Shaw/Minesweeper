from typing import Optional

import tcod.event

from actions import Action, EscapeAction, MovementAction, MouseAction, SpaceAction
from game_map import GameMap

class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, gamemap, context):
        self.context = context
        self.gamemap = gamemap

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        if key == tcod.event.K_UP:
            action = MovementAction(dx=0, dy=-1)
        elif key == tcod.event.K_DOWN:
            action = MovementAction(dx=0, dy=1)
        elif key == tcod.event.K_LEFT:
            action = MovementAction(dx=-1, dy=0)
        elif key == tcod.event.K_RIGHT:
            action = MovementAction(dx=1, dy=0)

        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction()

        elif key == tcod.event.K_SPACE:
            action = SpaceAction(event, self.context, self.gamemap)

        # No valid key was pressed
        return action

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
        action = MouseAction(event, self.context, self.gamemap)
        return action