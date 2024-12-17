from turtle import Screen
import pygame
import pygame_menu




pygame.init()
surface = pygame.display.set_mode((600, 400))

def set_difficulty(value, difficulty):



    pass

def start_the_game():
    import pygame
    import random
    import sys




    pygame.init()

    CELL_SIZE = 40
    GRID_SIZE = 10
    MINE_COUNT = 15
    WIDTH, HEIGHT = GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Démineur")

    WHITE = (255, 255, 255)
    GRAY = (200, 200, 200)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)

    font = pygame.font.SysFont("Arial", 24)

    def generate_grid():
        grid = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        mines = set()

        while len(mines) < MINE_COUNT:
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - 1)
            if grid[row][col] != 'M':
                grid[row][col] = 'M'
                mines.add((row, col))

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if grid[row][col] == 'M':
                    continue
                adjacent_mines = 0
                for r in range(-1, 2):
                    for c in range(-1, 2):
                        nr, nc = row + r, col + c
                        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and grid[nr][nc] == 'M':
                            adjacent_mines += 1
                grid[row][col] = str(adjacent_mines) if adjacent_mines > 0 else ' '

        return grid, mines

    def draw_grid(grid, revealed, flagged):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x, y = col * CELL_SIZE, row * CELL_SIZE

                if revealed[row][col]:
                    if grid[row][col] == 'M':
                        pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE))
                        pygame.draw.circle(screen, RED, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 8)
                    else:
                        pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE))
                        pygame.draw.rect(screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE), 2)
                    if grid[row][col] != ' ':
                        text = font.render(grid[row][col], True, BLACK)
                        screen.blit(text, (x + CELL_SIZE // 3, y + CELL_SIZE // 3))
                else:
                    pygame.draw.rect(screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 2)


                if flagged[row][col]:
                    pygame.draw.line(screen, RED, (x, y), (x + CELL_SIZE, y + CELL_SIZE), 3)
                    pygame.draw.line(screen, RED, (x + CELL_SIZE, y), (x, y + CELL_SIZE), 3)

    def reveal(grid, revealed, flagged, row, col):
        if revealed[row][col] or flagged[row][col]:
            return
        revealed[row][col] = True
        if grid[row][col] == ' ':
            for r in range(-1, 2):
                for c in range(-1, 2):
                    nr, nc = row + r, col + c
                    if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                        reveal(grid, revealed, flagged, nr, nc)

    def flag_cell(flagged, row, col):
        flagged[row][col] = not flagged[row][col]

    def main():
        grid, mines = generate_grid()
        revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        flagged = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        game_over = False
        won = False

        while True:
            screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    col, row = event.pos[0] // CELL_SIZE, event.pos[1] // CELL_SIZE

                    if event.button == 1:  # Clic gauche (révéler)
                        if grid[row][col] == 'M':
                            game_over = True
                        else:
                            reveal(grid, revealed, flagged, row, col)

                    elif event.button == 3:
                        flag_cell(flagged, row, col)

            if all(revealed[row][col] or grid[row][col] == 'M' for row in range(GRID_SIZE) for col in range(GRID_SIZE)):
                won = True

            draw_grid(grid, revealed, flagged)

            if game_over:
                game_over_text = font.render("t'as loose sale noeille", True, RED)
                screen.blit(game_over_text, (WIDTH // 4, HEIGHT // 2))
            elif won:
                win_text = font.render("GG MEC", True, GREEN)
                screen.blit(win_text, (WIDTH // 4, HEIGHT // 2))

            pygame.display.update()

    main()

    pass

menu = pygame_menu.Menu('Welcome', 600, 400,
    theme=pygame_menu.themes.THEME_BLUE)


menu.add.text_input('Name :', default='Your Name')
menu.add.selector('Difficulty :', [('Hard', 1), ('Easy', 2)], onchange=set_difficulty)
menu.add.button('Play', start_the_game)
menu.add.button('Quit', pygame_menu.events.EXIT)

menu.mainloop(surface)