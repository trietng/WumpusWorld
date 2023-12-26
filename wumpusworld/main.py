import ui
import pygame
import game

def main():
    run = True
    while run:
        menu_command = ui.draw_menu()
        # print(menu_command)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if pygame.MOUSEBUTTONDOWN:
                if menu_command == 1:
                    print("Play game")
                    game.main()

        # pygame.time.delay(100)
        pygame.display.flip()


main()
