from collections import deque
from copy import deepcopy
from enum import Enum
from world import WumpusWorld as World
from sat_solver import KnowledgeBase


class Room:
    def __init__(self, position, percept: str, parent=None, child=None):
        self.position = position
        self.percept = percept
        self.parent = parent
        self.child = child

    @classmethod
    def __find_nearest(cls, room, goal, path: deque, visited: set):
        """Internal method to find the nearest room with the input percept in it."""
        if room is None or id(room) in visited:
            return False
        visited.add(id(room))
        newroom = Room(room.position, room.percept, room.parent, room.child)
        if goal == 'BS':
            if 'B' in room.percept and 'S' in room.percept:
                path.appendleft(newroom)
                return True
        elif goal == 'B':
            if 'B' in room.percept:
                path.appendleft(newroom)
                return True
        elif goal == 'S':
            if 'S' in room.percept:
                path.appendleft(newroom)
                return True
        elif goal == 'E':
            if room.position == (1, 1):
                path.appendleft(newroom)
                return True
        if cls.__find_nearest(room.parent, goal, path, visited):
            path.appendleft(newroom)
            return True
        if cls.__find_nearest(room.child, goal, path, visited):
            path.appendleft(newroom)
            return True
        return False

    def find_nearest(self, stench=False, breeze=False):
        """Find the nearest room with a stench or breeze from a given room."""
        assert stench or breeze, 'stench and breeze cannot be False at the same time'
        path = deque()
        if stench and breeze:
            self.__find_nearest(self, 'BS', path, set())
        elif stench:
            self.__find_nearest(self, 'S', path, set())
        elif breeze:
            self.__find_nearest(self, 'B', path, set())
        if len(path) > 0:
            path.popleft()
        if len(path) > 0:
            path[0].parent = self
            path[0].child = None
        if len(path) > 1:
            path[0].child = path[1]
            for i in range(1, len(path) - 1):
                path[i].parent = path[i - 1]
                path[i].child = path[i + 1]
            path[-1].parent = path[-2]
            path[-1].child = None
        return path

    def __str__(self):
        return f'{self.position} {self.percept}'

    @classmethod
    def remove_stenches(cls, path: list, target: list):
        """Remove stenches from the rooms."""
        for room in path:
            pointer = room[0]
            if pointer.position in target:
                pointer.percept = pointer.percept.replace('S', '')
                print('remove stench', pointer.position, pointer.percept)



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


