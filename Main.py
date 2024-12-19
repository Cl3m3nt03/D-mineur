import pygame
import random
import sys
from database import mycursor, mydb
from saves import get_pseudo_and_saves
from scoreboard import display_leaderboard

# Pygame Configuration
pygame.init()

# Dimensions et couleurs
MARGIN = 1  # Marges réduites pour une meilleure densité
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
    def __init__(self):
        self.reset()

    def reset(self, preset_tableau_resolve=None):
        """Initialise ou réinitialise le tableau de jeu."""
        d = get_difficulty()
        
        if d == 3:
            self.h = 16
            self.l = 30
            self.bomb = 99  
            self.CELL_SIZE = 23 
        elif d == 1:
            self.h = 9
            self.l = 9
            self.bomb = 10
            self.CELL_SIZE = 40
        elif d == 2:
            self.h = 16
            self.l = 16
            self.bomb = 40
            self.CELL_SIZE = 23
        elif d == 0:
            self.h = 10
            self.l = 10
            self.bomb = 3
            self.CELL_SIZE = 25 
        else:
            self.h = 0
            self.l = 0
            print("Choix invalide. Programme terminé.")
            exit()
        
        # Si un tableau prédéfini est fourni, on l'utilise
        if preset_tableau_resolve:
            self.tableau_resolve = preset_tableau_resolve
            self.bomb = sum(row.count("B") for row in preset_tableau_resolve)
            self.h = len(preset_tableau_resolve)  # Update height
            self.l = len(preset_tableau_resolve[0])  # Update width
        else:
            self.tableau_resolve = [["x" for _ in range(self.l)] for _ in range(self.h)]

        self.tableau = [["x" for _ in range(self.l)] for _ in range(self.h)]
        self.flags_left = self.bomb
        self.start_time = None
        self.timer = "00:00"
        self.final = "0000"
        self.game_over = False
        self.victory = False
        self.bombs_revealed = False
        self.first_click = False
        self.first_click_pos = None

        # Debugging: Print the tableau to check if it is reset correctly
        print("Tableau reset:")
        for row in self.tableau_resolve:
            print(row)

    def reset_bomb_placement(self, first_click_x, first_click_y):
        # Placer les bombes en évitant la zone autour du premier clique
        placed_bombs = 0
        while placed_bombs < self.bomb:
            xbomb_pos = random.randint(0, self.h - 1)
            ybomb_pos = random.randint(0, self.l - 1)

            if (self.tableau_resolve[xbomb_pos][ybomb_pos] != "B" and
                not (first_click_x - 1 <= xbomb_pos <= first_click_x + 1 and
                     first_click_y - 1 <= ybomb_pos <= first_click_y + 1)):
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
        if not self.first_click:
            self.first_click_pos = (pos1, pos2)
            self.first_click = True
            self.reset_bomb_placement(pos1, pos2)
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

    def draw_save_button(self, screen, font, screen_width, screen_height):
        save_width = 180
        save_height = 50
        save_rect = pygame.Rect(
            screen_width // 2 - save_width // 2,
            screen_height // 2 + 90,
            save_width,
            save_height,
        )
        pygame.draw.rect(screen, YELLOW, save_rect)
        save_text = font.render("Save", True, BLACK)
        save_text_rect = save_text.get_rect(center=save_rect.center)
        screen.blit(save_text, save_text_rect)
        return save_rect

