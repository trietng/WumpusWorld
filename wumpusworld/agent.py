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
        self.child = None

    @classmethod
    def __find_nearest(cls, room, percept, path: deque, visited: set):
        """Internal method to find the nearest room with the input percept in it."""
        if room is None or id(room) in visited:
            return False
        visited.add(id(room))
        if percept in room.percept:
            path.append(room)
            return True
        if cls.__find_nearest(room.parent, percept, path, visited):
            path.appendleft(room)
            return True
        if cls.__find_nearest(room.child, percept, path, visited):
            path.appendleft(room)
            return True
        return False

    def find_nearest_stench(self):
        """Find the nearest room with a stench from a given room."""
        path = deque()
        self.__find_nearest(self, 'S', path, set())
        if len(path) > 0:
            path.pop()
        return path

    def find_nearest_breeze(self):
        """Find the nearest room with a breeze from a given room."""
        path = deque()
        self.__find_nearest(self, 'B', path, set())
        if len(path) > 0:
            path.pop()
        return path

    def __str__(self):
        return f'{self.position} {self.percept}'


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
        # print(room.position, room.percept, room.parent.position if room.parent is not None else None)
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
        backtrack = False
        if len(adjacents) == 0:
            if any(value is False for value in explored.values()):
                adjacents = visited_adjacents
                backtrack = True
            else:
                path.append(room)
                stench_path = room.find_nearest_stench()
                if len(stench_path) > 0:
                    path.extend(stench_path)
                else:
                    breeze_path = room.find_nearest_breeze()
                    path.extend(breeze_path)
                return True
        else:
            for adjacent in adjacents:
                if adjacent not in explored:
                    explored.update({adjacent: False})
        room.child = Room(adjacents[0], world[adjacents[0]], room)
        if backtrack:
            index = adjacents.index(room.parent.position)
            parent = adjacents[index]
            room.child = Room(parent, world[parent], room)
        if cls.__search(room.child, path, visited, explored, world, kb):
            path.appendleft(room)
            return True
        return False

    def __leap_of_faith(self, room, path: deque, world: World, kb: KnowledgeBase):
        pass

    def search(self):
        """Search the world."""
        path = deque()
        self.__search(self.current, path, set(), {}, self.world, self.kb)
        return path

WORLD = World('resources/maps/map1.txt')
print(WORLD)
agent = Agent(WORLD)
v = agent.search()
for i in v:
    print(i.position, i.percept)