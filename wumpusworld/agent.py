class Agent:
    def __init__(self, n: int, position: (int, int)):
        self.position = position
        self.memory = [[set() for _ in range(n)] for _ in range(n)]
        self.score = 0