def draw_difficulty_buttons():
    score_button = pygame.Rect(50, 120, 100, 50)
    easy_button = pygame.Rect(50, 190, 100, 50)
    medium_button = pygame.Rect(50, 260, 100, 50)
    hard_button = pygame.Rect(50, 330, 100, 50)
    debug_button = pygame.Rect(50, 400, 100, 50)
    
    pygame.draw.rect(screen, YELLOW, score_button)
    pygame.draw.rect(screen, YELLOW, easy_button)
    pygame.draw.rect(screen, YELLOW, medium_button)
    pygame.draw.rect(screen, YELLOW, hard_button)
    pygame.draw.rect(screen, YELLOW, debug_button)
    
    score_text = font.render("Score", True, BLACK)
    easy_text = font.render("Facile", True, BLACK)
    medium_text = font.render("Moyen", True, BLACK)
    hard_text = font.render("Difficile", True, BLACK)
    debug_text = font.render("Debug", True, BLACK)
    
    screen.blit(score_text, (score_button.centerx - score_text.get_width() // 2, score_button.centery - score_text.get_height() // 2))
    screen.blit(easy_text, (easy_button.centerx - easy_text.get_width() // 2, easy_button.centery - easy_text.get_height() // 2))
    screen.blit(medium_text, (medium_button.centerx - medium_text.get_width() // 2, medium_button.centery - medium_text.get_height() // 2))
    screen.blit(hard_text, (hard_button.centerx - hard_text.get_width() // 2, hard_button.centery - hard_text.get_height() // 2))
    screen.blit(debug_text, (debug_button.centerx - debug_text.get_width() // 2, debug_button.centery - debug_text.get_height() // 2))

    return easy_button, medium_button, hard_button, debug_button, score_button

def load_preset_tableau():
    """Charge un tableau prédéfini pour la partie."""
    return [
        ["x", "x", "x", "B", "x", "x", "x", "x", "x"],
        ["x", "B", "x", "x", "x", "x", "x", "x", "x"],
        ["x", "x", "x", "x", "x", "x", "x", "x", "x"],
        ["B", "x", "x", "x", "B", "x", "x", "x", "x"],
        ["x", "x", "B", "x", "x", "x", "x", "x", "x"],
        ["x", "x", "B", "x", "x", "x", "x", "x", "x"],
        ["x", "x", "B", "x", "x", "x", "x", "x", "x"],
        ["x", "x", "B", "x", "x", "x", "x", "x", "x"],
        ["x", "x", "B", "x", "x", "x", "x", "x", "x"]
    ]

def handle_difficulty_buttons(screen, font,  ):
    global game, screen_width, screen_height, left_margin, top_margin
    easy_button, medium_button, hard_button, debug_button, score_button = draw_difficulty_buttons()
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
            preset_tableau = load_preset_tableau()
            game.reset(preset_tableau_resolve=preset_tableau)
            print("Debug button clicked. Tableau reset with preset tableau.")
            # Mise à jour des dimensions de l'écran et des marges après le reset
            screen_width = 1200  
            screen_height = game.h * game.CELL_SIZE + PANEL_HEIGHT + SCREEN_PADDING * 2
            screen = pygame.display.set_mode((screen_width, screen_height))
            left_margin = (screen_width - game.l * game.CELL_SIZE) // 2
            top_margin = (screen_height - game.h * game.CELL_SIZE - PANEL_HEIGHT) // 2
        
        elif score_button.collidepoint(mouse_x, mouse_y):
            display_leaderboard(screen, font, )

def draw_grid():
    """Dessine la grille de jeu à l'écran."""
    for i in range(game.h):
        for j in range(game.l):
            rect = pygame.Rect(
                left_margin + j * game.CELL_SIZE,
                top_margin + i * game.CELL_SIZE,
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

game = Tableau()
screen_width = 1200  
screen_height = game.h * game.CELL_SIZE + PANEL_HEIGHT + SCREEN_PADDING * 2
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ines et les 40 bombes")

bomb_image = pygame.image.load("assets/bomb.png")
bomb_image = pygame.transform.scale(bomb_image, (game.CELL_SIZE - MARGIN, game.CELL_SIZE - MARGIN))
pygame.display.set_icon(bomb_image)

font = pygame.font.Font(None, 36)
alert_font = pygame.font.Font(None, 72)

left_margin = (screen_width - game.l * game.CELL_SIZE) // 2
top_margin = (screen_height - game.h * game.CELL_SIZE - PANEL_HEIGHT) // 2

background_image = pygame.image.load("assets/Background.png")
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

running = True
while running:
    screen.blit(background_image, (0, 0))

    if game.start_time and not game.game_over and not game.victory:
        elapsed_time = (pygame.time.get_ticks() - game.start_time) // 1000
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        game.final = f"{minutes:02}{seconds:02}"
        game.timer = f"{minutes:02}:{seconds:02}"

    if not game.game_over and not game.victory:
        save_one = True
        handle_difficulty_buttons(screen, font)
        draw_grid()  # Draw the grid inside the main loop

    pygame.draw.rect(
        screen, BLACK, (0, screen_height - PANEL_HEIGHT, screen_width, PANEL_HEIGHT)
    )
    
    timer_text = font.render(f"Temps : {game.timer}", True, WHITE)
    flags_text = font.render(f"Drapeaux restants : {game.flags_left}", True, WHITE)
    screen.blit(timer_text, (SCREEN_PADDING + 20, screen_height - PANEL_HEIGHT + 20))
    screen.blit(flags_text, (SCREEN_PADDING + 20, screen_height - PANEL_HEIGHT + 70))

    if game.game_over:
        game_over_text = alert_font.render("Game Over", True, RED)
        game_over_text_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 3.5))
        screen.blit(game_over_text, game_over_text_rect)

        replay_button_rect = game.draw_replay_button(screen, font, screen_width, screen_height)
        if pygame.mouse.get_pressed()[0] and replay_button_rect.collidepoint(mouse_x, mouse_y):
            game.reset()
            
    if game.victory:
        victory_text = alert_font.render("You Win!", True, GREEN)
        victory_text_rect = victory_text.get_rect(center=(screen_width // 2, screen_height // 3.5))
        screen.blit(victory_text, victory_text_rect)

        replay_button_rect = game.draw_replay_button(screen, font, screen_width, screen_height)
        if pygame.mouse.get_pressed()[0] and replay_button_rect.collidepoint(mouse_x, mouse_y):
            game.reset()
            
        save_button_rect = game.draw_save_button(screen, font, screen_width, screen_height)
        
        if pygame.mouse.get_pressed()[0] and save_button_rect.collidepoint(mouse_x, mouse_y) and save_one:
                save_one = False
                print(save_one)
                game_final = game.final
                get_pseudo_and_saves(screen, game.tableau_resolve, game_final)

    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if event.button == 1:
                if game.game_over or game.victory:
                    replay_button_rect = game.draw_replay_button(screen, font, screen_width, screen_height)
                    if replay_button_rect.collidepoint(mouse_x, mouse_y):
                        game.reset()
                else:
                    grid_x = (mouse_x - left_margin) // game.CELL_SIZE
                    grid_y = (mouse_y - top_margin) // game.CELL_SIZE
                    game.append(grid_y, grid_x)
                    if game.check_victory():
                        game.victory = True
            elif event.button == 3:
                grid_x = (mouse_x - left_margin) // game.CELL_SIZE
                grid_y = (mouse_y - top_margin) // game.CELL_SIZE
                if 0 <= grid_x < game.l and 0 <= grid_y < game.h:
                    if game.tableau[grid_y][grid_x] == "x" and game.flags_left > 0:
                        game.tableau[grid_y][grid_x] = "P"
                        game.flags_left -= 1
                    elif game.tableau[grid_y][grid_x] == "P":
                        game.tableau[grid_y][grid_x] = "x"
                        game.flags_left += 1

pygame.quit()
sys.exit()