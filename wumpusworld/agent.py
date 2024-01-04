from collections import deque
from copy import deepcopy
from enum import Enum
from world import WumpusWorld as World
from world import Direction
from sat_solver import KnowledgeBase
import math
from queue import PriorityQueue

class Status(Enum):
    UNSAFE = 1
    SAFE = 2
    EXPLORED = 3


class Room:
    def __init__(self, pos: tuple, wpos: tuple, percept, status: Status):
        self.pos = pos
        self.wpos = wpos
        self.percept = percept
        self.status = status


class Map:
    def __init__(self, world: World, start: Room):
        self.__world = world
        self.__data: list[list] = [[start]]
        self.__offset = (0, 0)

    def data(self):
        return self.__data

    def __getallocstate(self, position):
        d = (position[0] + self.__offset[0], position[1] + self.__offset[1])
        if d[0] >= len(self.__data) or d[1] >= len(self.__data[0]) or d[0] < 0 or d[1] < 0:
            return 0
        if self[position] is None:
            return 1
        return 2

    def _getworldposition_(self, item):
        d = (item[0] + self.__offset[0], item[1] + self.__offset[1])
        return d

    def __getitem__(self, item):
        d = (item[0] + self.__offset[0], item[1] + self.__offset[1])
        return self.__data[d[0]][d[1]]

    def __setitem__(self, key, value):
        d = (key[0] + self.__offset[0], key[1] + self.__offset[1])
        self.__data[d[0]][d[1]] = value

    def add(self, parent, direction, cwpos):
        if direction == Direction.RIGHT:
            cpos = (parent[0], parent[1] + 1)
            if self.__getallocstate(cpos) == 0:
                for row in self.__data:
                    row.append(None)
                self[cpos] = Room(cpos, cwpos, None, Status.SAFE)
            elif self.__getallocstate(cpos) == 1:
                self[cpos] = Room(cpos, cwpos, None, Status.SAFE)
        elif direction == Direction.DOWN:
            cpos = (parent[0] + 1, parent[1])
            if self.__getallocstate(cpos) == 0:
                self.__data.append([None for _ in range(len(self.__data[0]))])
                self[cpos] = Room(cpos, cwpos, None, Status.SAFE)
            elif self.__getallocstate(cpos) == 1:
                self[cpos] = Room(cpos, cwpos, None, Status.SAFE)
        elif direction == Direction.LEFT:
            cpos = (parent[0], parent[1] - 1)
            if self.__getallocstate(cpos) == 0:
                for row in self.__data:
                    row.insert(0, None)
                self.__offset = (self.__offset[0], self.__offset[1] + 1)
                self[cpos] = Room(cpos, cwpos, None, Status.SAFE)
            elif self.__getallocstate(cpos) == 1:
                self[cpos] = Room(cpos, cwpos, None, Status.SAFE)
        elif direction == Direction.UP:
            cpos = (parent[0] - 1, parent[1])
            if self.__getallocstate(cpos) == 0:
                self.__data.insert(0, [None for _ in range(len(self.__data[0]))])
                self.__offset = (self.__offset[0] + 1, self.__offset[1])
                self[cpos] = Room(cpos, cwpos, None, Status.SAFE)
            elif self.__getallocstate(cpos) == 1:
                self[cpos] = Room(cpos, cwpos, None, Status.SAFE)

    def get_nearby(self, position):
        nearby = []
        right = (position[0], position[1] + 1)
        left = (position[0], position[1] - 1)
        up = (position[0] - 1, position[1])
        down = (position[0] + 1, position[1])
        if self.__getallocstate(right) == 2:
            nearby.append(self[right])
        if self.__getallocstate(down) == 2:
            nearby.append(self[down])
        if self.__getallocstate(left) == 2:
            nearby.append(self[left])
        if self.__getallocstate(up) == 2:
            nearby.append(self[up])
        return nearby

    def explore(self, position):
        self[position].status = Status.EXPLORED

    def is_explored(self):
        return not any(room is not None and room.status == Status.SAFE for row in self.__data for room in row)

    def position(self, actual_position):
        return actual_position[0] - self.__world.agent[0], actual_position[1] - self.__world.agent[1]

    def __str__(self):
        return '\n'.join(['[' + ','.join([str(room) if room is not None else '(None, None, None)' for room in row]) + ']' for row in self.__data])


