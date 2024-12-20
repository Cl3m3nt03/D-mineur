import pygame
import sys
import mysql.connector

pygame.init()

# Dimensions et couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
color_inactive = (255, 255, 255)
color_active = (0, 255, 0) 


pseudo = ""  

# Configuration de la zone de saisie du pseudo
input_box = pygame.Rect(400, 100, 400, 50) 
active = False  #


font = pygame.font.Font(None, 36)

# Fonction pour dessiner la zone de texte 
def draw_input_boxs(screen):
    color = color_active if active else color_inactive
    pygame.draw.rect(screen, color, input_box, 2)

    # Afficher le texte 
    txt_surface = font.render(pseudo, True, color)
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

# Fonction pour gérer l'entrée du texte
def handle_text_inputs(event):
    global pseudo
    if event.key == pygame.K_BACKSPACE:
        pseudo = pseudo[:-1]  # Supprimer le dernier caractère
    else:
        pseudo += event.unicode  # Ajouter le caractère tapé à la chaîne

#  dessiner le bouton save et definir sa position et taille
def draw_save_buttons(screen):
    save_width = 180
    save_height = 50
    save_rect = pygame.Rect(
        screen.get_width() // 2 - save_width // 2,
        screen.get_height() // 2 + 90,
        save_width,
        save_height,
    )
    pygame.draw.rect(screen, YELLOW, save_rect)
    save_text = font.render("Save", True, BLACK)
    save_text_rect = save_text.get_rect(center=save_rect.center)
    screen.blit(save_text, save_text_rect)

    return save_rect

# Fonction pour dessiner l'arrière-plan et le titre
def draw_background_and_title(screen):
    # Charger l'image de fond
    screen_width, screen_height = screen.get_size()
    background_image = pygame.image.load("assets/Background.png")
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
    screen.blit(background_image, (0, 0))

    # Titre
    title_font = pygame.font.Font(None, 50)
    title_text = title_font.render("Saisie du Pseudo", True, YELLOW)
    title_rect = title_text.get_rect(center=(screen_width // 2, 50))
    screen.blit(title_text, title_rect)

# Fonction pour obtenir le pseudo et enregistrer les données
def get_pseudo_and_saves(screen, tableau_resolve, game_final):
    global active, pseudo
    running_input = True
    while running_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_input = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active 
                else:
                    active = False
                # Vérifier si le bouton Save est cliqué
                save_button_rect = draw_save_buttons(screen)
                if save_button_rect.collidepoint(event.pos):
                    print({pseudo}) 
                    savemap(tableau_resolve, game_final)  # Passer tableau_resolve et game_final
                    running_input = False
            if event.type == pygame.KEYDOWN:
                if active:
                    handle_text_inputs(event)

        # Dessiner l'arrière-plan, le titre et la zone de texte
        draw_background_and_title(screen)
        draw_input_boxs(screen)
        draw_save_buttons(screen)

        pygame.display.flip()

# Sauvegarder la carte dans la base de données
def savemap(tableau_resolve, game_final):
    result = ""
    for y in range(len(tableau_resolve)):  
        compt = 0  
        for x in range(len(tableau_resolve[y])): 
            if tableau_resolve[y][x] == 'x':  
                compt += 1
            elif tableau_resolve[y][x] == 'B': 
                if compt > 0:  
                    result += f"{compt}x" if compt > 1 else "x"
                    compt = 0  
                result += "B"  
        #Saut de ligne
        if compt > 0:
            result += f"{compt}x" if compt > 1 else "x"

        result += "v"  


    # Connexion à la bdd
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="mydatabase2"
    )
    mycursor = mydb.cursor()

    # Insertion de la carte le pseudo et le temps dans la table save
    string1 = f"INSERT INTO save (save_map, time,name) VALUES ('{result}', {game_final},'{pseudo}')"
    mycursor.execute(string1)

    mydb.commit() 
    mydb.close()

    return result

# Lancer la page de saisie du pseudo
if __name__ == "__main__":
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Page Pseudo")



    pygame.quit()
    sys.exit()
