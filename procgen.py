from typing import Iterator, Tuple, List, TYPE_CHECKING
import random
import time
from game_map import GameMap
import tile_types
from entity import Entity
import numpy as np

circ_coords = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
core_coords = ((-1, -1), (1, 1))
corner_coords = ((-1, -1), (1, -1), (-1, 1), (1, 1))
class GrowingSeed():

    def __init__(self, gamemap: GameMap, allocated_space: int = 30, start_point: Tuple[int, int] = (0, 0)):
        """Initialize the seed growth"""
        self.gamemap, self.allocated_space, self.start_point = gamemap, allocated_space, start_point
        self.options = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        self.coords = set()
        self.coords.update(set(((start_point),)))
        self.proceed = True
        self.tendrils = {'right': Tendril(gamemap, self.add_coords(self.start_point, self.options[0])), 
            'down': Tendril(gamemap, self.add_coords(self.start_point, self.options[1])),
            'left': Tendril(gamemap, self.add_coords(self.start_point, self.options[2])),
            'up': Tendril(gamemap, self.add_coords(self.start_point, self.options[3]))}
        for k, v in self.tendrils.items():
            self.coords.update(set(((v.origin),)))
        while len(self.coords)<self.allocated_space and self.proceed:
            self.advance()
        
    def add_coords(self, ori_pair: Tuple[int, int], added: Tuple[int, int]):
        """Add together two tuple pairs of coords"""
        return((ori_pair[0]+added[0], ori_pair[1]+added[1]))

    def advance(self):
        """For each tendril in the seed, advance by one square as best as possible,
        ending future attempts if each tendril ends up trapped and dead"""
        tally = 0
        for tendril in self.tendrils.values():
            if tendril.grow:
                maybe = tendril.advance_one(self.options.copy(), ghost = [0, 1, 2, 3])
                if maybe: 
                    self.coords.update(((maybe),))
            else: tally+=1
        if tally>3: self.proceed = False
    
class Tendril():
    def __init__(self, gamemap, start_point: Tuple[int, int]):
        """Initialize the tendril"""
        self.coords = set((start_point))
        self.origin = start_point
        self.grow = True
        self.gamemap = gamemap
        self.head = start_point

    def advance_one(self, options, ghost=[0, 1, 2, 3]) -> None:
        """Advance by one if possible, going through the options given recursively, stopping
        if all options are already in the tendril"""
        cycle = random.choice(ghost)
        potential = (self.head[0]+options[cycle][0], self.head[1]+options[cycle][1])
        if potential not in self.coords and potential[0]>=0 and potential[1]>=0 and(
            potential[0]<self.gamemap.width+6 and potential[1]<self.gamemap.height+6
        ):
            self.coords.update(potential)
            self.head = potential
            return(potential)
        else: 
            if len(ghost)>1:
                ghost.remove(cycle)
                self.advance_one(options, ghost=ghost)
            else: self.grow = False

