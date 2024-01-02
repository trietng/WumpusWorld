from enum import Enum


class Direction(Enum):
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    UP = 4


class WumpusWorld:
    def __init__(self, path: str):
        """Initialize the world.
        :param path: path to the map file
        """
        self.n, self.__world, self.agent, self.stenches = self.read_map(path)

    @classmethod
    def __set_adjecent_rooms(cls, world, n: int, i: int, j: int, stenches: dict):
        """Set percepts of adjacent rooms.
        :param world: the world
        :param n: size of the world
        :param i: row index of the room
        :param j: column index of the room
        :param stenches: a dictionary data structure to keep track of stenches
        """
        signal = ''
        if 'W' in world[i][j]:
            signal = 'S'
        elif 'P' in world[i][j]:
            print(world[i][j])
            signal = 'B'
        assert signal != '', 'Invalid percept'
        if i > 0:
            x, y = n - i + 1, j + 1
            if signal == 'S':
                if (x, y) not in stenches:
                    world[i - 1][j] += signal
                    stenches.update({(x, y): 1})
                else:
                    stenches[(x, y)] += 1
            else:
                if signal not in world[i - 1][j]:
                    world[i - 1][j] += signal
        if i < n - 1:
            if signal == 'S':
                x, y = n - i - 1, j + 1
                if (x, y) not in stenches:
                    world[i + 1][j] += signal
                    stenches.update({(x, y): 1})
                else:
                    stenches[(x, y)] += 1
            else:
                if signal not in world[i + 1][j]:
                    world[i + 1][j] += signal
        if j > 0:
            if signal == 'S':
                x, y = n - i, j
                if (x, y) not in stenches:
                    world[i][j - 1] += signal
                    stenches.update({(x, y): 1})
                else:
                    stenches[(x, y)] += 1
            else:
                if signal not in world[i][j - 1]:
                    world[i][j - 1] += signal
        if j < n - 1:
            if signal == 'S':
                x, y = n - i, j + 2
                if (x, y) not in stenches:
                    world[i][j + 1] += signal
                    stenches.update({(x, y): 1})
                else:
                    stenches[(x, y)] += 1
            else:
                if signal not in world[i][j + 1]:
                    world[i][j + 1] += signal

    @classmethod
    def read_map(cls, path: str):
        """Read the map from file. Should be only called by the constructor.
        :param path: path to the map file
        :returns: a tuple of (n, world, agent, stenches)
        """
        with open(path, 'r') as f:
            n = int(f.readline())
            world = [[room.replace('-', '') for room in f.readline().strip().replace(' ', '').split('.')] for _ in
                     range(n)]
        agent = None
        stenches = {}
        for i in range(n):
            for j in range(n):
                if 'P' in world[i][j]:
                    cls.__set_adjecent_rooms(world, n, i, j, stenches)
                elif 'W' in world[i][j]:
                    cls.__set_adjecent_rooms(world, n, i, j, stenches)
                elif 'A' in world[i][j]:
                    agent = n - i, j + 1
                    world[i][j] = world[i][j].replace('A', '')
        return n, world, agent, stenches

    def row(self, item):
        """Get a row of the world.
        :param item: index of the row
        :returns: an array of rooms
        """
        return self.__world[self.n - item]

    def col(self, item):
        """Get a column of the world.
        :param item: index of the column
        :returns: an array of rooms
        """
        return [self.__world[self.n - i][item - 1] for i in range(1, self.n + 1)]

    def __getitem__(self, item):
        """Get a room at position (x, y).
        :param item: position of the room
        :returns: a string representation of all percepts in the room
        :raises AssertionError: if item is not a tuple of length 2
        """
        assert isinstance(item, tuple) and len(item) == 2, 'Index must be a tuple of length 2'
        return self.__world[self.n - item[0]][item[1] - 1]

    def __setitem__(self, key, value):
        """Set a room at position (x, y).
        :param key: position of the room
        :param value: a string representation of all percepts in the room
        :raises AssertionError: if key is not a tuple of length 2
        """
        assert isinstance(key, tuple) and len(key) == 2, 'Index must be a tuple of length 2'
        self.__world[self.n - key[0]][key[1] - 1] = value

    def __str__(self):
        return f'N = {self.n}\n' + str(self.__world)

    def pickup_gold(self, position):
        if 'G' not in self[position]:
            return False
        self[position] = self[position].replace('G', 'E')
        return True

    def kill_wumpus(self, position):
        if 'W' not in self[position]:
            return False
        self[position] = self[position].replace('W', 'K')
        x, y = position
        if x > 1 and (x - 1, y) in self.stenches:
            self.stenches[(x - 1, y)] -= 1
            if self.stenches[(x - 1, y)] == 0:
                self.stenches.pop((x - 1, y))
                self[(x - 1, y)] = self[(x - 1, y)].replace('S', '')
        if x < self.n and (x + 1, y) in self.stenches:
            self.stenches[(x + 1, y)] -= 1
            if self.stenches[(x + 1, y)] == 0:
                self.stenches.pop((x + 1, y))
                self[(x + 1, y)] = self[(x + 1, y)].replace('S', '')
        if y > 1 and (x, y - 1) in self.stenches:
            self.stenches[(x, y - 1)] -= 1
            if self.stenches[(x, y - 1)] == 0:
                self.stenches.pop((x, y - 1))
                self[(x, y - 1)] = self[(x, y - 1)].replace('S', '')
        if y < self.n and (x, y + 1) in self.stenches:
            self.stenches[(x, y + 1)] -= 1
            if self.stenches[(x, y + 1)] == 0:
                self.stenches.pop((x, y + 1))
                self[(x, y + 1)] = self[(x, y + 1)].replace('S', '')
        return True

    def get_adjacents(self, position):
        """Get adjacent positions of a room.
        :param position: position of the room
        :returns: an array of valid adjacent positions
        """
        adjacents = []
        x, y = position
        if y < self.n:
            adjacents.append((Direction.RIGHT, x, y + 1))
        if x > 1:
            adjacents.append((Direction.DOWN, x - 1, y))
        if y > 1:
            adjacents.append((Direction.LEFT, x, y - 1))
        if x < self.n:
            adjacents.append((Direction.UP, x + 1, y))
        return adjacents
