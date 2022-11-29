from typing import Iterable, Any

from tcod.context import Context
from tcod.console import Console

from entity import Entity
from input_handlers import EventHandler
from game_map import GameMap

class Engine:
    def __init__(self, event_handler: EventHandler, game_map: GameMap):
        self.event_handler, self.game_map = event_handler, game_map

    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)
            if action is None: continue
            action.perform(self)

    def render(self, console: Console, context: Context):
        self.game_map.render(console)
        context.present(console)
        console.clear()