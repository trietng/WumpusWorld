import ui
import pygame
import agent as Agent


class Visualizer:
    visual_grid = None
    agent = None
    shot = 0

    @staticmethod
    def convert_x_coord_to_ui(x):
        return 10 - x

    @staticmethod
    def convert_y_coord_to_ui(y):
        return y - 1


def move_player(player, action, shoot, shoot_keys):
    if action == Agent.Action.MOVE_LEFT:
        player.left_pressed = True
    if action == Agent.Action.MOVE_RIGHT:
        player.right_pressed = True
    if action == Agent.Action.MOVE_UP:
        player.up_pressed = True
    if action == Agent.Action.MOVE_DOWN:
        player.down_pressed = True

    is_moved = player.update()

    # draw
    ui.draw(Visualizer.visual_grid, 10, 10, 0, 0)
    player.draw()
    pygame.display.flip()
    pygame.time.delay(100)

    if is_moved:
        player.update()
        # draw
        ui.draw(Visualizer.visual_grid, 10, 10, 0, 0)
        player.draw()
        pygame.display.flip()
        pygame.time.delay(100)

    if action == Agent.Action.SHOOT:
        # print(shoot)
        player.shoot = True
        shoot_key = shoot_keys[Visualizer.shot]
        for shot in shoot[Visualizer.shot]:
            player.update((Visualizer.convert_x_coord_to_ui(shot[0]), Visualizer.convert_y_coord_to_ui(shot[1]),
                           (Visualizer.convert_x_coord_to_ui(shoot_key[0]),
                            Visualizer.convert_y_coord_to_ui(shoot_key[1]))))
            # draw
            ui.draw(Visualizer.visual_grid, 10, 10, 0, 0)
            player.draw()
            pygame.display.flip()
            pygame.time.delay(500)

        Visualizer.shot += 1

    player.left_pressed = False
    player.right_pressed = False
    player.up_pressed = False
    player.down_pressed = False
    player.shoot = False


def set_world(World):
    world = World.get_world()
    print(world)
    for i in range(World.n):
        for j in range(World.n):
            if 'S' not in world[i][j]:
                Visualizer.visual_grid[i][j].name += world[i][j]
            if 'S' in world[i][j]:
                if 'W' in world[i][j]:
                    Visualizer.visual_grid[i][j].name += 'W'
                if 'P' in world[i][j]:
                    Visualizer.visual_grid[i][j].name += 'P'
                if 'G' in world[i][j]:
                    Visualizer.visual_grid[i][j].name += 'G'
                if 'B' in world[i][j]:
                    Visualizer.visual_grid[i][j].name += 'B'

            if 'W' in world[i][j]:
                if i - 1 >= 0:
                    Visualizer.visual_grid[i - 1][j].name += 'S'
                if i + 1 < World.n:
                    Visualizer.visual_grid[i + 1][j].name += 'S'
                if j - 1 >= 0:
                    Visualizer.visual_grid[i][j - 1].name += 'S'
                if j + 1 < World.n:
                    Visualizer.visual_grid[i][j + 1].name += 'S'

            if world[i][j] == 'A':
                Visualizer.agent = (i, j)

    for i in range(World.n):
        for j in range(World.n):
            if Visualizer.visual_grid[i][j].name == '':
                print('0', end=' ')
            print(Visualizer.visual_grid[i][j].name, end=' ')
        print('\n')


def play_game(player, World):
    agent = Agent.Agent(World)

    routine, actionk, shoot = agent.search()
    count = 0
    move = []
    shoot_list = list(shoot.values())
    shoot_keys = list(shoot.keys())

    if routine:
        for i in routine:
            action = [i.wpos]
            if i.wpos in shoot:
                action.append(shoot[i.wpos])
                del shoot[i.wpos]
            # print(action)

            move.append(action)
    # print(move)
    # print(shoot)
    print(shoot_list)
    if actionk:
        for i in range(len(actionk)):
            move_player(player, actionk[i], shoot_list, shoot_keys)


def setup_world():
    World = Agent.World('../resources/maps/map5.txt')
    set_world(World)
    # print(World.agent)
    player = ui.Sprite(10 - World.agent[0], World.agent[1] - 1, 10, 10, 0, 0)
    player.visual_grid = Visualizer.visual_grid
    player.set_visited()
    ui.draw(Visualizer.visual_grid, 10, 10, 0, 0)
    player.draw()
    return player, World


def main():
    run = True
    visual_grid = ui.make_grid(10, 10)
    Visualizer.visual_grid = visual_grid

    # Player Initialization
    setup_world()
    play_again = False

    while run:
        # if play_again:
        #     # Player Initialization
        #     play_again = False
        #     World = Agent.World('../resources/maps/map2.txt')
        #     set_world(World)
        #     print(World.agent)
        #     player = ui.Sprite(10 - World.agent[0], World.agent[1] - 1, 10, 10, 0, 0)
        #     player.visual_grid = visual_grid
        #     player.set_visited()
        #     ui.draw(visual_grid, 10, 10, 0, 0)
        #     player.draw()
        #
        #     # pygame.display.flip()
        #     # clock = pygame.time.Clock()
        #     # clock.tick(120)
        command = ui.draw_menu_ingame()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_LEFT:
            #         player.left_pressed = True
            #     if event.key == pygame.K_RIGHT:
            #         player.right_pressed = True
            #     if event.key == pygame.K_UP:
            #         player.up_pressed = True
            #     if event.key == pygame.K_DOWN:
            #         player.down_pressed = True
            #     player.update()
            #     print(player.x, player.y)
            #
            # if event.type == pygame.KEYUP:
            #     if event.key == pygame.K_LEFT:
            #         player.left_pressed = False
            #     if event.key == pygame.K_RIGHT:
            #         player.right_pressed = False
            #     if event.key == pygame.K_UP:
            #         player.up_pressed = False
            #     if event.key == pygame.K_DOWN:
            #         player.down_pressed = False
            #     player.update()
            #     print(player.x, player.y)

            if pygame.MOUSEBUTTONDOWN:
                if command == 0:
                    run = False
                if command == 1:
                    Visualizer.visual_grid = ui.make_grid(10, 10)
                    Visualizer.shot = 0
                    player, World = setup_world()
                    play_game(player, World)
                    play_again = True

        # draw
        # ui.draw(visual_grid, 10, 10, 0, 0)
        # player.draw()

        # update
        pygame.time.delay(100)
        pygame.display.flip()
        ui.clock.tick(120)
