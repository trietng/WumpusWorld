import ui
import pygame

def main():
    run = True
    visual_grid = ui.make_grid(10, 10)
    # Player Initialization
    player = ui.Sprite(0, 0, 10, 10, 0, 0)
    ui.draw(visual_grid, 10, 10, 0, 0)
    player.draw()

    pygame.display.flip()
    clock = pygame.time.Clock()
    clock.tick(120)
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.left_pressed = True
                if event.key == pygame.K_RIGHT:
                    player.right_pressed = True
                if event.key == pygame.K_UP:
                    player.up_pressed = True
                if event.key == pygame.K_DOWN:
                    player.down_pressed = True
                player.update()
                print(player.x, player.y)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player.left_pressed = False
                if event.key == pygame.K_RIGHT:
                    player.right_pressed = False
                if event.key == pygame.K_UP:
                    player.up_pressed = False
                if event.key == pygame.K_DOWN:
                    player.down_pressed = False
                player.update()
                print(player.x, player.y)

        # draw
        ui.draw(visual_grid, 10, 10, 0, 0)
        player.draw()

        # update
        pygame.display.flip()
        clock.tick(120)


