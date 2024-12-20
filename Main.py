
import pygame
"""
Main.py
Ce script implémente un jeu de Démineur en utilisant Pygame. Le jeu inclut différents niveaux de difficulté,
un tableau des scores et la possibilité de sauvegarder et rejouer des parties.
Modules:
    - pygame: Bibliothèque pour créer des jeux vidéo.
    - random: Bibliothèque pour générer des nombres aléatoires.
    - sys: Bibliothèque pour les paramètres et fonctions spécifiques au système.
    - database: Module personnalisé pour les interactions avec la base de données.
    - saves: Module personnalisé pour gérer les sauvegardes de jeu.
    - scoreboard: Module personnalisé pour afficher le tableau des scores.
Classes:
    - Tableau: Représente le plateau de jeu du Démineur et contient les méthodes pour la logique du jeu.
Fonctions:
    - set_difficulty(value): Définit le niveau de difficulté du jeu.
    - get_difficulty(): Retourne le niveau de difficulté actuel en tant qu'entier.
    - resize_bomb_image(cell_size): Redimensionne l'image de la bombe pour s'adapter à la taille des cellules.
    - draw_difficulty_buttons(): Dessine les boutons de sélection de la difficulté à l'écran.
    - handle_difficulty_buttons(screen, font, game): Gère les clics sur les boutons de difficulté et réinitialise le jeu en conséquence.
    - play_replay(selected_save_map): Réinitialise le jeu avec un tableau sauvegardé pour rejouer.
    - draw_grid(): Dessine la grille de jeu à l'écran.
Configuration de Pygame:
    - Initialise Pygame et configure les dimensions de l'écran, les couleurs et les polices.
Boucle de Jeu:
    - Boucle principale qui exécute le jeu, gère les événements, met à jour l'écran et vérifie les conditions de fin de jeu ou de victoire.
"""
import random
import sys
from database import mycursor, mydb
from saves import get_pseudo_and_saves
from scoreboard import display_leaderboard

# Pygame configuration
pygame.init()

# Dimensions et couleurs
MARGIN = 0.5  # Marges réduites entre les cases
PANEL_HEIGHT = 150
SCREEN_PADDING = 100
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
COLOR_1 = (137, 243, 54)  # Vert clair
COLOR_2 = (105, 217, 45)  # Vert foncé

flag_image = pygame.image.load("assets/flag.png")
cell_image_1 = pygame.image.load("assets/pokeball.png")
cell_image_2 = pygame.image.load("assets/pokeballblack.png")

def resize_cell_images(cell_size):
    cell_image_1_resized = pygame.transform.scale(cell_image_1, (cell_size - MARGIN, cell_size - MARGIN))
    cell_image_2_resized = pygame.transform.scale(cell_image_2, (cell_size - MARGIN, cell_size - MARGIN))
    return cell_image_1_resized, cell_image_2_resized

def resize_flag_image(cell_size):
    return pygame.transform.scale(flag_image, (cell_size - MARGIN, cell_size - MARGIN))
# Variables pour la gestion de la difficulté
difficulte_value = "1"  # Valeur par défaut de la difficulté

def set_difficulty(value):
    global difficulte_value
    difficulte_value = value

def get_difficulty():
    return int(difficulte_value)

