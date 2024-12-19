import pygame
import random
import sys

pygame.init()
# Pygame Configuration
MARGIN = 1
PANEL_HEIGHT = 150
SCREEN_PADDING = 100
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
COLOR_1 = (137, 243, 54)  # Vert clair
COLOR_2 = (105, 217, 45)  # Vert foncé

# Variables pour la gestion de la difficulté
difficulte_value = "1"  # Valeur par défaut de la difficulté

def set_difficulty(value):
    global difficulte_value
    difficulte_value = value

def get_difficulty():
    return int(difficulte_value)

# Classe Tableau pour gérer la logique du jeu
class Tableau:
    def __init__(self, tableau_data=None):
        """Si tableau_data est passé, il est utilisé pour initialiser le tableau. Sinon, on initialise un tableau vide."""
        if tableau_data:
            self.tableau = tableau_data
        else:
            self.reset()

        self.h = len(self.tableau)
        self.l = len(self.tableau[0]) if self.h > 0 else 0
        self.tableau_resolve = [["x" for _ in range(self.l)] for _ in range(self.h)]
        self.flags_left = self.tableau.count('B')  # Le nombre de bombes est compté dans le tableau
        self.start_time = None
        self.timer = "00:00"
        self.final = "0000"
        self.game_over = False
        self.victory = False
        self.first_click = False
        self.first_click_pos = None

        # Définir CELL_SIZE en fonction de la difficulté
        d = get_difficulty()
        if d == 3:
            self.CELL_SIZE = 23
        elif d == 1:
            self.CELL_SIZE = 40
        elif d == 2:
            self.CELL_SIZE = 23
        elif d == 0:
            self.CELL_SIZE = 25
        else:
            self.CELL_SIZE = 30  # Valeur par défaut au cas où

    def reset(self):
        """Initialise ou réinitialise le tableau de jeu."""
        self.h = 16
        self.l = 30
        self.bomb = 99  
        self.CELL_SIZE = 23 
        
        # Générer un tableau vide par défaut
        self.tableau = [["x" for _ in range(self.l)] for _ in range(self.h)]
        self.tableau_resolve = [["x" for _ in range(self.l)] for _ in range(self.h)]

        self.flags_left = self.bomb
        self.start_time = None
        self.timer = "00:00"
        self.final = "0000"
        self.game_over = False
        self.victory = False
        self.first_click = False
        self.first_click_pos = None

    def count_adjacent_bombs(self, pos1, pos2):
        count = 0
        for i in range(pos1 - 1, pos1 + 2):
            for j in range(pos2 - 1, pos2 + 2):
                if 0 <= i < self.h and 0 <= j < self.l and (i != pos1 or j != pos2):
                    if self.tableau[i][j] == "B":
                        count += 1
        return count

    def reveal(self, pos1, pos2):
        if self.tableau[pos1][pos2] != "x" or self.game_over:
            return

        adjacent_bombs = self.count_adjacent_bombs(pos1, pos2)
        if adjacent_bombs == 0:
            self.tableau[pos1][pos2] = "0"
            for i in range(pos1 - 1, pos1 + 2):
                for j in range(pos2 - 1, pos2 + 2):
                    if 0 <= i < self.h and 0 <= j < self.l and (i != pos1 or j != pos2):
                        self.reveal(i, j)
        else:
            self.tableau[pos1][pos2] = str(adjacent_bombs)

    def append(self, pos1, pos2):
        if self.game_over or not (0 <= pos1 < self.h and 0 <= pos2 < self.l):
            return True

        if not self.first_click:
            self.first_click_pos = (pos1, pos2)
            self.first_click = True
            # Pas de génération de bombes ici, on utilise directement le tableau fourni

            # Initialiser le timer au premier clic
            self.start_time = pygame.time.get_ticks()

        if self.tableau_resolve[pos1][pos2] == "B":
            self.game_over = True
            return False

        self.reveal(pos1, pos2)
        return True

    def check_victory(self):
        for i in range(self.h):
            for j in range(self.l):
                if self.tableau[i][j] == "x" and self.tableau_resolve[i][j] != "B":
                    return False
        self.victory = True
        return True

# Fonction d'affichage de la grille
def display_custom_tableau(tableau_data):
    if isinstance(tableau_data, Tableau):
        game = tableau_data
    else:
        game = Tableau(tableau_data)

    print(f"Tableau reçu : {game.tableau}")
    print(f"Dimensions : largeur={game.l}, hauteur={game.h}")

    screen_width = 1200
    screen_height = game.h * game.CELL_SIZE + PANEL_HEIGHT + SCREEN_PADDING * 2
    print(f"Dimensions de l'écran : {screen_width}x{screen_height}")

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Ines et les 40 bombes")

    font = pygame.font.Font(None, 36)
    alert_font = pygame.font.Font(None, 72)


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Dessinez le tableau ici
        for y, row in enumerate(game.tableau):
            for x, cell in enumerate(row):
                if cell == 'B':  # Bombe
                    pygame.draw.rect(screen, (255, 0, 0), (x * game.CELL_SIZE, y * game.CELL_SIZE, game.CELL_SIZE, game.CELL_SIZE))
                else:
                    pygame.draw.rect(screen, (0, 255, 0), (x * game.CELL_SIZE, y * game.CELL_SIZE, game.CELL_SIZE, game.CELL_SIZE))

        pygame.display.flip()
    pygame.quit()

