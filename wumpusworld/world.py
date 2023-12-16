class WumpusWorld:
    def __init__(self, path: str):
        self.n, self.__world = self.read_map(path)

    @classmethod
    def set_adjecent_rooms(cls, world, n, i, j):
        signal = 'B' if world[i][j] == 'P' else 'S'
        if i > 0:
            if signal not in world[i - 1][j]:
                world[i - 1][j] += signal
        if i < n - 1:
            if signal not in world[i + 1][j]:
                world[i + 1][j] += signal
        if j > 0:
            if signal not in world[i][j - 1]:
                world[i][j - 1] += signal
        if j < n - 1:
            if signal not in world[i][j + 1]:
                world[i][j + 1] += signal

    @classmethod
    def read_map(cls, path: str):
        with open(path, 'r') as f:
            n = int(f.readline())
            world = [[room.replace('-', '') for room in f.readline().strip().replace(' ', '').split('.')] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if world[i][j] == 'W' or world[i][j] == 'P':
                    cls.set_adjecent_rooms(world, n, i, j)
        return n, world

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