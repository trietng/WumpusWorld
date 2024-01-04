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


def move_player(player, action, move, index):
    if action == Agent.Action.MOVE_LEFT:
        player.left_pressed = True
    if action == Agent.Action.MOVE_RIGHT:
        player.right_pressed = True
    if action == Agent.Action.MOVE_UP:
        player.up_pressed = True
    if action == Agent.Action.MOVE_DOWN:
        player.down_pressed = True
    if action == Agent.Action.SHOOT:
        player.shoot = True
        Visualizer.shot += 1
        print(Visualizer.shot)


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



    player.left_pressed = False
    player.right_pressed = False
    player.up_pressed = False
    player.down_pressed = False
    player.shoot = False


def set_world(World):
    world = World.get_world()
    for i in range(World.n):
        for j in range(World.n):
            Visualizer.visual_grid[i][j].name += world[i][j]
            if world[i][j] == 'A':
                Visualizer.agent = (i, j)


def play_game(player, World):
    agent = Agent.Agent(World)

    routine, actionk, shoot = agent.search()
    count = 0
    move = []
    if routine:
        for i in routine:
            action = [i.wpos]
            if i.wpos in shoot:
                action.append(shoot[i.wpos])
                del shoot[i.wpos]
            print(action)
            move.append(action)
    print(move)
    print(actionk)
    if actionk:
        for i in range(len(actionk)):
            move_player(player, actionk[i], move, i)


def setup_world():
    World = Agent.World('../resources/maps/map2.txt')
    set_world(World)
    print(World.agent)
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
