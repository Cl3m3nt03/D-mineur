#importation de module pygame
import pygame
import pygame_menu
import random
import sys

# Initialisation de pygame pour que tous les ajouts fonctionnent
pygame.init()

# Création de la fenêtre du jeu
surface = pygame.display.set_mode((600, 400))

# Définition des niveaux des tailles et du nombre de mines
difficulté_niv ={
'Easy': {'grid_size': 8, 'mine_count': 10},
'M': {'grid_size': 10, 'mine_count': 20},
'H': {'grid_size': 18, 'mine_count': 40},
}

# Difficulté sélectionnée par défaut
selection_difficulté = 'Easy'

# Fonction appelée quand on choisit un niveau
def difficulté(value, difficulty):
    # Utilisation de la variable globale
    global selection_difficulté
    # Mise à jour de la difficulté choisie
    selection_difficulté = difficulty[0]

# Démarrer le jeu en fonction de la difficulté choisie par le joueur
def lanceur():
    # Utilisation de la variable globale
    global selection_difficulté
    # Récupération des paramètres de la grille et des mines selon le niveau
    grid_size = difficulté_niv[selection_difficulté]['grid_size']
    mine_count = difficulté_niv[selection_difficulté]['mine_count']
    # Taille de chaque case
    CELL_SIZE = 40
    # Longueur et largeur de la fenêtre du jeu
    WIDTH, HEIGHT = grid_size * CELL_SIZE, grid_size * CELL_SIZE
    # Création de la fenêtre du jeu avec les nouvelles tailles
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # Nom de la fenêtre de jeu
    pygame.display.set_caption(f"Démineur - {selection_difficulté}")

    # Couleurs utilisées dans la partie
    WHITE = (255, 255, 255)
    GRAY = (200, 200, 200)
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)

    # Police d'écriture
    font = pygame.font.SysFont("Arial", 24)

    # Fonction génération de cases et de mines
    def generation():
        # Grille vide
        grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
        # Stockage des positions des mines
        mines = set()
        # Placement aléatoire des mines
        while len(mines) < mine_count:
            row, col = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
            # Si la case n'a pas déjà une mine
            if grid[row][col] != 'M':
                # Placer une mine
                grid[row][col] = 'M'
                mines.add((row, col))
        # Calcul des nombres de mines pour chaque case
        for row in range(grid_size):
            for col in range(grid_size):
                # Passer les cases avec des mines
                if grid[row][col] == 'M': continue
                adjacent_mines = sum(1 for r in range(-1, 2) for c in range(-1, 2)
                                     if 0 <= row + r < grid_size and 0 <= col + c < grid_size and grid[row + r][col + c] == 'M')
                # Remplacer les cases vides par le nombre de mines autour
                grid[row][col] = str(adjacent_mines) if adjacent_mines > 0 else ' '
        # Retourner la grille et les positions des mines
        return grid, mines

    # Fonction pour dessiner la grille
    def grille_generation(grid, revealed, flagged, game_over=False, mines=set()):
        for row in range(grid_size):
            for col in range(grid_size):
                # Calcul de la position de la case
                x, y = col * CELL_SIZE, row * CELL_SIZE
                # Si la case est révélée
                if revealed[row][col]:
                    # Si la case est une mine
                    if grid[row][col] == 'M':
                        # Alors la case devient rouge
                        pygame.draw.rect(screen, RED, (x, y, CELL_SIZE, CELL_SIZE))
                        # Et dessine un rond noir dessus (effet de mine)
                        pygame.draw.circle(screen, BLACK, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 8)
                    else:
                        # La case est blanche
                        pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE))
                        # La case aura un contour gris
                        pygame.draw.rect(screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE), 2)
                    if grid[row][col] != ' ':
                        # Texte avec le nombre de mines autour
                        text = font.render(grid[row][col], True, BLACK)
                        # Affichage du texte sur la case
                        screen.blit(text, (x + CELL_SIZE // 3, y + CELL_SIZE // 3))
                else:
                    # La case cachée sera grise
                    pygame.draw.rect(screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE))
                    # Les cases auront un contour noir
                    pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 2)
                # Si la partie est terminée, alors toutes les mines seront affichées
                if game_over and (row, col) in mines:
                    pygame.draw.rect(screen, RED, (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.circle(screen, BLACK, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 8)

    # Fonction pour révéler une case
    def reveler_une_case(grid, revealed, flagged, row, col):
        # Si la case est déjà révélée ou marquée, ne rien faire
        if revealed[row][col] or flagged[row][col]: return
        # Marquer la case comme révélée
        revealed[row][col] = True
        if grid[row][col] == ' ':
            for r in range(-1, 2):
                for c in range(-1, 2):
                    # Parcourir les cases autour
                    nr, nc = row + r, col + c
                    if 0 <= nr < grid_size and 0 <= nc < grid_size:
                        # reveler les case autour
                        reveler_une_case(grid, revealed, flagged, nr, nc)

    # Fonction pour placer un drapeau
    def drapeau(flagged, row, col):
        # Pouvoir enlever ou mettre un drapeau
        flagged[row][col] = not flagged[row][col]

    # Fonction principale
    def main():
        # Générer la grille de jeu et les mines
        grid, mines = generation()
        # Liste pour suivre les cases révélées
        revealed = [[False for _ in range(grid_size)] for _ in range(grid_size)]
        # Liste pour suivre les cases marquées
        flagged = [[False for _ in range(grid_size)] for _ in range(grid_size)]
        # Variable pour suivre l'état du jeu
        game_over = False
        # Variable pour vérifier la victoire du joueur
        won = False

        # Boucle principale
        while True:
            # Écran blanc
            screen.fill(WHITE)
            for event in pygame.event.get():
                # Si le joueur ferme la fenêtre
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Si la partie est terminée, ignorer les autres événements
                if game_over: continue
                # Si on appuie sur un bouton de souris
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Vérifier la case sous le curseur
                    col, row = event.pos[0] // CELL_SIZE, event.pos[1] // CELL_SIZE
                    # Si clic gauche appuyé
                    if event.button == 1:
                        # Si une mine a explosé
                        if grid[row][col] == 'M':
                            # Fin de la partie
                            game_over = True
                        else:
                            # Révéler la case
                            reveler_une_case(grid, revealed, flagged, row, col)
                    # Si clic droit appuyé
                    elif event.button == 3:
                        # Mettre ou enlever un drapeau
                        drapeau(flagged, row, col)
            # Vérifier si toutes les cases sauf celles avec des mines sont révélées
            if all(revealed[row][col] or grid[row][col] == 'M' for row in range(grid_size) for col in range(grid_size)):
                # Si oui, alors le joueur a gagné
                won = True

            # Générer la grille sur l'écran
            grille_generation(grid, revealed, flagged, game_over, mines)

            # Afficher le message de fin de jeu
            if game_over:
                # Afficher "PERDU, T'EST UN NOEILLE" si la partie est perdue
                game_over_text = font.render("PERDU, T'EST UN NOEILLE", True, RED)
                screen.blit(game_over_text, (WIDTH // 4, HEIGHT // 2))
            elif won:
                # Afficher "GG BRO" si le joueur gagne
                win_text = font.render("GG BRO", True, (0, 255, 0))
                screen.blit(win_text, (WIDTH // 4, HEIGHT // 2))

            # Mettre à jour l'affichage
            pygame.display.update()

    main()

# Menu du jeu
menu = pygame_menu.Menu('Welcome', 600, 400, theme=pygame_menu.themes.THEME_BLUE)
menu.add.text_input('Name :', default='Your Name')
menu.add.selector('Difficulty :', [('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')], onchange=difficulté)
menu.add.button('Play', lanceur)
menu.add.button('Quit', pygame_menu.events.EXIT)
menu.mainloop(surface)
