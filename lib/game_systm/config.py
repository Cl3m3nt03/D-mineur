def configuration():

    flagspawn = 0
    bombspawn = 0

    while True: 
        try:
            level = int(input("Sélectionne ton Niveau (1, 2 ou 3) : "))

            if level == 1:
                print("Level 1")
                return 5
            elif level == 2:
                print("Level 2")
                return 10
            elif level == 3:
                print("Level 3")
                return 15
            else:
                print("Niveau invalide. Veuillez choisir 1, 2 ou 3.")
        except ValueError:
            print("Erreur : veuillez entrer un nombre entier (1, 2 ou 3).")