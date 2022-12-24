import tcod
from input_handlers import EventHandler
from engine import Engine
from procgen import generate_map

def main():
    s_width = 500
    s_height = 500
    g_width = 500
    g_height = 500

    tileset = tcod.tileset.load_tilesheet("Games/Minesweeper/randomimage.png", 32, 8, tcod.tileset.CHARMAP_TCOD)
    playable = True
    game_map = generate_map(g_width, g_height, 25, playable)
    context = tcod.context.new(
        x=100,
        y=100,
        width = 1000,
        height = 1000,
        columns = g_width,
        rows = g_height,
        tileset=tileset,
        title = "Minesweeper",
        vsync=True)

    event_handler = EventHandler(game_map, context)

    engine = Engine(event_handler = event_handler, game_map = game_map)

    root_console = tcod.Console(s_width, s_height, order='F')
    while True:
        engine.render(console=root_console, context=context)
        events = tcod.event.wait()
        engine.handle_events(events)
                
if __name__ == '__main__':
    main()