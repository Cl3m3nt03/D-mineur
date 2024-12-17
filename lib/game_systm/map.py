from lib.game_systm import config
import numpy as np
import random

level = config.configuration()

def generatemap():
    if level is not None and isinstance(level, int) and level > 0:
        tableau = np.full((level, level), 'x', dtype=str)

        num_bombes = level
        bombes = set()
        while len(bombes) < num_bombes:
            x = random.randint(0, level - 1)
            y = random.randint(0, level - 1)
            if (x, y) not in bombes:
                bombes.add((x, y))
                tableau[y, x] = 'B'

        print("Carte initiale avec les bombes :")
        print(tableau)
        return tableau, bombes
    else:
        print("Erreur : le niveau n'a pas été correctement défini.")
        return None, None

def indicator(y, x, bombes):

    directions = [
        (-1, -1), (-1, 0), (-1, 1),(0, -1),(0, 1),(1, -1), (1, 0), (1, 1)      
    ]

    bomb_count = 0
    for dy, dx in directions:
        ny, nx = y + dy, x + dx
        if 0 <= ny < level and 0 <= nx < level and (nx, ny) in bombes:
            bomb_count += 1
    return bomb_count

def reveal_area(carte_joueur, bombes, y, x, visited):

    if (y, x) in visited or not (0 <= y < level and 0 <= x < level):
        return
    visited.add((y, x))

    bomb_count = indicator(y, x, bombes)
    carte_joueur[y, x] = str(bomb_count)

 
    if bomb_count == 0:
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dy, dx in directions:
            reveal_area(carte_joueur, bombes, y + dy, x + dx, visited)

def maplayer(carte_joueur):
    
    print("Carte du joueur :")
    print(carte_joueur)

def deplacementplayer(carte_joueur, bombes):

    print("Déplacez-vous avec les coordonnées (y, x) !")

    try:
        x = int(input(f"Entrez vos coordonnées en X (0-{level-1}): "))
        y = int(input(f"Entrez vos coordonnées en Y (0-{level-1}): "))

        if 0 <= x < level and 0 <= y < level:
            if (x, y) in bombes:
                print("Vous avez touché une bombe ! Vous avez perdu !")
                return False
            else:
                visited = set()
                reveal_area(carte_joueur, bombes, y, x, visited)
        else:
            print("Coordonnées invalides, essayez encore.")
    except ValueError:
        print("Veuillez entrer des chiffres valides.")
    return True

def main():
    tableau, bombes = generatemap()
    if tableau is None or bombes is None:
        print("Erreur : le jeu ne peut pas démarrer.")
        return

    carte_joueur = np.full((level, level), 'x', dtype=str)

    while True:
        maplayer(carte_joueur)
        if not deplacementplayer(carte_joueur, bombes):
            break 

if __name__ == "__main__":
    main()