def generate_map(
    map_width: int,
    map_height: int,
    desired_bomb_percent: int,
    playable: bool) -> GameMap:
    """Generate a new minesweeper map."""

    mine_map = GameMap(map_width, map_height)
    gen_start = time.time()
    indexes = []
    #Create the preset map seeds initial coords
    for x in range(1, 4):
        for y in range(1, 4):
            if x != 2 and y != 2:
                indexes.append(((map_height+6)*y//4, (map_width+6)*x//4))
    print(f'Generation Started at {round((time.time()-gen_start), 2)}')
    threshold = max(map_width//50, map_height//50)
    free_space_total = (map_width+6)*(map_height+6)
    bomb_num = free_space_total*desired_bomb_percent//100
    safe_num = free_space_total-bomb_num
    initial_safe = safe_num
    center = (map_width//2, map_height//2)
    #Create the first seed in the center of the map
    seed = GrowingSeed(mine_map, random.randint(safe_num//10, safe_num//5), center)
    safe_num -= len(seed.coords)
    seeds = [seed]
    total_coords = set()
    total_coords.update(seed.coords)
    print(f'First seed done at {round((time.time()-gen_start), 2)}')
    trial = 0
    while safe_num > (free_space_total-bomb_num)//10:
        if trial <= len(indexes)-1:
            start = indexes[trial]
            trial += 1
            amount = initial_safe // 20
        else: 
            if trial==len(indexes):
                trial+=1
                print(f'Preset seeds done at {round((time.time()-gen_start), 2)}, starting random')
            else: print(f'New random seed at {round((time.time()-gen_start), 2)}')
            trial += 1
            if trial < 20: counter = trial
            else: counter = 20
            amount = random.randint(((free_space_total-bomb_num)//25), safe_num//(21-counter))
            start = rand_start_point(map_width+6, map_height+6, mine_map, total_coords, threshold=threshold)
            #print(f'Random start found at {round((time.time()-gen_start), 2)}, generating')
        seeds.append(GrowingSeed(mine_map, amount, start))
        total_coords.update(seeds[-1].coords)
        safe_num = free_space_total-bomb_num-len(total_coords)
    print(f'Seeds complete, shifting at {round((time.time()-gen_start), 2)}')
    for x, y in total_coords:
        if not(x<=2 or y<=2 or y>=map_height+3 or x>=map_width+3):
            mine_map.tiles[x-3, y-3] = tile_types.safe
            mine_map.explosive[x-3, y-3] = False
    if playable:
        print(f'Shifting complete, filling gaps at {round((time.time()-gen_start), 2)}')
        mine_map, start_points = fill_gaps(gen_start, mine_map)
        print(f"Filling done, revealing start at {round((time.time()-gen_start), 2)}")
        #reveal_all_blanks(start_points, mine_map)
        reveal_squares_around_start(start_points, mine_map)
        print(f"Start revealed, game begins at {round((time.time()-gen_start), 2)}")
    else: 
        print(f'Shifting complete, trying to reveal start {round((time.time()-gen_start), 2)}')
        try_until_pop(map_width, map_height, mine_map)
    return mine_map

def rand_start_point(map_width, map_height, mine_map, total_coords, threshold = 0):
    """Repeatedly check random points on the map for a certain radius of
    openness for a new seed based on the size of the map, returning a properly isolated point"""
    go = False
    rounds = 0
    while not go:
        coord = (random.randint(1, map_width-3), random.randint(1, map_height-3))
        if coord not in total_coords: 
            if not threshold: go=True
            else: 
                if not sum_safes(coord, mine_map):
                    if threshold == 1: go = True
                    else:
                        around = return_circle_coords(coord, mine_map)
                        count = 0
                        for pair in around:
                            if sum_safes(pair, mine_map): count+=1
                            if threshold > 4:
                                around2 = return_circle_coords(pair, mine_map)
                                for pair2 in around2:
                                    if sum_safes(pair2, mine_map): count+=1
                        if not count: go = True
        rounds += 1
        if rounds > 200:
            if threshold > 0:
                return(rand_start_point(map_width, map_height, mine_map, total_coords, threshold-1))
            else: return(0, 0)
    return(coord)

def fill_gaps(gen_start, mine_map):
    """Fill up bomb gorges in a semi-random way, then assign values to each tile
    according to the number of bombs in their direct proximity"""
    gen_start = gen_start
    start_points = set()
    bounds = np.shape(mine_map.tiles)
    prev_circle = return_circle_coords((0, 0), mine_map)
    tiles = mine_map.tiles
    expl = mine_map.explosive
    # First pass to fill in isolated bomb gorges
    for x in range(bounds[0]):
        for y in range(bounds[1]):
            now, prev_circle = sum_safes_with_back_tracking((x, y), mine_map, prev_circle)
            if now < 2:
                tiles[x, y] = tile_types.safe
                expl[x, y] = False
            elif now == 2:
                if random.random()>0.5:
                    tiles[x, y] = tile_types.safe
                    expl[x, y] = False
    print(f"First pass complete in filling, onto second at {round((time.time()-gen_start), 2)}")
    # Second pass to cover isolated spaces that were converted, but still have no others around them
    prev_circle = return_circle_coords((0, 0), mine_map)
    for x in range(bounds[0]):
        for y in range(bounds[1]):
            now, prev_circle = sum_safes_with_back_tracking((x, y), mine_map, prev_circle)
            if now < 1:
                new = return_random_adjacent((x, y), mine_map)
                tiles[new] = tile_types.safe
                expl[new] = False
    print(f"Second pass complete, updating all tiles to finish at {round((time.time()-gen_start), 2)}")
    # Update numbombs for each square, and change square number accordingly
    prev_circle = return_circle_coords((0, 0), mine_map)
    for x in range(bounds[0]):
        for y in range(bounds[1]):
            count, prev_circle = sum_bombs_with_back_tracking((x, y), mine_map, prev_circle)
            tiles[x, y]['numbomb'] = count
            if tiles[x, y]['numbomb'] and not expl[x, y]:
                tiles[x, y]['light'][0] = ord(str(tiles[x, y]['numbomb']))
            else: start_points.update(((x, y),))
    return(mine_map, start_points)

def return_random_adjacent(tile_address, mine_map, unwanted=False, trial = 0, bounds=None):
    """Repeatedly try random adjacent spots until one is in bounds and not of the unwanted explosive variety.
    If none of them work after 150 attempts, simply returns the tile address given. Can preset the trial number
    to heighten or lower the number of allowed attempts"""
    if not bounds: bounds = np.shape(mine_map.tiles)
    idea = [tile_address[0]+random.randint(-1, 1), tile_address[1]+random.randint(-1, 1)]
    if idea != tile_address and check_in_bounds(idea, bounds) and (
        mine_map.explosive[idea[0], idea[1]] != unwanted):
        return(idea)
    elif trial<150: 
        trial+=1
        return(return_random_adjacent(tile_address, mine_map, trial=trial, bounds=bounds))
    else: return(tile_address)

def return_surrounding_types(tile_address, mine_map):
    """Return a list of surrounding tile types"""
    output = return_circle_coords(tile_address, mine_map)
    ret = []
    for x, y in output: ret.append(mine_map.tiles[x, y]['explosive'])
    return(ret)

def return_circle_coords_old(tile_address, mine_map):
    """Return the Tuple addresses for all 8 surrounding squares for a tile, less if it is an edge,
    adjusting to the bounds of the map accordingly"""
    output = []
    bounds = np.shape(mine_map.tiles)
    for x in range(-1, 2):
        for y in range(-1, 2):
            perhaps = (tile_address[0]+x, tile_address[1]+y)
            if (x or y) and check_in_bounds(perhaps, bounds):
                output.append(perhaps)
    return(output)

def return_circle_coords(tile_address, mine_map):
    """Return the tuple addresses for the surrounding squares, only running corner collision checks
    unless there is a wall of some kind. Speeds up pop_clears"""
    output = []
    bounds = np.shape(mine_map.tiles)
    for x, y in core_coords:
        perhaps = (tile_address[0]+x, tile_address[1]+y)
        if check_in_bounds(perhaps, bounds):
            continue
        return(return_circle_coords_old(tile_address, mine_map))
    for x, y in circ_coords:
        output.append((tile_address[0]+x, tile_address[1]+y))
    return(output)

def pop_clears(tile_address, mine_map, round = 0):
    """Repeatedly reveal both the tile_address and its surroundings if it has no bombs 
    adjacent to it, with a given 300 recursive attempts to get them all. This means not all
    of massive landscapes at 100*100 maps and up are revealed in one go, but it is needed to
    avoid looping and recursion limits in interior functions"""
    if not mine_map.tiles[tile_address[0], tile_address[1]]['numbomb'] and (
        not mine_map.tiles[tile_address[0], tile_address[1]]['explosive']):
        mine_map.revealed[tile_address[0], tile_address[1]] = True
        for x, y in return_circle_coords(tile_address, mine_map):
            mine_map.revealed[x, y] = True
            around = []
            for w, z in return_circle_coords((x, y), mine_map):
                around.append(mine_map.revealed[w, z])
            if not all(around):
                stuck = set()
                for a, b in return_circle_coords((x, y), mine_map):
                    if not mine_map.revealed[a, b]:
                        stuck.update(((a, b),))
                        break
                if round<300:
                    round+=1
                    for coord1, coord2 in stuck:
                        pop_clears((coord1, coord2), mine_map, round=round)

def sum_of_bombs(tile_address, mine_map):
    """Return the sum of bombs in the adjacent squares"""
    list = return_surrounding_types(tile_address, mine_map)
    count = 0
    for x in list: count+=x
    return(count)

def sum_safes(tile_address, mine_map):
    """Return the sum of safe spaces in the adjacent squares"""
    list = return_surrounding_types(tile_address, mine_map)
    count = 0
    for x in list: count += not x
    return(count)

def sum_safes_with_back_tracking(tile_address, mine_map, prev_circle):
    """Return the sum of safe spaces in the adjacent squares, using previous info to speed things up
    and avoid unnecessary repeat checks. Assumes that iterators go through the map per column, and 
    that they proceed one y coordinate down at a time."""
    if len(prev_circle) == 8:
        for x in range(8):
            prev_circle[x] = (prev_circle[x][0], prev_circle[x][1]+1)
        if prev_circle[2][1] >= np.shape(mine_map.tiles)[1]:
            prev_circle.pop(7)
            prev_circle.pop(4)
            prev_circle.pop(2)
        count = 0
        for x in prev_circle: count += not mine_map.explosive[x]
        return(count, prev_circle)
    else: return(sum_safes(tile_address, mine_map), return_circle_coords_old(tile_address, mine_map))

def sum_bombs_with_back_tracking(tile_address, mine_map, prev_circle):
    """Return the sum of bombs in the adjacent squares, using previous info to speed things up
    and avoid unnecessary repeat checks. Assumes that iterators go through the map per column, and 
    that they proceed one y coordinate down at a time."""
    if len(prev_circle) == 8:
        for x in range(8):
            prev_circle[x] = (prev_circle[x][0], prev_circle[x][1]+1)
        if prev_circle[2][1] >= np.shape(mine_map.tiles)[1]:
            prev_circle.pop(7)
            prev_circle.pop(4)
            prev_circle.pop(2)
        count = 0
        for x in prev_circle: count += mine_map.explosive[x]
        return(count, prev_circle)
    else: return(sum_of_bombs(tile_address, mine_map), return_circle_coords_old(tile_address, mine_map))

def check_in_bounds(tile_address, bounds):
    """Check if a specified tile_address is within the boundaries of the map"""
    if tile_address[0]>=0 and tile_address[1]>=0:
        if tile_address[0]<bounds[0] and tile_address[1]<bounds[1]:
            return True
    return False

def reveal_squares_around_start(start_points, mine_map):
    """Using an odd counter system for the starter point set that avoids list inefficiency for bigger sizes,
    reveal a maybe-random clear space to start the game"""
    trial = 0
    for start_point in start_points:
        cycle = 0
        start_point = start_point
        break
    while not mine_map.revealed[start_point[0], start_point[1]]:
        for start_point in start_points:
            start_point = start_point
            if trial == cycle:
                trial = 0
                cycle += 1
                break 
            trial += 1    
        if cycle != 1: print(f"Previous cycle failed, onto cycle {cycle}")
        # Occasionally pop_clears fails to reveal anything in this context, and I'm scared of the recursive 
        # mess I made. So, repeat until it works! It works about 60% of the time on the first try, but then tends
        # to fail repeatedly if it does fail. Not sure why, but it doesn't delay the game too much.
        pop_clears(start_point, mine_map)

def reveal_all_blanks(start_points, mine_map):
    """Attempt to unveil every point with 0 bombs. Time-consuming, honestly just iterating to
    reveal every tile is more helpful generally, but this does avoid revealing bombs."""
    for start_point in start_points:
        pop_clears(start_point, mine_map)

def correct_char(tile_address, mine_map):
    """Based on the explosive nature and number of nearby bombs, return the associated character"""
    if not mine_map.explosive[tile_address]: 
        su = sum_of_bombs(tile_address, mine_map)
        if not su:
            return('-')
        else: return(str(su))
    else: return('\\')

def try_until_pop(map_width, map_height, mine_map):
    coord = (0, 0)
    rounds = 0
    while not mine_map.revealed[coord[0], coord[1]]:
        coord = (random.randint(0, map_width-1), random.randint(0, map_height-1))
        if not sum_of_bombs(coord, mine_map):
            pop_clears(coord, mine_map)
        rounds+=1
        if rounds>50: 
            print('Darn, looks like something went wrong. Debug code: Try again')
            break