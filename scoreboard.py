import pygame
import mysql.connector
import sys

PANEL_HEIGHT = 150
SCREEN_PADDING = 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)


#Function qui permet de decrypter le tableau de sauvegarde
def decrypt(selected_save_map):
    recupdata = selected_save_map 
    tableaucrypte = recupdata 
    
    # On calcule la hauteur (nombre de 'v')
    hauteur = tableaucrypte.count('v')

    # Calcul de la largeur (nombre de caractères avant 'v')
    largeur = 0
    i = 0
    while i < len(tableaucrypte):
        if tableaucrypte[i].isdigit():  
            nbr = ""
            while i < len(tableaucrypte) and tableaucrypte[i].isdigit():
                nbr += tableaucrypte[i] 
                i += 1
            nbr = int(nbr)  
            if i < len(tableaucrypte) and tableaucrypte[i].isalpha():  
                largeur += nbr 
        elif tableaucrypte[i] == 'v':
            break  
        else:
            i += 1  

   # Création du tableau
    tableau = [['x' for _ in range(largeur)] for _ in range(hauteur)]

    # Remplissage du tableau
    ix, iy = 0, 0  
    nbr = ""  
    for char in tableaucrypte:
        if char.isnumeric():
            nbr += char  
        elif char == 'v':  #Saut de ligne
            ix = 0
            iy += 1
        else:
            compt = int(nbr) if nbr else 1  
            for _ in range(compt):
                if ix < largeur:  
                    tableau[iy][ix] = char
                    ix += 1
            nbr = ""  
    return tableau

def play_replay(selected_save_map, game, screen, font):
    game.reset(preset_tableau_resolve=selected_save_map)
    # Reset de la partie en cours pour mettre à jour le tableau de jeu

def display_leaderboard(screen, font, game):
    # Connection à la bdd
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="mydatabase2"
    )
    mycursor = db.cursor()

    # Selection des 10 meilleurs scores pour l'affichage
    def get_top_scores_and_saves(limit=10):
        mycursor.execute("SELECT id, time, name, save_map FROM save ORDER BY time ASC LIMIT %s", (limit,))
        return mycursor.fetchall()
    scores = get_top_scores_and_saves()
    db.close()

    # Dimensions
    screen_width, screen_height = screen.get_size()

    # Image de fond
    background_image = pygame.image.load("assets/Background.png")
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
    screen.blit(background_image, (0, 0))

    # Titre
    title_font = pygame.font.Font(None, 50)
    title_text = title_font.render("Classement des Meilleurs Scores", True, BLACK)
    title_rect = title_text.get_rect(center=(screen_width // 2, 50))
    screen.blit(title_text, title_rect)

    # Affichage des scores avec les boutons "Rejouer"
    replay_buttons = []
    saves_map = []

    # Affichage des scores avec les nom et les temps
    for i, (id_, score, name, save_map) in enumerate(scores):
        score_text = font.render(f"{i + 1}. {name} - {score}s", True, WHITE)
        screen.blit(score_text, (screen_width // 4, 150 + i * 40))

        replay_button_rect = pygame.Rect(screen_width // 2 + 100, 150 + i * 40, 150, 30)
        pygame.draw.rect(screen, YELLOW, replay_button_rect)
        replay_text = font.render("REJOUER", True, BLACK)
        replay_text_rect = replay_text.get_rect(center=replay_button_rect.center)
        screen.blit(replay_text, replay_text_rect)

        replay_buttons.append(replay_button_rect)
        saves_map.append(save_map)

    # Button Retour
    button_font = pygame.font.Font(None, 40)
    return_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height - 100, 200, 50)
    pygame.draw.rect(screen, YELLOW, return_button_rect)
    return_text = button_font.render("RETOUR", True, BLACK)
    return_text_rect = return_text.get_rect(center=return_button_rect.center)
    screen.blit(return_text, return_text_rect)

    pygame.display.flip()

    # Gestion des interrections
    selected_save_map = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Si le bouton Retour est cliqué on quitte 
                if return_button_rect.collidepoint(event.pos):
                    running = False

                # Si bouton Rejouer est cliqué on rejoue la partie en decryptant le tableau de sauvegarde
                # et en le passant à la fonction play_replay
                for i, replay_button_rect in enumerate(replay_buttons):
                    if replay_button_rect.collidepoint(event.pos):
                        selected_save_map = saves_map[i]  
                        selected_save_map = decrypt(selected_save_map) 
                        #Print dans la console pour debug 
                        for row in selected_save_map:
                            print(' '.join(row))
                        play_replay(selected_save_map, game, screen, font)
                        running = False 
    return selected_save_map