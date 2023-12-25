class WumpusWorld:
    def __init__(self, path: str):
        self.n, self.__world, self.agent, self.stenches = self.read_map(path)

    @classmethod
    def set_adjecent_rooms(cls, world, n, i, j, stenches):
        signal = 'B' if world[i][j] == 'P' else 'S'
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
        with open(path, 'r') as f:
            n = int(f.readline())
            world = [[room.replace('-', '') for room in f.readline().strip().replace(' ', '').split('.')] for _ in range(n)]
        agent = None
        stenches = {}
        for i in range(n):
            for j in range(n):
                if world[i][j] == 'P':
                    cls.set_adjecent_rooms(world, n, i, j, stenches)
                elif world[i][j] == 'W':
                    cls.set_adjecent_rooms(world, n, i, j, stenches)
                    x, y = n - i, j + 1
                    if (x, y) not in stenches:
                        stenches.update({(x, y): 1})
                    else:
                        stenches[(x, y)] += 1
                elif world[i][j] == 'A':
                    agent = n - i, j + 1
                    world[i][j] = world[i][j].replace('A', '')
        return n, world, agent, stenches

    def row(self, item):
        return self.__world[self.n - item]

    def col(self, item):
        return [self.__world[self.n - i][item - 1] for i in range(1, self.n + 1)]

    def __getitem__(self, item):
        assert isinstance(item, tuple) and len(item) == 2, 'Index must be a tuple of length 2'
        return self.__world[self.n - item[0]][item[1] - 1]

    def __setitem__(self, key, value):
        assert isinstance(key, tuple) and len(key) == 2, 'Index must be a tuple of length 2'
        self.__world[self.n - key[0]][key[1] - 1] = value

    def __str__(self):
        return f'N = {self.n}\n' + str(self.__world)

    def kill_wumpus(self, position):
        if 'W' not in self[position]:
            return False
        self[position] = self[position].replace('W', '')
        x, y = position
        print(self.stenches)
        if x > 1 and (x - 1, y) in self.stenches:
            print('nearby', (x - 1, y))
            self.stenches[(x - 1, y)] -= 1
            if self.stenches[(x - 1, y)] == 0:
                self.stenches.pop((x - 1, y))
                self[(x - 1, y)] = self[(x - 1, y)].replace('S', '')
        if x < self.n and (x + 1, y) in self.stenches:
            print('nearby', (x + 1, y))
            self.stenches[(x + 1, y)] -= 1
            if self.stenches[(x + 1, y)] == 0:
                self.stenches.pop((x + 1, y))
                self[(x + 1, y)] = self[(x + 1, y)].replace('S', '')
        if y > 1 and (x, y - 1) in self.stenches:
            print('nearby', (x, y - 1))
            self.stenches[(x, y - 1)] -= 1
            if self.stenches[(x, y - 1)] == 0:
                self.stenches.pop((x, y - 1))
                self[(x, y - 1)] = self[(x, y - 1)].replace('S', '')
        if y < self.n and (x, y + 1) in self.stenches:
            print('nearby', (x, y + 1))
            self.stenches[(x, y + 1)] -= 1
            if self.stenches[(x, y + 1)] == 0:
                self.stenches.pop((x, y + 1))
                self[(x, y + 1)] = self[(x, y + 1)].replace('S', '')
        return True

    def get_adjacents(self, position):
        adjacents = []
        x, y = position
        if y < self.n:
            adjacents.append((x, y + 1))
        if x > 1:
            adjacents.append((x - 1, y))
        if y > 1:
            adjacents.append((x, y - 1))
        if x < self.n:
            adjacents.append((x + 1, y))
        return adjacents