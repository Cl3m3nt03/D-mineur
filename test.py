def savemap(tableau_resolve, game_final):
    result = ""
    
    for y in range(len(tableau_resolve)):  
        for x in range(len(tableau_resolve[y])): 
            if tableau_resolve[y][x] == "B": 
                result += "9"
            elif tableau_resolve[y][x] == "x": 
                result += "0"
        result += "1"