# Classe Tableau pour le jeu
class Tableau:
    def __init__(self):
        self.reset()
        
    # Si aucun tableau prédéfini n'est fourni, générer un nouveau tableau
    def reset(self, preset_tableau_resolve=None):
        # Récupérer la difficulté actuelle et définir les dimensions du tableau
        d = get_difficulty()
        #self h = hauteur, l = largeur, bomb = nombre de bombes
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
            self.CELL_SIZE = 28
        elif d == 0:
            self.h = 5
            self.l = 5
            self.bomb = 1
            self.CELL_SIZE = 40
        else:
            self.h = 0
            self.l = 0
            print("Mauvais choix ")
            exit()
        
        # Redimensionner les images de cellules et de drapeau
        self.cell_image_1_resized, self.cell_image_2_resized = resize_cell_images(self.CELL_SIZE)
        self.flag_image_resized = resize_flag_image(self.CELL_SIZE)
        
        self.preset_used = preset_tableau_resolve is not None

        # Si un tableau prédéfini est fourni, on l'utilise
        if self.preset_used:
            self.tableau_resolve = preset_tableau_resolve
            self.bomb = sum(row.count("B") for row in preset_tableau_resolve)
            self.h = len(preset_tableau_resolve)  #mise a jour de la hauteur
            self.l = len(preset_tableau_resolve[0])  # mise a jour de la largeur
        else:
            #initialisation du tableau de résolution
            self.tableau_resolve = [["x" for _ in range(self.l)] for _ in range(self.h)]
        #initialisation du tableau
        self.tableau = [["x" for _ in range(self.l)] for _ in range(self.h)]
        
        #initialisation des variables
        self.flags_left = self.bomb
        self.start_time = None
        self.timer = "00:00"
        self.final = "0000"
        self.game_over = False
        self.victory = False
        self.bombs_revealed = False
        self.first_click = False
        self.first_click_pos = None

    #fonction pour placer les bombes
    def reset_bomb_placement(self, first_click_x, first_click_y):
        if self.preset_used:
            return  # Ne pas placer de bomb si talbeau prédéfini

        # Placer les bombes en évitant la zone autour du premier clique
        placed_bombs = 0
        while placed_bombs < self.bomb:
            # Position aléatoire pour la bombe
            xbomb_pos = random.randint(0, self.h - 1)
            ybomb_pos = random.randint(0, self.l - 1)
            # Vérifier si la position est déjà une bombe ou à proximité du premier clic (3x3)
            if (self.tableau_resolve[xbomb_pos][ybomb_pos] != "B" and
                not (first_click_x - 1 <= xbomb_pos <= first_click_x + 1 and
                     first_click_y - 1 <= ybomb_pos <= first_click_y + 1)):
                self.tableau_resolve[xbomb_pos][ybomb_pos] = "B"
                placed_bombs += 1
    #fonction pour compter les bombes adjacentes
    def count_adjacent_bombs(self, pos1, pos2):
        count = 0
        for i in range(pos1 - 1, pos1 + 2):
            for j in range(pos2 - 1, pos2 + 2):
                if 0 <= i < self.h and 0 <= j < self.l and (i != pos1 or j != pos2):
                    if self.tableau_resolve[i][j] == "B":
                        count += 1
        return count
    #fonction pour révéler les cases adjacentes 
    def reveal(self, pos1, pos2):
        if self.tableau[pos1][pos2] != "x" or self.game_over:
            return
        adjacent_bombs = self.count_adjacent_bombs(pos1, pos2)
        # Si la case est vide, révéler les cases adjacentes
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
        # Si c'est le premier clic, placer les bombes et démarrer le chronomètre
        if not self.first_click:
            # Si la case cliquée est une bombe, déplacer la bombe et réessayer
            self.first_click_pos = (pos1, pos2)
            self.first_click = True
            #Placement des bombes
            self.reset_bomb_placement(pos1, pos2)
            self.start_time = pygame.time.get_ticks()
        # Si la case cliquée est une bombe, révéler toutes les bombes et terminer le jeu
        if self.tableau_resolve[pos1][pos2] == "B":
            self.game_over = True
            self.reveal_bombs()
            return False
        # Sinon, révéler la case 
        self.reveal(pos1, pos2)
        return True
    #fonction pour vérifier la victoire
    def check_victory(self):
        for i in range(self.h):
            for j in range(self.l):
                # Si une case non révélée n'est pas une bombe, le jeu continue
                if self.tableau[i][j] == "x" and self.tableau_resolve[i][j] != "B":
                    return False
        self.victory = True
        return True
    #fonction pour dessiner le bouton rejouer
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
    #fonction pour dessiner le bouton sauvegarder
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
    #fonction pour révéler les bomb quand le jeu est terminé
    def reveal_bombs(self):
        """Révèle toutes les bombes dans le tableau."""
        for i in range(self.h):
            for j in range(self.l):
                if self.tableau_resolve[i][j] == "B":
                    self.tableau[i][j] = "B"

# Charger l'image de la bombe
bomb_image = pygame.image.load("assets/bomb.png")