class Action(Enum):
    """Enum class to represent the actions of the agent."""
    MOVE_RIGHT = 0
    MOVE_UP = 1
    MOVE_LEFT = 2
    MOVE_DOWN = 3
    SHOOT = 4
    GRAB = 5
    CLIMB = 6
    FALL_INTO_PIT = 7
    EATEN_BY_WUMPUS = 8
    SHOOT_MULTIPLE_TIMES = 9


class Agent:
    RECURSION_LIMIT = 100
    RECURSION_COUNT = 0

    def __init__(self, world: World):
        self.world = world
        self.current = Room((0, 0), world.agent, 'A', Status.SAFE)
        self.visited = set()
        self.kb = KnowledgeBase(True, [])
        self.golds = []

    def __is_wall(self, position: tuple):
        """Check if a given position is a wall."""
        if position[0] < 1 or position[0] > self.world.n:
            return True
        return False

    @classmethod
    def infer(cls, kb, clause):
        """Infer the knowledge base."""
        temp = deepcopy(kb)
        temp.add_clause([clause])
        result = temp.solve()
        return not result

    @classmethod
    def update(cls, kb, room, adjacents):
        """Update the knowledge base."""
        if 'P' in room.percept:
            pit_clause = {f'P{room.pos}': 0}
        else:
            pit_clause = {f'P{room.pos}': 1}
        kb.add_clause([pit_clause])

        if 'W' in room.percept:
            wumpus_clause = {f'W{room.pos}': 0}
        else:
            wumpus_clause = {f'W{room.pos}': 1}
        kb.add_clause([wumpus_clause])

        if 'B' in room.percept:
            # Breeze => Pup or Pdown or Pleft or Pright
            # not Breeze or Pup or Pdown or Pleft or Pright
            breeze_clause = {f'B{room.pos}': 1}
            for adjacent in adjacents:
                breeze_clause.update({f'P{adjacent.pos}': 0})
            kb.add_clause([breeze_clause])

        if 'S' in room.percept:
            # Stench => Wup or Wdown or Wleft or Wright
            stench_clause = {f'S{room.pos}': 1}
            for adjacent in adjacents:
                stench_clause.update({f'P{adjacent.pos}': 0})
            kb.add_clause([stench_clause])

        if room.percept == '' or room.percept == 'E' or room.percept == 'K':
            for adjacent in adjacents:
                # not Padj and not Wadj
                kb.add_clause([{f'P{adjacent.pos}': 1}, {f'W{adjacent.pos}': 1}])
                kb.del_clause(f'S{room.pos}')
                kb.del_clause(f'B{room.pos}')

    @classmethod
    def remove_wumpus(cls, kb, symbol):
        """Remove wumpus from the knowledge base."""
        kb.del_clause(symbol)

    @classmethod
    def __shoot(cls, room, path: deque, mem: Map, inventory: set, world: World,
                kb: KnowledgeBase, shoot):
        """Internal method to shoot the wumpus 1 (one) time."""
        adjacents = mem.get_nearby(room.pos)
        adjacents = [adjacent for adjacent in adjacents if adjacent.status != Status.EXPLORED]
        target = adjacents.pop(0)
        scream = world.kill_wumpus(target.wpos)
        room.percept = world[target.wpos]
        sadjacents = [sadjacent for sadjacent in mem.get_nearby(target.pos) if sadjacent.pos != room.pos]
        target.status = Status.EXPLORED
        if scream:
            cls.remove_wumpus(kb, f'W{target.pos}')
            if 'S' not in room.percept:
                for adjacent in adjacents:
                    if adjacent.status == Status.UNSAFE:
                        adjacent.status = Status.SAFE
                cls.update(kb, room, mem.get_nearby(room.pos))
        else:
            for adjacent in sadjacents:
                if not all(room for room in mem.get_nearby(adjacent.pos) if room.status == Status.EXPLORED):
                    adjacent.status = Status.SAFE
        target.status = Status.SAFE
        if cls.__search(target, room, path, mem, inventory, world, kb, shoot):
            return True

    @classmethod
    def __shoot_until_scream(cls, room, path: deque, mem: Map, inventory: set, world: World, kb: KnowledgeBase, shoot):
        """Internal method to shoot the wumpus until it screams."""
        adjacents = mem.get_nearby(room.pos)
        adjacents = [adjacent for adjacent in adjacents if adjacent.status != Status.EXPLORED]
        target = []
        for adjacent in adjacents:
            target.append(adjacent)
            scream = world.kill_wumpus(target[-1].wpos)
            room.percept = world[room.wpos]
            if scream:
                cls.remove_wumpus(kb, f'W{target[-1].pos}')
                if 'S' not in room.percept:
                    cls.update(kb, room, mem.get_nearby(room.pos))
                    for t in target:
                        t.status = Status.SAFE
                    if room.wpos not in shoot:
                        shoot[room.wpos] = [t.wpos for t in target]
                    break
        if cls.__search(target[-1], room, path, mem, inventory, world, kb, shoot):
            return True

    @classmethod
    def __search(cls, room: Room, parent, path: deque, mem: Map, inventory: set, world: World, kb: KnowledgeBase, shoot = None):
        """Internal method to search the world."""
        cls.RECURSION_COUNT += 1
        if cls.RECURSION_COUNT >= cls.RECURSION_LIMIT:
            return True
        if room is None:
            return False
        room.percept = world[room.wpos]
        
        path.append((room, room.wpos, deepcopy(room.percept)))
        if 'W' in room.percept:
            return True
        if 'P' in room.percept:
            return True
        if 'G' in room.percept:
            room.percept = room.percept.replace('G', 'E')
            world.pickup_gold(room.pos)
            inventory.add(room.pos)
        wadjacents = world.get_adjacents(room.wpos)
        for wadjacent in wadjacents:
            mem.add(room.pos, wadjacent[0], (wadjacent[1], wadjacent[2]))
        adjacents = mem.get_nearby(room.pos)
        adjacents = [adjacent for adjacent in adjacents if adjacent.status != Status.EXPLORED]
        if room.status != Status.EXPLORED:
            cls.update(kb, room, adjacents)
            room.status = Status.EXPLORED
        if 'B' in room.percept:
            for adjacent in adjacents:
                if cls.infer(kb, {f'P{adjacent.pos}': 1}):
                    cls.update(kb, room, adjacents)
                    adjacent.status = Status.UNSAFE
                elif not cls.infer(kb, {f'P{adjacent.pos}': 0}):
                    adjacent.status = Status.UNSAFE
        if 'S' in room.percept:
            for adjacent in adjacents:
                if cls.infer(kb, {f'W{adjacent.wpos}': 1}):
                    cls.update(kb, room, adjacents)
                    adjacent.status = Status.UNSAFE
                elif not cls.infer(kb, {f'W{adjacent.pos}': 0}):
                    adjacent.status = Status.UNSAFE
        if room.percept == '' or room.percept == 'E' or room.percept == 'K':
            for adjacent in adjacents:
                adjacent.status = Status.SAFE
        if len(adjacents) == 0:
            if not mem.is_explored():
                path.append((parent, parent.wpos, deepcopy(parent.percept)))
                return False
            else:
                return True
        else:
            if 'S' in room.percept and 'B' in room.percept:
                if cls.__shoot_until_scream(room, path, mem, inventory, world, kb, shoot):
                    return True
            elif 'S' in room.percept:
                if cls.__shoot_until_scream(room, path, mem, inventory, world, kb, shoot):
                    return True
            elif 'B' in room.percept:
                if mem.is_explored():
                    return True
                else:
                    adjacents = [adjacent for adjacent in adjacents if adjacent.status == Status.SAFE]
                    if len(adjacents) == 0:
                        path.append((parent, parent.wpos, deepcopy(parent.percept)))
                        return False
                    else:
                        if cls.__search(adjacents[0], room, path, mem, inventory, world, kb, shoot):
                            return True
            else:
                for adjacent in adjacents:
                    if adjacent.status == Status.SAFE and cls.__search(adjacent, room, path, mem, inventory, world, kb, shoot):
                        return True
        path.append((parent, parent.wpos, deepcopy(parent.percept)))
        return False

    def manhattan_heuristic(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def find_exit_path(self, map: Map, agent_pos: Room, goal_pos: Room):
        '''
        This function using A* search with Manhattan heuristic function to find out the shortest path for agent to
        get the exit room, whenever it has discovered the whole map or there is no safe way to continue the discovery.

        Obviously, the input are the map that stored so far by the agent, the room that agent is standing in, and the goal
        position iff the agent has visited it before. Note that the agent only know the exit door if it has visited
        the exit room before, so in some cases the goal_pos is Unknown.

        For safety, in the discovered process of the agent, if there is no any possible safe room to be explored and the agent has pass through
        the exit room, it prioritizes to go to the exit room instead of continue the exploration. If there is no any safe room
        but the agent has not go to the exit room before, it has to continue the exploration by go one step randomly.

        This returns the list of path in form of coordinations of room.
        '''

        frontier = PriorityQueue()
        frontier.put((self.manhattan_heuristic(agent_pos.wpos, goal_pos.wpos), (0, agent_pos.pos)))

        map_data = map.data()

        visited = set()
        path = {}
        path[agent_pos] = None
        while not frontier.empty():
            _, (cost, agent) = frontier.get_nowait()

            agent = map.__getitem__(agent)

            if agent == goal_pos:
                break

            if agent in visited:
                continue
            visited.add(agent)


            raw_neighbors = map.get_nearby(agent.pos)
            neighbors = []
            for row in map_data:
                for room in row:
                    if room in raw_neighbors:
                        if room.percept != None:
                            if room.percept == '' or 'G' in room.percept or 'B' in room.percept or 'S' in room.percept or 'E' in room.percept or 'K' in room.percept:
                                neighbors.append(room)

            for neighbor in neighbors:
                if neighbor in visited:
                    continue
                path[neighbor] = agent
                frontier.put((cost + self.manhattan_heuristic(neighbor.wpos, goal_pos.wpos) + 1, (cost + 1, neighbor.pos)))
        routine = self.extract_final_path(path, goal_pos)

        return routine

    def extract_final_path(self, path, goal):
        routine = []

        pos = goal
        while True:
            if pos not in path:
                break
            if path[pos] == None:
                break
            routine.append(pos)
            pos = path[pos]
        return routine

    def convert_to_motions(self, path):
        '''
        This function responsible for converting the path in coordination form into Motion and Action signals
        
        originally, path is list of room (in tuple of coordination) and already ordered follows the agent motion in its discovered process. 
        
        This function responsible for converting the path in coordination form into Motion signals

        originally, path is list of room (in tuple of coordination) and already ordered follows the agent motion.

        Now, it is converted into Motions signal by using a simple set of rules: if the current room is located on the
        right hand-side of the next room (for example, current room is (4, 3) and next room is (4,2)),
        the signal of Motion is MOVE_LEFT.

        Similarly, we apply the rule for the rest of cases.

        This function return set of Motions in a list.

        Recall the enum of motions annotation:
            MOVE_RIGHT = 0
            MOVE_UP = 1
            MOVE_LEFT = 2
            MOVE_DOWN = 3
            SHOOT = 4
            GRAB = 5
            CLIMB = 6
            FALL_INTO_PIT = 7
            EATEN_BY_WUMPUS = 8
        '''
        motions = []
        gold_obtained = set()
        shooted_wumpus = set()
        motions = []

        for i in range (1, len(path)):
            # Motion    
            if (path[i-1].pos)[0] < (path[i].pos)[0]:
                motions.append(Action.MOVE_DOWN)
            elif (path[i-1].pos)[0] > (path[i].pos)[0]:
                motions.append(Action.MOVE_UP)
            elif (path[i-1].pos)[1] < (path[i].pos)[1]:
                motions.append(Action.MOVE_RIGHT)
            else:
                motions.append(Action.MOVE_LEFT)
                
            #Action
            if not path[i].percept:
                continue
            
            if 'E' in path[i].percept and path[i].pos not in gold_obtained:
                motions.append(Action.GRAB)
                gold_obtained.add(path[i].pos)
            
            # Note: this action including the yelling of the wumpus after it is shooted
            # if a room has both Breeze and Stench, it shoots until a wumpus is dead and go to that room. 
            # temporary
            if 'B' in path[i].percept:
                if i != len(path) - 1:
                    if not path[i+1].percept:
                        continue
                    if 'K' in path[i+1].percept and path[i+1].pos not in shooted_wumpus:    
                        motions.append(Action.SHOOT)
                        shooted_wumpus.add(path[i+1].pos)
            # if there is only stench in a room, it shoots once time. Regardless whether any wumpus is dead after be shot or not,
            # the agent still ensure that the room is safe to go.
            else:
                if i != len(path) - 1:
                    if not path[i+1].percept:
                        continue
                    if 'K' in path[i+1].percept and path[i+1].pos not in shooted_wumpus:    
                        motions.append(Action.SHOOT)
                        shooted_wumpus.add(path[i+1].pos)
                    
            if 'W' in path[i].percept:
                motions.append(Action.EATEN_BY_WUMPUS)
                
            if 'P' in path[i].percept:
                motions.append(Action.FALL_INTO_PIT)
        
        return motions


    def search(self):
        """Search the world."""
        path = deque()
        inventory = set()
        memory = Map(self.world, self.current)
        shoot = {}
        self.__search(self.current, None, path, memory, inventory, self.world, self.kb, shoot)

        # for m in memory.data():
        #     for room in m:
        #         print(room.pos, " with ", room.wpos)

        routine = []
        goal = None
        stench_room = []
        stench_breeze_room = []
        breeze_room = []
        for room in path:
            if (room[0].wpos == (1,1)):
                goal = room[0]
            if 'B' in room[0].percept and 'S' in room[0].percept:
                stench_breeze_room.append(room[0])
            else:
                if 'B' in room[0].percept:
                    breeze_room.append(room[0])
                if 'S' in room[0].percept:
                    stench_room.append(room[0])
            routine.append(room[0])
        
        if goal: 
            path_to_exit = self.find_exit_path(memory, routine[-1], goal)
            path_to_exit.reverse()
            routine.extend(path_to_exit)
            action = self.convert_to_motions(routine)
            return routine, action, shoot
            
        # raw_neighbors = memory.get_nearby((10,3))
        # print("neighbors:  ", raw_neighbors)

        # path_to_exit = self.find_exit_path(memory, routine[-1], goal)
        # path_to_exit.reverse()
        # routine.extend(path_to_exit)


WORLD = World('resources/maps/map2.txt')
print(WORLD)
agent = Agent(WORLD)
routine, actionk, shoot = agent.search()
count = 0
if routine:
    for i in routine:
        action = [i.wpos]
        if i.wpos in shoot:
            action.append(shoot[i.wpos]) 
            del shoot[i.wpos]
        print(action)
if actionk:
    for a in actionk:
        print(a)        

# for row in m.data():
#     for room in row:
#         print("room: ", room.wpos)
#         count += 1
# print("map size: ", count)