class Agent:
    def __init__(self, world: World):
        self.world = world
        self.current = Room(world.agent, '')
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
        return result

    @classmethod
    def update(cls, kb, room, adjacents):
        """Update the knowledge base."""
        if 'P' in room.percept:
            pit_clause = {f'P{room.position}': 0}
        else:
            pit_clause = {f'P{room.position}': 1}
        kb.add_clause([pit_clause])

        if 'W' in room.percept:
            wumpus_clause = {f'W{room.position}': 0}
        else:
            wumpus_clause = {f'W{room.position}': 1}
        kb.add_clause([wumpus_clause])

        if 'B' in room.percept:
            # Breeze => Pup or Pdown or Pleft or Pright
            # not Breeze or Pup or Pdown or Pleft or Pright
            breeze_clause = {f'B{room.position}': 1}
            for adjacent in adjacents:
                breeze_clause.update({f'P{adjacent}': 0})
            kb.add_clause([breeze_clause])

        if 'S' in room.percept:
            # Stench => Wup or Wdown or Wleft or Wright
            stench_clause = {f'S{room.position}': 1}
            for adjacent in adjacents:
                stench_clause.update({f'P{adjacent}': 1})
            kb.add_clause([stench_clause])

        if room.percept == '':
            for adjacent in adjacents:
                # not Padj and not Wadj
                kb.add_clause([{f'P{adjacent}': 1}, {f'W{adjacent}': 1}])

    @classmethod
    def remove_wumpus(cls, kb, symbol):
        """Remove wumpus from the knowledge base."""
        kb.del_clause(symbol)

    @classmethod
    def __kill_wumpus(cls, room, path: list, visited: set, explored: dict, inventory: set, world: World,
                      kb: KnowledgeBase):
        """Internal method to kill the wumpus."""
        print(room.position, room.percept, room.parent.position if room.parent is not None else None)
        action = None
        adjacents = world.get_adjacents(room.position)
        adjacents = [adjacent for adjacent in adjacents if adjacent not in visited]
        if not cls.infer(kb, {f'W{adjacents[0]}': 1}):
            if world.kill_wumpus(adjacents[0]):
                cls.remove_wumpus(kb, f'W{adjacents[0]}')
                room.percept = world[room.position]
        elif cls.infer(kb, {f'W{adjacents[0]}': 0}):
            if world.kill_wumpus(adjacents[0]):
                cls.remove_wumpus(kb, f'W{adjacents[0]}')
                room.percept = world[room.position]
        if 'S' not in room.percept:
            adjacents = world.get_adjacents(adjacents[0])
            for adjacent in adjacents:
                explored.update({adjacent: False})
                visited.remove(adjacent)
            explored.update({room.position: True})
            visited.add(room.position)
            Room.remove_stenches(path, adjacents)
            cls.update(kb, room, adjacents)
            action = Action.SHOOT
        room.child = Room(adjacents[0], world[adjacents[0]], room)
        if cls.__search(room.child, path, visited, explored, inventory, world, kb, action):
            return True

    @classmethod
    def __search(cls, room, path: list, visited: set, explored: dict, inventory: set, world: World, kb: KnowledgeBase, action=None):
        """Internal method to search the world."""
        if room is None:
            return False
        path.append((room, room.position, deepcopy(room.percept)))
        print(room.position, room.percept, room.parent.position if room.parent is not None else None)
        if 'W' in room.percept:
            return True
        if 'P' in room.percept:
            return True
        if room.position == (1, 1):
            path.append(room)
            return True
        if 'G' in room.percept:
            room.percept = room.percept.replace('G', '')
            world.pickup_gold(room.position)
            inventory.add(room.position)
        adjacents = world.get_adjacents(room.position)
        adjacents = [adjacent for adjacent in adjacents if adjacent not in visited]
        if room.position not in visited:
            visited.add(room.position)
            cls.update(kb, room, adjacents)
        explored.update({room.position: True})
        invalids = set()
        if 'B' in room.percept:
            for adjacent in adjacents:
                if not cls.infer(kb, {f'P{adjacent}': 1}):
                    cls.update(kb, room, adjacents)
                    invalids.add(adjacent)
                else:
                    if cls.infer(kb, {f'P{adjacent}': 0}):
                        invalids.add(adjacent)
        adjacents = [adjacent for adjacent in adjacents if adjacent not in invalids]
        invalids.clear()
        if 'S' in room.percept:
            for adjacent in adjacents:
                if not cls.infer(kb, {f'W{adjacent}': 1}):
                    cls.update(kb, room, adjacents)
                    invalids.add(adjacent)
                else:
                    if cls.infer(kb, {f'W{adjacent}': 0}):
                        invalids.add(adjacent)
        adjacents = [adjacent for adjacent in adjacents if adjacent not in invalids]
        if len(adjacents) == 0:
            if any(value is False for value in explored.values()):
                if cls.__search(room.parent, path, visited, explored, inventory, world, kb):
                    return True
            else:
                xpath = []
                stench_path = room.find_nearest(stench=True)
                if len(stench_path) > 0:
                    xpath.extend(stench_path)
                else:
                    stench_and_breeze_path = room.find_nearest(stench=True, breeze=True)
                    if len(stench_and_breeze_path) > 0:
                        xpath.extend(stench_and_breeze_path)
                    else:
                        breeze_path = room.find_nearest(breeze=True)
                        if len(breeze_path) > 0:
                            xpath.extend(breeze_path)
                room = xpath[-1]
                for room in xpath:
                    path.append((room, room.position, deepcopy(room.percept)))
                if 'S' in room.percept:
                    if cls.__kill_wumpus(room, path, visited, explored, inventory, world, kb):
                        return True
                elif 'B' in room.percept:
                    if cls.__leap_of_faith(room, path, visited, explored, inventory, world, kb):
                        return True
                return False
        else:
            for adjacent in adjacents:
                if adjacent not in explored:
                    explored.update({adjacent: False})
        if len(adjacents) == 0:
            xpath = room.find_exit()
            if len(xpath) > 0:
                print(xpath)
                for room in xpath:
                    path.append((room, room.position, deepcopy(room.percept)))
                return True
            else:
                return False
        room.child = Room(adjacents[0], world[adjacents[0]], room)
        if cls.__search(room.child, path, visited, explored, inventory, world, kb):
            return True
        return False

    def __leap_of_faith(self, room, path: list, visited: set, explored: dict, inventory: set, world: World,
                        kb: KnowledgeBase):
        """Internal method to leap of faith."""
        adjacents = world.get_adjacents(room.position)
        adjacents = [adjacent for adjacent in adjacents if adjacent not in visited]
        room.child = Room(adjacents[0], world[adjacents[0]], room)
        explored.update({adjacents[0]: False})
        if self.__search(room.child, path, visited, explored, inventory, world, kb):
            return True


    def search(self):
        """Search the world."""
        path = []
        inventory = set()
        explored = {}
        visited = set()
        self.__search(self.current, path, visited, explored, inventory, self.world, self.kb)
        return path


WORLD = World('resources/maps/map1.txt')
print(WORLD)
agent = Agent(WORLD)
v = agent.search()
for i in v:
    print(i)