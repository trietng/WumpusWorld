# Some differences from the data structure used in the UI code:
# 1. The Grid is a 2D array of spots, with the starting point at the top left corner
# (0, 0). The coordinate system is (x, y) with x representing the row index and y
# representing the column index.
# 2. The world from the project's requirement is a 2D array, with the starting point
# at the bottom left corner (1, 1). The coordinate system is (i, j) with i
# representing the row index and j representing the column index.
# 3. The UI code uses a 2D array of spots to represent the grid, with the starting
# point at the top left corner (0, 0). The coordinate system is (i, j) with i
# representing the column index and j representing the row index.
# To make the UI code work with the world code, we need to convert the coordinate
# system from (x, y) to (i, j) and vice versa.
import pygame

pygame.init()

WIDTH = 600
HEIGHT = 600
WIN = pygame.display.set_mode((WIDTH + 300, WIDTH))
pygame.display.set_caption("Wumpus World")

# Colors:
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
BROWN = (165, 42, 42)

# Fonts:
font = pygame.font.SysFont('freesansbold', 24)

# Clock:
clock = pygame.time.Clock()


class Spot:
    def __init__(self, row, col, width, total_rows, total_cols, name=''):
        self.sprite__gold = None
        self.sprite__pit = None

        self.gap = gap_fn(total_rows, total_cols)
        self.sprite__wumpus = None
        self.visited = False
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.width = width
        self.total_rows = total_rows
        self.total_cols = total_cols
        self.x = col * width
        self.y = row * width
        self.name = name
        self.color = GREY
        self.load_sprite()

    def get_pos(self):
        return self.row, self.col

    def load_sprite(self):
        image = pygame.surface.Surface((self.width, self.width)).convert_alpha()

        image.fill(WHITE)
        self.sprite__gold = image.copy()
        self.sprite__pit = image.copy()
        self.sprite__wumpus = image.copy()
        self.sprite__gold.blit(pygame.image.load('assets/gold.png').convert_alpha(), (0, 0))
        self.sprite__pit.blit(pygame.image.load('assets/pit.png').convert_alpha(), (0, 0))
        self.sprite__wumpus.blit(pygame.image.load('assets/rip.png').convert_alpha(), (0, 0))

        self.sprite__gold = pygame.transform.scale(self.sprite__gold, (self.width, self.width))

    def draw(self, win, grid_start_x, grid_start_y):
        if self.name != '' and self.visited:
            pygame.draw.rect(win, WHITE, (self.x + grid_start_x, self.y + grid_start_y, self.width, self.width))
            if 'P' in self.name:
                win.blit(self.sprite__pit, (self.x + grid_start_x, self.y + grid_start_y))
            elif 'W' in self.name:
                win.blit(self.sprite__wumpus, (self.x + grid_start_x, self.y + grid_start_y))
            elif 'G' in self.name:
                win.blit(self.sprite__gold, (self.x + grid_start_x, self.y + grid_start_y))

            font_scale = pygame.font.SysFont('freesansbold', int((self.gap / 30) * 12))
            if 'B' in self.name:
                text = font_scale.render('Breeze', True, 'red')
                win.blit(text, (self.x + grid_start_x, self.y + grid_start_y))

            if 'S' in self.name:
                text = font_scale.render('Stench', True, 'blue')
                win.blit(text, (self.x + grid_start_x, self.y + grid_start_y + (self.gap / 30) * 12))

        else:
            if self.visited:
                self.color = WHITE
            else:
                self.color = GREY
            pygame.draw.rect(win, self.color, (self.x + grid_start_x, self.y + grid_start_y, self.width, self.width))


