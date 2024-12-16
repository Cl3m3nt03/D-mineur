import pygame
import pygame_menu

pygame.init()
surface = pygame.display.set_mode((1280, 720))

def set_difficulty(value, difficulty):
    # Do the job here !
    pass

def start_the_game():
    # Do the job here !
    pass

menu = pygame_menu.Menu('Welcome', 1280, 720,
    theme=pygame_menu.themes.THEME_BLUE)

menu.add.text_input('Name :', default='Your Name')
menu.add.selector('Difficulty :', [('Hard', 1), ('Easy', 2)], onchange=set_difficulty)
menu.add.button('Play', start_the_game)
menu.add.button('Quit', pygame_menu.events.EXIT)

menu.mainloop(surface)