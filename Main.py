import pygame
import random
import sys

# Pygame Configuration
pygame.init()

# Dimensions et couleurs
MARGIN = 1  # Marges réduites pour une meilleure densité
PANEL_HEIGHT = 150
SCREEN_PADDING = 150
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
    def __init__(self):
        self.reset()

    def reset(self):
        """Initialise ou réinitialise le tableau de jeu."""
        d = get_difficulty()
        
        if d == 3:
            self.h = 16
            self.l = 30
            self.bomb = 99  
            self.CELL_SIZE = 17 
        elif d == 1:
            self.h = 9
            self.l = 9
            self.bomb = 10
            self.CELL_SIZE = 25 
        elif d == 2:
            self.h = 16
            self.l = 16
            self.bomb = 40
            self.CELL_SIZE = 20 
        elif d == 0:
            self.h = 4
            self.l = 4
            self.bomb = 1
            self.CELL_SIZE = 25 
        
        else:
            self.h = 0
            self.l = 0
            print("Choix invalide. Programme terminé.")
            exit()

        self.tableau = [["x" for _ in range(self.l)] for _ in range(self.h)]
        self.tableau_resolve = [["x" for _ in range(self.l)] for _ in range(self.h)]

        self.flags_left = self.bomb
        self.start_time = None
        self.timer = "00:00"
        self.game_over = False
        self.victory = False
        self.bombs_revealed = False

        # Placer les bombes
        placed_bombs = 0
        while placed_bombs < self.bomb:
            xbomb_pos = random.randint(0, self.h - 1)
            ybomb_pos = random.randint(0, self.l - 1)
            if self.tableau_resolve[xbomb_pos][ybomb_pos] != "B":
                self.tableau_resolve[xbomb_pos][ybomb_pos] = "B"
                placed_bombs += 1

    def count_adjacent_bombs(self, pos1, pos2):
        count = 0
        for i in range(pos1 - 1, pos1 + 2):
            for j in range(pos2 - 1, pos2 + 2):
                if 0 <= i < self.h and 0 <= j < self.l and (i != pos1 or j != pos2):
                    if self.tableau_resolve[i][j] == "B":
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

    def draw_replay_button(self, screen, font, screen_width, screen_height):
        replay_width = 180
        replay_height = 50
        replay_rect = pygame.Rect(
            screen_width // 2 - replay_width // 2,
            screen_height // 2 + 20,
            replay_width,
            replay_height,
        )
        pygame.draw.rect(screen, YELLOW, replay_rect)
        replay_text = font.render("Rejouer", True, BLACK)
        replay_text_rect = replay_text.get_rect(center=replay_rect.center)
        screen.blit(replay_text, replay_text_rect)

        return replay_rect

