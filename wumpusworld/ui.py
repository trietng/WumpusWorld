import tkinter
import tkinter.filedialog
import pygame
import copy
import os

pygame.init()

WIDTH = 600
HEIGHT = 600
WIN = pygame.display.set_mode((WIDTH + 300, WIDTH))
pygame.display.set_caption("Wumpus World")

# Colors:
WHITE = (255, 255, 255)
GREY = (128, 128, 128)

# Fonts:
font = pygame.font.SysFont('freesansbold', 24)

# Clock:
clock = pygame.time.Clock()


class Spot:
    def __init__(self, row, col, width, total_rows, total_cols, name=''):
        self.sprite__gold = None
        self.sprite__pit = None
        self.sprite__wumpus = None

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
        self.color = WHITE
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
        self.sprite__wumpus.blit(pygame.image.load('assets/wumpus.png').convert_alpha(), (0, 0))

        self.sprite__gold = pygame.transform.scale(self.sprite__gold, (self.width, self.width))

    def is_wumpus(self):
        return self.name == 'W'

    def is_pit(self):
        return self.name == 'P'

    def is_gold(self):
        return self.name == 'G'

    def draw(self, win, grid_start_x, grid_start_y):
        if self.name != '':
            if self.name == 'P':
                win.blit(self.sprite__pit, (self.x + grid_start_x, self.y + grid_start_y))
            elif self.name == 'W':
                win.blit(self.sprite__wumpus, (self.x + grid_start_x, self.y + grid_start_y))
            elif self.name == 'G':
                win.blit(self.sprite__gold, (self.x + grid_start_x, self.y + grid_start_y))
        else:
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
        self.speed = 0
        self.status = 'R'
        self.spriteSheet = SpriteSheet(pygame.image.load('assets/sprite.png').convert_alpha())

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
        WIN.blit(self.blit, (self.x + self.grid_start_x, self.y + self.grid_start_y))

    def update(self):
        self.velX = 0
        self.velY = 0

        self.speed = self.gap
        if self.left_pressed and not self.right_pressed:
            if self.status != 'L':
                self.status = 'L'
            else:
                self.velX = -self.speed
        if self.right_pressed and not self.left_pressed:
            if self.status != 'R':
                self.status = 'R'
            else:
                self.velX = self.speed
        if self.up_pressed and not self.down_pressed:
            if self.status != 'U':
                self.status = 'U'
            else:
                self.velY = -self.speed
        if self.down_pressed and not self.up_pressed:
            if self.status != 'D':
                self.status = 'D'
            else:
                self.velY = self.speed

        print(self.velX, self.velY)
        self.x += self.velX
        self.y += self.velY
        print(self.x, self.y)

        self.draw_player()


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
        pygame.draw.line(WIN, GREY, (grid_start_x, grid_start_y + i * gap),
                         (grid_start_x + column * gap, grid_start_y + i * gap))
        for j in range(column + 1):
            pygame.draw.line(WIN, GREY, (j * gap + grid_start_x, grid_start_y),
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
