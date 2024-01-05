import ui
import pygame
import game
import tkinter
import tkinter.filedialog

def prompt_file():
    """Create a Tk file dialog and cleanup when finished"""
    top = tkinter.Tk()
    top.withdraw()  # hide window
    file_name = tkinter.filedialog.askopenfilename(parent=top)
    top.destroy()
    return file_name

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
                    # print("Play game")
                    # url = prompt_file()
                    url = '../resources/maps/map2.txt'
                    game.main(url)

        # pygame.time.delay(100)
        pygame.display.flip()


main()