# Fonction pour dessiner les boutons de difficulté
def draw_difficulty_buttons():
    easy_button = pygame.Rect(50, 50, 100, 50)
    medium_button = pygame.Rect(50, 120, 100, 50)
    hard_button = pygame.Rect(50, 190, 100, 50)
    debug_button = pygame.Rect(50, 230, 100, 50)

    pygame.draw.rect(screen, YELLOW, easy_button)
    pygame.draw.rect(screen, YELLOW, medium_button)
    pygame.draw.rect(screen, YELLOW, hard_button)
    pygame.draw.rect(screen, YELLOW, debug_button)

    easy_text = font.render("Facile", True, BLACK)
    medium_text = font.render("Moyen", True, BLACK)
    hard_text = font.render("Difficile", True, BLACK)
    debug_text = font.render("debug", True, BLACK)

    screen.blit(easy_text, (easy_button.centerx - easy_text.get_width() // 2, easy_button.centery - easy_text.get_height() // 2))
    screen.blit(medium_text, (medium_button.centerx - medium_text.get_width() // 2, medium_button.centery - medium_text.get_height() // 2))
    screen.blit(hard_text, (hard_button.centerx - hard_text.get_width() // 2, hard_button.centery - hard_text.get_height() // 2))
    screen.blit(debug_text, (debug_button.centerx - debug_text.get_width() // 2, debug_button.centery - debug_text.get_height() // 2))

    return easy_button, medium_button, hard_button, debug_button

# Fonction pour gérer les clics sur les boutons de difficulté
def handle_difficulty_buttons():
    global game
    easy_button, medium_button, hard_button, debug_button = draw_difficulty_buttons()
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if pygame.mouse.get_pressed()[0]:
        if easy_button.collidepoint(mouse_x, mouse_y):
            set_difficulty("1")
            game.reset()
        elif medium_button.collidepoint(mouse_x, mouse_y):
            set_difficulty("2")
            game.reset()
        elif hard_button.collidepoint(mouse_x, mouse_y):
            set_difficulty("3")
            game.reset()
        elif debug_button.collidepoint(mouse_x, mouse_y):
            set_difficulty("0")
            game.reset()

# Initialiser le tableau de jeu
game = Tableau()
screen_width = 1200  # Changer la largeur à 500 pixels
screen_height = game.h * game.CELL_SIZE + PANEL_HEIGHT + SCREEN_PADDING * 2
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Démineur")

font = pygame.font.Font(None, 36)
alert_font = pygame.font.Font(None, 72)

# Calculer la marge gauche pour centrer la grille
left_margin = (screen_width - game.l * game.CELL_SIZE) // 2

# Charger l'image de fond
background_image = pygame.image.load("assets/Background.png")
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# Charger l'image de la bombe
bomb_image = pygame.image.load("assets/bomb.png")
bomb_image = pygame.transform.scale(bomb_image, (game.CELL_SIZE - MARGIN, game.CELL_SIZE - MARGIN))

# Boucle principale
running = True
while running:
    screen.blit(background_image, (0, 0))

    if game.start_time and not game.game_over and not game.victory:
        elapsed_time = (pygame.time.get_ticks() - game.start_time) // 1000
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        game.timer = f"{minutes:02}:{seconds:02}"

    if not game.game_over and not game.victory:
        for i in range(game.h):
            for j in range(game.l):
                rect = pygame.Rect(
                    left_margin + j * game.CELL_SIZE,
                    SCREEN_PADDING + i * game.CELL_SIZE,
                    game.CELL_SIZE - MARGIN,
                    game.CELL_SIZE - MARGIN,
                )

                cell_color = COLOR_1 if (i + j) % 2 == 0 else COLOR_2
                if game.tableau[i][j] == "x":
                    pygame.draw.rect(screen, cell_color, rect)
                elif game.tableau[i][j] == "0":
                    pygame.draw.rect(screen, WHITE, rect)
                elif game.tableau[i][j].isdigit():
                    pygame.draw.rect(screen, WHITE, rect)
                    text = font.render(game.tableau[i][j], True, BLACK)
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
                elif game.tableau[i][j] == "P":
                    pygame.draw.rect(screen, RED, rect)

    pygame.draw.rect(
        screen, BLACK, (0, screen_height - PANEL_HEIGHT, screen_width, PANEL_HEIGHT)
    )
    timer_text = font.render(f"Temps : {game.timer}", True, WHITE)
    flags_text = font.render(f"Drapeaux restants : {game.flags_left}", True, WHITE)
    screen.blit(timer_text, (SCREEN_PADDING + 20, screen_height - PANEL_HEIGHT + 20))
    screen.blit(flags_text, (SCREEN_PADDING + 20, screen_height - PANEL_HEIGHT + 70))

    handle_difficulty_buttons()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not game.game_over:
                if not game.start_time:
                    game.start_time = pygame.time.get_ticks()

                x, y = event.pos
                if y < game.h * game.CELL_SIZE + SCREEN_PADDING:
                    col = (x - left_margin) // game.CELL_SIZE
                    row = (y - SCREEN_PADDING) // game.CELL_SIZE
                    if event.button == 1:
                        game.game_over = not game.append(row, col)
                    elif event.button == 3:
                        if game.tableau[row][col] == "x" and game.flags_left > 0:
                            game.tableau[row][col] = "P"
                            game.flags_left -= 1
                        elif game.tableau[row][col] == "P":
                            game.tableau[row][col] = "x"
                            game.flags_left += 1
                    game.check_victory()

            if game.game_over or game.victory:
                replay_rect = game.draw_replay_button(screen, font, screen_width, screen_height)
                if replay_rect.collidepoint(event.pos):
                    game.reset()

    if game.game_over:
        alert_text = alert_font.render("PERDU !", True, RED)
        alert_rect = alert_text.get_rect(center=(screen_width // 2, screen_height // 3.5 ))
        screen.blit(alert_text, alert_rect)
        replay_rect = game.draw_replay_button(screen, font, screen_width, screen_height)

    if game.victory:
        alert_text = alert_font.render("VICTOIRE !", True, GREEN)
        alert_rect = alert_text.get_rect(center=(screen_width // 2, screen_height // 3.5))
        screen.blit(alert_text, alert_rect)
        replay_rect = game.draw_replay_button(screen, font, screen_width, screen_height)

    pygame.display.flip()

pygame.quit()
sys.exit()