# Redimensionner l'image de la bombe pour s'adapter à la taille des cellules
def resize_bomb_image(cell_size):
    return pygame.transform.scale(bomb_image, (cell_size - MARGIN, cell_size - MARGIN))
#fonction pour dessiner les boutons de difficulté
def draw_difficulty_buttons():
    score_button = pygame.Rect(50, 120, 135, 50)
    easy_button = pygame.Rect(50, 190, 135, 50)
    medium_button = pygame.Rect(50, 260, 130, 50)
    hard_button = pygame.Rect(50, 330, 135, 50)
    debug_button = pygame.Rect(50, 400, 135, 50)
    
    pygame.draw.rect(screen, YELLOW, score_button)
    pygame.draw.rect(screen, YELLOW, easy_button)
    pygame.draw.rect(screen, YELLOW, medium_button)
    pygame.draw.rect(screen, YELLOW, hard_button)
    pygame.draw.rect(screen, YELLOW, debug_button)
    
    score_text = font.render("SCORE", True, BLACK)
    easy_text = font.render("FACILE", True, BLACK)
    medium_text = font.render("MOYEN", True, BLACK)
    hard_text = font.render("DIFFICILE", True, BLACK)
    debug_text = font.render("DEBUG", True, BLACK)
    
    screen.blit(score_text, (score_button.centerx - score_text.get_width() // 2, score_button.centery - score_text.get_height() // 2))
    screen.blit(easy_text, (easy_button.centerx - easy_text.get_width() // 2, easy_button.centery - easy_text.get_height() // 2))
    screen.blit(medium_text, (medium_button.centerx - medium_text.get_width() // 2, medium_button.centery - medium_text.get_height() // 2))
    screen.blit(hard_text, (hard_button.centerx - hard_text.get_width() // 2, hard_button.centery - hard_text.get_height() // 2))
    screen.blit(debug_text, (debug_button.centerx - debug_text.get_width() // 2, debug_button.centery - debug_text.get_height() // 2))

    return easy_button, medium_button, hard_button, debug_button, score_button

#fonction pour gérer les clics sur les boutons de difficulté
def handle_difficulty_buttons(screen, font, game):
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
            set_difficulty("0")
            game.reset()
    
        elif score_button.collidepoint(mouse_x, mouse_y):
            display_leaderboard(screen, font, game)
            pygame.time.wait(100)
            
#fonction pour gérer les clics sur le bouton rejouer
def play_replay(selected_save_map):
    game.reset(preset_tableau_resolve=selected_save_map)
    # Mise à jour des dimensions de l'écran et des marges après le reset
    global screen_width, screen_height, left_margin, top_margin
    screen_width = 1200  
    screen_height = game.h * game.CELL_SIZE + PANEL_HEIGHT + SCREEN_PADDING * 2
    screen = pygame.display.set_mode((screen_width, screen_height))
    left_margin = (screen_width - game.l * game.CELL_SIZE) // 2
    top_margin = (screen_height - game.h * game.CELL_SIZE - PANEL_HEIGHT) // 2
    
#fonction pour dessiner la grille
def draw_grid():
    for i in range(game.h):
        for j in range(game.l):
            #Position de la grid
            rect = pygame.Rect(
                left_margin + j * game.CELL_SIZE,
                top_margin + i * game.CELL_SIZE,
                game.CELL_SIZE - MARGIN,
                game.CELL_SIZE - MARGIN,
            )
            # image de la case en damier
            cell_image = game.cell_image_1_resized if (i + j) % 2 == 0 else game.cell_image_2_resized
            # Dessiner les cases en fonction de leur contenu
            if game.tableau[i][j] == "x":
                screen.blit(cell_image, rect.topleft)
            elif game.tableau[i][j] == "0":
                pygame.draw.rect(screen, YELLOW, rect)
                # Afficher le nombre de bombes adjacentes
            elif game.tableau[i][j].isdigit():
                pygame.draw.rect(screen, YELLOW, rect)
                text = font.render(game.tableau[i][j], True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            elif game.tableau[i][j] == "P":
                screen.blit(game.flag_image_resized, rect.topleft)
            elif game.tableau[i][j] == "B":
                bomb_resized = resize_bomb_image(game.CELL_SIZE)
                screen.blit(bomb_resized, rect.topleft)
# Initialiser le jeu
game = Tableau()
screen_width = 1200  
screen_height = game.h * game.CELL_SIZE + PANEL_HEIGHT + SCREEN_PADDING * 2
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("PikaBombe")


pygame.display.set_icon(bomb_image)

font = pygame.font.Font(None, 36)
alert_font = pygame.font.Font(None, 72)
# Initialiser les dimensions de l'écran et les marges
left_margin = (screen_width - game.l * game.CELL_SIZE) // 2
top_margin = (screen_height - game.h * game.CELL_SIZE - PANEL_HEIGHT) // 2

# Charger l'image de fond
background_image = pygame.image.load("assets/Background.png")
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))


running = True
while running:
    screen.blit(background_image, (0, 0))
    
    # Si le jeu n'est pas terminé, afficher le temps écoulé et les drapeaux restants
    if game.start_time and not game.game_over and not game.victory:
        elapsed_time = (pygame.time.get_ticks() - game.start_time) // 1000
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        game.final = f"{minutes:02}{seconds:02}"
        game.timer = f"{minutes:02}:{seconds:02}"
        save_one = True
    # Afficher les boutons de difficulté et gérer les clics
    handle_difficulty_buttons(screen, font, game)
    #afficher la grille
    draw_grid()  


    # Afficher le texte du chronomètre et des drapeaux restants et definir leur position
    timer_text = font.render(f"Temps : {game.timer}", True, BLACK)
    flags_text = font.render(f"Drapeaux restants : {game.flags_left}", True, BLACK)
    screen.blit(timer_text, (SCREEN_PADDING + 400, screen_height - PANEL_HEIGHT + 10))
    screen.blit(flags_text, (SCREEN_PADDING + 400, screen_height - PANEL_HEIGHT + 60))

    # Si le jeu est terminé, afficher le texte "Game Over" 
    if game.game_over:
        draw_grid()  # Redessinez la grille pour montrer les bombes révélées
        game_over_text = alert_font.render("Game Over", True, RED)
        game_over_text_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 3.5))
        screen.blit(game_over_text, game_over_text_rect)
        # Afficher le bouton "Rejouer" et si cliqué, réinitialiser le jeu
        replay_button_rect = game.draw_replay_button(screen, font, screen_width, screen_height)
        if pygame.mouse.get_pressed()[0] and replay_button_rect.collidepoint(mouse_x, mouse_y):
            game.reset()
    # Si le jeu est gagné, afficher le texte "You Win!"     
    if game.victory:
        victory_text = alert_font.render("You Win!", True, GREEN)
        victory_text_rect = victory_text.get_rect(center=(screen_width // 2, screen_height // 3.5))
        screen.blit(victory_text, victory_text_rect)
        # Afficher le bouton "Rejouer" et si cliqué, réinitialiser le jeu
        replay_button_rect = game.draw_replay_button(screen, font, screen_width, screen_height)
        if pygame.mouse.get_pressed()[0] and replay_button_rect.collidepoint(mouse_x, mouse_y):
            game.reset()
        # Afficher le bouton "Save" et si cliqué, obtenir le pseudo et sauvegarder les données  
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
            #gestion de clique gauche
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
            #gestion de clique droit       
            elif event.button == 3:
                grid_x = (mouse_x - left_margin) // game.CELL_SIZE
                grid_y = (mouse_y - top_margin) // game.CELL_SIZE
                if 0 <= grid_x < game.l and 0 <= grid_y < game.h:
                    #Si la case est x et qu'il reste des flag placer un flag et enlever 1 au compteur
                    if game.tableau[grid_y][grid_x] == "x" and game.flags_left > 0:
                        game.tableau[grid_y][grid_x] = "P"
                        game.flags_left -= 1
                    # Si il y a deja un drapeau mettre un x pour une case blanche et rajouter 1 au compteur
                    elif game.tableau[grid_y][grid_x] == "P":
                        game.tableau[grid_y][grid_x] = "x"
                        game.flags_left += 1

pygame.quit()
sys.exit()