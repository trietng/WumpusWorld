class Agent:
    def __init__(self, n: int):
        self.position = (1, 1)
        self.memory = [[set() for _ in range(n)] for _ in range(n)]
        self.score = 0