# SpriteSheet Class
class SpriteSheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale, colour):
        image = pygame.Surface((width, height)).convert_alpha()
        image.fill(colour)
        row = frame // 4
        col = frame % 4
        image.blit(self.sheet, (0, 0), (col * width, row * height, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(WHITE)

        return image


class Button:
    def __init__(self, txt, pos):
        self.text = txt
        self.pos = pos
        self.button = pygame.rect.Rect((self.pos[0], self.pos[1]), (260, 40))

    def draw(self):
        pygame.draw.rect(WIN, 'light gray', self.button, 0, 5)
        pygame.draw.rect(WIN, 'dark gray', [self.pos[0], self.pos[1], 260, 40], 5, 5)
        text2 = font.render(self.text, True, 'black')
        WIN.blit(text2, (self.pos[0] + 15, self.pos[1] + 7))

    def check_clicked(self):
        if self.button.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            return True
        else:
            return False


# Player Class
class Sprite:
    visual_grid = None

    def __init__(self, x, y, rows, columns, grid_start_x, grid_start_y):
        self.blit = None
        self.gap = gap_fn(rows, columns)
        self.x = int(x) * self.gap
        self.y = int(y) * self.gap
        self.rows = rows
        self.columns = columns
        self.grid_start_x = grid_start_x
        self.grid_start_y = grid_start_y
        self.color = (250, 120, 60)
        self.velX = 0
        self.velY = 0
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.shoot = False
        self.speed = 0
        self.status = 'R'
        self.spriteSheet = SpriteSheet(pygame.image.load('assets/sprite.png').convert_alpha())

    def set_visited(self):
        self.visual_grid[self.x // self.gap][self.y // self.gap].visited = True

    def get_pos(self):
        return self.x, self.y

    def draw_player(self):

        if self.status == 'D':
            self.blit = self.spriteSheet.get_image(0, 64, 64, self.gap / 64, WHITE)
        elif self.status == 'L':
            self.blit = self.spriteSheet.get_image(4, 64, 64, self.gap / 64, WHITE)
        elif self.status == 'R':
            self.blit = self.spriteSheet.get_image(8, 64, 64, self.gap / 64, WHITE)
        elif self.status == 'U':
            self.blit = self.spriteSheet.get_image(12, 64, 64, self.gap / 64, WHITE)

    def draw(self):
        self.draw_player()
        WIN.blit(self.blit, (self.y + self.grid_start_y, self.x + self.grid_start_x))

    def update(self, shoot_coord=None):
        self.velX = 0
        self.velY = 0

        self.speed = self.gap
        if self.left_pressed and not self.right_pressed:
            if self.status != 'L':
                self.status = 'L'
                self.set_visited()
                self.draw_player()
                # self.update()

                return True
            else:
                self.velY = -self.speed
        if self.right_pressed and not self.left_pressed:
            if self.status != 'R':
                self.status = 'R'
                self.set_visited()
                self.draw_player()

                # self.update()
                return True
            else:
                self.velY = self.speed
        if self.up_pressed and not self.down_pressed:
            if self.status != 'U':
                self.status = 'U'
                self.set_visited()
                self.draw_player()
                # self.update()
                return True
            else:
                self.velX = -self.speed
        if self.down_pressed and not self.up_pressed:
            if self.status != 'D':
                self.status = 'D'
                self.set_visited()
                self.draw_player()
                # self.update()
                return True
            else:
                self.velX = self.speed

        # corX, corY = 0, 0
        # print(shoot_coord)
        if self.shoot:
            if shoot_coord[0] < shoot_coord[2][0]:
                self.status = 'U'
            elif shoot_coord[0] > shoot_coord[2][0]:
                self.status = 'D'
            elif shoot_coord[1] < shoot_coord[2][1]:
                self.status = 'L'
            elif shoot_coord[1] > shoot_coord[2][1]:
                self.status = 'R'

            if 'W' in self.visual_grid[shoot_coord[0]][shoot_coord[1]].name:
                print("Shoot coord")
                print(shoot_coord)
                if shoot_coord[0] + 1 < self.rows:
                    self.visual_grid[shoot_coord[0] + 1][shoot_coord[1]].name \
                        = self.visual_grid[shoot_coord[0] + 1][shoot_coord[1]].name.replace('S', '', 1)
                    print(self.visual_grid[shoot_coord[0] + 1][shoot_coord[1]].name)
                if shoot_coord[0] - 1 >= 0:
                    self.visual_grid[shoot_coord[0] - 1][shoot_coord[1]].name \
                        = self.visual_grid[shoot_coord[0] - 1][shoot_coord[1]].name.replace('S', '', 1)
                    print(self.visual_grid[shoot_coord[0] - 1][shoot_coord[1]].name)
                if shoot_coord[1] + 1 < self.columns:
                    self.visual_grid[shoot_coord[0]][shoot_coord[1] + 1].name \
                        = self.visual_grid[shoot_coord[0]][shoot_coord[1] + 1].name.replace('S', '', 1)
                    print(self.visual_grid[shoot_coord[0]][shoot_coord[1] + 1].name)
                if shoot_coord[1] - 1 >= 0:
                    self.visual_grid[shoot_coord[0]][shoot_coord[1] - 1].name \
                        = self.visual_grid[shoot_coord[0]][shoot_coord[1] - 1].name.replace('S', '', 1)
                    print(self.visual_grid[shoot_coord[0]][shoot_coord[1] - 1].name)

                # self.visual_grid[self.x // self.gap + corX][self.y // self.gap + corY].name.replace('W', '')

        # print(self.velX, self.velY)
        self.x += self.velX
        self.y += self.velY
        self.set_visited()
        # print(self.x, self.y)

        self.draw_player()

        return False


def gap_fn(rows, column):
    if rows >= column:
        gap = WIDTH // rows
    else:
        gap = WIDTH // column
    return gap


def make_grid(rows, column):
    grid = []
    gap = gap_fn(rows, column)
    # UI.gap = gap
    # print(UI.gap)
    for i in range(rows):
        grid.append([])
        for j in range(column):
            spot = Spot(i, j, gap, rows, column, )
            grid[i].append(spot)
    return grid


def draw_grid(rows, column, grid_start_x, grid_start_y):
    gap = gap_fn(rows, column)
    for i in range(rows + 1):
        pygame.draw.line(WIN, BLACK, (grid_start_x, grid_start_y + i * gap),
                         (grid_start_x + column * gap, grid_start_y + i * gap))
        for j in range(column + 1):
            pygame.draw.line(WIN, BLACK, (j * gap + grid_start_x, grid_start_y),
                             (grid_start_x + j * gap, grid_start_y + rows * gap))


def draw(grid, rows, column, grid_start_x, grid_start_y):
    # win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(WIN, grid_start_x, grid_start_y)

    draw_grid(rows, column, grid_start_x, grid_start_y)

    # if not menu:
    # pygame.display.update()


def draw_menu():
    WIN.fill(WHITE)
    command = -1
    pygame.draw.rect(WIN, 'black', [100, 100, 300, 320])
    pygame.draw.rect(WIN, 'green', [100, 100, 300, 320], 5)
    pygame.draw.rect(WIN, 'white', [120, 120, 260, 40], 0, 5)
    pygame.draw.rect(WIN, 'gray', [120, 120, 260, 40], 5, 5)
    text = font.render('Wumpus World', True, 'black')

    WIN.blit(text, (135, 127))
    button1 = Button('Play game', (120, 200))
    button2 = Button('Load Map', (120, 260))

    button1.draw()
    button2.draw()

    if button1.check_clicked():
        command = 1
    elif button2.check_clicked():
        command = 2

    return command


def draw_menu_ingame():
    # WIN.fill(WHITE)
    # WIN.fill('white')
    command = -1
    exitButton = Button('Exit Menu', (620, 420))
    exitButton.draw()
    scoretxt = font.render('Score: ', True, 'black')
    WIN.blit(scoretxt, (620, 100))

    button1 = Button('Play game', (620, 180))
    button1.draw()

    if button1.check_clicked():
        command = 1
    elif exitButton.check_clicked():
        command = 0
    return command
