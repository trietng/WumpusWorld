from collections import deque
from queue import LifoQueue
from copy import deepcopy
from enum import Enum
from world import WumpusWorld as World
from sat_solver import KnowledgeBase

class Room:
    def __init__(self, position, percept: str, parent=None):
        self.position = position
        self.percept = percept
        self.parent = parent
        self.children = []

    @classmethod
    def __find_nearest_stench(cls, room, path: deque, visited: set):
        """Internal method to find the nearest stench cell from a given cell."""
        if room is None or room.position in visited:
            return False
        visited.add(room.position)
        if 'S' in room.percept:
            path.append(room)
            return True
        for child in room.children:
            if cls.__find_nearest_stench(child, path, visited):
                path.appendleft(room)
                return True
        if cls.__find_nearest_stench(room.parent, path, visited):
            path.appendleft(room)
            return True
        return False

    def find_nearest_stench(self):
        """Find the nearest stench cell from a given cell."""
        path = deque()
        self.__find_nearest_stench(self, path, set())
        return path


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
        self.actions = []

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
    def __search(cls, room, path: deque, visited: set, explored: dict, world: World, kb: KnowledgeBase):
        """Internal method to search the world."""
        print(room.position, room.percept, room.parent.position if room.parent is not None else None)
        if room is None:
            return False
        if 'W' in room.percept:
            path.append(room)
            return True
        if 'P' in room.percept:
            path.append(room)
            return True
        if room.position == (1, 1):
            path.append(room)
            return True
        adjacents = world.get_adjacents(room.position)
        visited_adjacents = [adjacent for adjacent in adjacents if adjacent in visited]
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
                    if not cls.infer(kb, {f'P{adjacent}': 0}):
                        pass
                    else:
                        invalids.add(adjacent)
        adjacents = [adjacent for adjacent in adjacents if adjacent not in invalids]
        invalids.clear()
        if 'S' in room.percept:
            for adjacent in adjacents:
                if not cls.infer(kb, {f'W{adjacent}': 1}):
                    cls.update(kb, room, adjacents)
                    invalids.add(adjacent)
                else:
                    if not cls.infer(kb, {f'W{adjacent}': 0}):
                        pass
                    else:
                        invalids.add(adjacent)
        adjacents = [adjacent for adjacent in adjacents if adjacent not in invalids]
        if len(adjacents) == 0:
            if any(value is False for value in explored.values()):
                adjacents = visited_adjacents
            else:
                return True
        else:
            for adjacent in adjacents:
                if adjacent not in explored:
                    explored.update({adjacent: False})
        room.children = [Room(adjacent, world[adjacent], room) for adjacent in adjacents]
        for child in room.children:
            if cls.__search(child, path, visited, explored, world, kb):
                path.appendleft(room)
                return True
        return False

    def search(self):
        """Search the world."""
        path = deque()
        self.__search(self.current, path, set(), {}, self.world, self.kb)
        return path

# WORLD = World('resources/maps/map1.txt')
# print(WORLD)
# agent = Agent(WORLD)
# v = agent.search()