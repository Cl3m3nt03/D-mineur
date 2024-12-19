import pygame
import mysql.connector
import sys

# Constants for screen dimensions and layout
PANEL_HEIGHT = 150
SCREEN_PADDING = 100

# Function to decrypt the saved map
def decrypt(selected_save_map):
    recupdata = selected_save_map  # Example input
    tableaucrypte = recupdata  # Direct use of the string
    
    # Calculate the height (number of 'v' = number of rows)
    hauteur = tableaucrypte.count('v')

    # Calculate the width (considering repetitions before each 'v')
    largeur = 0
    i = 0
    while i < len(tableaucrypte):
        if tableaucrypte[i].isdigit():  # If a digit is found
            nbr = ""
            while i < len(tableaucrypte) and tableaucrypte[i].isdigit():
                nbr += tableaucrypte[i]  # Get all digits
                i += 1
            nbr = int(nbr)  # Convert to integer
            if i < len(tableaucrypte) and tableaucrypte[i].isalpha():  # If the next character is a letter
                largeur += nbr  # Add the number of repetitions of this character
        elif tableaucrypte[i] == 'v':
            break  # Move to the next character
        else:
            i += 1  # Move to the next letter

    # Initialize the table with the calculated width and height
    tableau = [['x' for _ in range(largeur)] for _ in range(hauteur)]

    # Fill the table
    ix, iy = 0, 0  # Indices to fill the table
    nbr = ""  # Store encountered numbers

    for char in tableaucrypte:
        if char.isnumeric():
            nbr += char  # Build the number
        elif char == 'v':  # End of line
            ix = 0
            iy += 1
        else:
            compt = int(nbr) if nbr else 1  # Calculate the number of occurrences of the character

            # Fill the table cells
            for _ in range(compt):
                if ix < largeur:  # If still within line limits (maximum width)
                    tableau[iy][ix] = char
                    ix += 1

            nbr = ""  # Reset the number

    return tableau

def play_replay(selected_save_map, game, screen, font):
    game.reset(preset_tableau_resolve=selected_save_map)
    print("Replay button clicked. Tableau reset with saved tableau.")
    # No need to update screen dimensions and margins after reset

def display_leaderboard(screen, font, game):
    # Connect to the database
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="mydatabase2"
    )
    mycursor = db.cursor()

    # Fetch top scores and associated saves, sorted by ascending time
    def get_top_scores_and_saves(limit=10):
        mycursor.execute("SELECT id, time, name, save_map FROM save ORDER BY time ASC LIMIT %s", (limit,))
        return mycursor.fetchall()

    scores = get_top_scores_and_saves()
    db.close()

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)

    # Dimensions
    screen_width, screen_height = screen.get_size()

    # Load background image
    background_image = pygame.image.load("assets/Background.png")
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
    screen.blit(background_image, (0, 0))

    # Title
    title_font = pygame.font.Font(None, 50)
    title_text = title_font.render("Classement des Meilleurs Scores", True, BLACK)
    title_rect = title_text.get_rect(center=(screen_width // 2, 50))
    screen.blit(title_text, title_rect)

    # Variables to handle "Rejouer" buttons
    replay_buttons = []
    saves_map = []

    # Display scores with "Rejouer" buttons
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

    # Return button
    button_font = pygame.font.Font(None, 40)
    return_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height - 100, 200, 50)
    pygame.draw.rect(screen, YELLOW, return_button_rect)
    return_text = button_font.render("RETOUR", True, BLACK)
    return_text_rect = return_text.get_rect(center=return_button_rect.center)
    screen.blit(return_text, return_text_rect)

    pygame.display.flip()

    # Event handling
    selected_save_map = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the return button is clicked
                if return_button_rect.collidepoint(event.pos):
                    running = False

                # Check if a "Rejouer" button is clicked
                for i, replay_button_rect in enumerate(replay_buttons):
                    if replay_button_rect.collidepoint(event.pos):
                        selected_save_map = saves_map[i]  
                        selected_save_map = decrypt(selected_save_map) 
                        for row in selected_save_map:
                            print(' '.join(row))
                        play_replay(selected_save_map, game, screen, font)
                        running = False 
    return selected_save_map