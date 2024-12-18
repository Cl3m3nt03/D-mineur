import pygame
import mysql.connector
import sys

def display_leaderboard(screen, font):

    # Connexion à la base de données
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="mydatabase2"
    )
    mycursor = db.cursor()

    # Récupérer les meilleurs scores et leurs sauvegardes associées, triés par temps croissant
    def get_top_scores_and_saves(limit=10):
        # Tri du temps par ordre croissant (le plus rapide en premier)
        mycursor.execute("SELECT id, time, name, save_map FROM save ORDER BY time ASC LIMIT %s", (limit,))
        return mycursor.fetchall()

    scores = get_top_scores_and_saves()
    db.close()

    # Couleurs
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)

    # Dimensions
    screen_width, screen_height = screen.get_size()

    # Charger l'image de fond
    background_image = pygame.image.load("assets/Background.png")
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
    screen.blit(background_image, (0, 0))

    # Titre
    title_font = pygame.font.Font(None, 50)
    title_text = title_font.render("Classement des Meilleurs Scores", True, YELLOW)
    title_rect = title_text.get_rect(center=(screen_width // 2, 50))
    screen.blit(title_text, title_rect)

    # Variables pour gérer les boutons "Rejouer"
    replay_buttons = []  # Liste des rects pour les boutons "Rejouer"
    saves_map = []  # Liste des sauvegardes associées

    # Affichage des scores avec boutons "Rejouer"
    for i, (id_, score, name, save_map) in enumerate(scores):
        # Afficher le nom et le score
        score_text = font.render(f"{i + 1}. {name} - {score}s", True, WHITE)
        screen.blit(score_text, (screen_width // 4, 150 + i * 40))

        # Ajouter un bouton "Rejouer"
        replay_button_rect = pygame.Rect(screen_width // 2 + 100, 150 + i * 40, 100, 30)
        pygame.draw.rect(screen, YELLOW, replay_button_rect)
        replay_text = font.render("Rejouer", True, BLACK)
        replay_text_rect = replay_text.get_rect(center=replay_button_rect.center)
        screen.blit(replay_text, replay_text_rect)

        replay_buttons.append(replay_button_rect)
        saves_map.append(save_map)

    # Bouton Retour
    button_font = pygame.font.Font(None, 40)
    return_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height - 100, 200, 50)
    pygame.draw.rect(screen, WHITE, return_button_rect)
    return_text = button_font.render("Retour", True, BLACK)
    return_text_rect = return_text.get_rect(center=return_button_rect.center)
    screen.blit(return_text, return_text_rect)

    pygame.display.flip()

    # Gestion des événements
    selected_save_map = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier si le bouton Retour est cliqué
                if return_button_rect.collidepoint(event.pos):
                    running = False  # Quitte l'écran de classement

                # Vérifier si un bouton "Rejouer" est cliqué
                for i, replay_button_rect in enumerate(replay_buttons):
                    if replay_button_rect.collidepoint(event.pos):
                        selected_save_map = saves_map[i]  # Récupère la sauvegarde associée
                        print(selected_save_map)
                        running = False  # Quitte l'écran après sélection

    return selected_save_map