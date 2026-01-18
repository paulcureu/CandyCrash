import pygame
import sys
import random

pygame.init()

pygame.font.init()
font_scor = pygame.font.SysFont("Arial", 28, bold=True)
total_score = 0

# --- CONFIGURARE ---
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 560
TILE_SIZE = 50 
ROWS, COLS = 8, 8

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Candy Crush")

# --- 1. ÎNCĂRCAREA IMAGINILOR ---
candy_images = []
for i in range(1, 9):
    try:
        img = pygame.image.load(f"{i}.png").convert_alpha()
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        candy_images.append(img)
    except:
        temp_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        temp_surf.fill((random.randint(0,255), random.randint(0,255), random.randint(0,255)))
        candy_images.append(temp_surf)

# --- 2. CREAREA MATRICEI ---
grid = [[random.randint(0, 7) for col in range(COLS)] for row in range(ROWS)]
# Această matrice va reține câți pixeli "mai are de căzut" fiecare bomboană
offsets = [[0 for _ in range(COLS)] for _ in range(ROWS)]
ANIMATION_SPEED = 5 # Viteza de cădere (pixeli pe cadru)
# --- 3. VARIABILE PENTRU LOGICĂ ---
selected_tile = None 

def find_matches_and_score(grid):
    to_remove = set()
    h_matches = [] # Stocăm liniile orizontale găsite
    v_matches = [] # Stocăm liniile verticale găsite
    turn_score = 0

    # 1. Căutare ORIZONTALĂ
    for r in range(ROWS):
        c = 0
        while c < COLS:
            color = grid[r][c]
            if color == -1: 
                c += 1
                continue
            match_len = 1
            while c + match_len < COLS and grid[r][c + match_len] == color:
                match_len += 1
            
            if match_len >= 3:
                match_coords = [(r, c + i) for i in range(match_len)]
                h_matches.append(match_coords)
                for coord in match_coords: to_remove.add(coord)
            c += match_len

    # 2. Căutare VERTICALĂ
    for c in range(COLS):
        r = 0
        while r < ROWS:
            color = grid[r][c]
            if color == -1:
                r += 1
                continue
            match_len = 1
            while r + match_len < ROWS and grid[r + match_len][c] == color:
                match_len += 1
            
            if match_len >= 3:
                match_coords = [(r + i, c) for i in range(match_len)]
                v_matches.append(match_coords)
                for coord in match_coords: to_remove.add(coord)
            r += match_len

    # 3. CALCULARE SCOR
    # Verificăm intersecțiile pentru T și L
    processed_h = [False] * len(h_matches)
    processed_v = [False] * len(v_matches)

    for i, h_line in enumerate(h_matches):
        for j, v_line in enumerate(v_matches):
            # Dacă au o celulă comună, avem un L sau T
            intersectie = set(h_line) & set(v_line)
            if intersectie:
                # Verificăm dacă e T (brațe de 3 care se intersectează)
                if len(h_line) == 3 and len(v_line) == 3:
                    # Dacă intersecția e la mijlocul uneia, e T, altfel e L
                    # Pentru simplitate, folosim punctajele cerute:
                    # Dacă e intersecție de linii de 3, dăm bonus de T sau L
                    center_h = h_line[1]
                    if center_h in intersectie: turn_score += 30 # T
                    else: turn_score += 20 # L
                    
                    processed_h[i] = True
                    processed_v[j] = True

    # Adăugăm punctele pentru liniile care nu au făcut parte dintr-un L sau T
    for i, h_line in enumerate(h_matches):
        if not processed_h[i]:
            if len(h_line) == 3: turn_score += 5
            elif len(h_line) == 4: turn_score += 10
            elif len(h_line) >= 5: turn_score += 50

    for j, v_line in enumerate(v_matches):
        if not processed_v[j]:
            if len(v_line) == 3: turn_score += 5
            elif len(v_line) == 4: turn_score += 10
            elif len(v_line) >= 5: turn_score += 50

    return list(to_remove), turn_score

def apply_gravity_and_refill(grid, offsets):
    for col in range(COLS):
        for row in range(ROWS - 1, -1, -1):
            if grid[row][col] == -1:
                for r_above in range(row - 1, -1, -1):
                    if grid[r_above][col] != -1:
                        grid[row][col] = grid[r_above][col]
                        grid[r_above][col] = -1
                        # Calculăm decalajul: (rândul destinație - rândul sursă) * mărime
                        offsets[row][col] = (row - r_above) * TILE_SIZE
                        break
                else:
                    # Dacă nu am găsit bomboană deasupra, generăm una nouă
                    grid[row][col] = random.randint(0, 7)
                    # Bomboanele noi vin de "deasupra" ecranului (un rând virtual)
                    offsets[row][col] = (row + 1) * TILE_SIZE
running = True
clock = pygame.time.Clock()
ANIMATION_SPEED = 5
while running:
    # --- 1. ACTUALIZARE ANIMAȚIE ---
    is_animating = False
    for r in range(ROWS):
        for c in range(COLS):
            if offsets[r][c] > 0:
                offsets[r][c] -= ANIMATION_SPEED
                if offsets[r][c] < 0: 
                    offsets[r][c] = 0
                is_animating = True # Dacă există un offset > 0, înseamnă că ceva încă se mișcă

    # --- 2. GESTIONARE EVENIMENTE ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Permitem click-ul DOAR dacă nu avem nicio animație în curs
        if event.type == pygame.MOUSEBUTTONDOWN and not is_animating:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            col = mouse_x // TILE_SIZE
            row = mouse_y // TILE_SIZE
            
            if row < ROWS and col < COLS:
                if selected_tile is None:
                    selected_tile = (row, col)
                else:
                    r1, c1 = selected_tile
                    r2, c2 = row, col
                    distanta = abs(r1 - r2) + abs(c1 - c2)
                    
                    if distanta == 1:
                        # Facem schimbul
                        grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                        
                        matches, score_obtinut = find_matches_and_score(grid)
                        if not matches:
                            # Dacă nu e meci, punem înapoi
                            grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                        else:
                            # Avem meciuri! Aplicăm cascada
                            while matches:
                                total_score += score_obtinut
                                for rm, cm in matches:
                                    grid[rm][cm] = -1
                                
                                # Trimitem și offsets către funcția de gravitate
                                apply_gravity_and_refill(grid, offsets) 
                                
                                matches, score_obtinut = find_matches_and_score(grid)
                        
                        selected_tile = None
                    else:
                        selected_tile = (row, col)

    # --- 3. DESENARE ---
    screen.fill((30, 30, 30)) 
    
    for row in range(ROWS):
        for col in range(COLS):
            candy_index = grid[row][col]
            if candy_index != -1:
                # IMPORTANT: Calculăm poziția Y scăzând offset-ul
                x_pos = col * TILE_SIZE
                y_pos = (row * TILE_SIZE) - offsets[row][col]
                screen.blit(candy_images[candy_index], (x_pos, y_pos))

    # Desenăm conturul selecției (doar dacă nu suntem în animație)
    if selected_tile and not is_animating:
        r, c = selected_tile
        pygame.draw.rect(screen, (255, 255, 255), (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE), 3)

    # Afișare Scor
    text_suprafata = font_scor.render(f"Scor: {total_score}", True, (255, 255, 255))
    screen.blit(text_suprafata, (20, 420)) 

    pygame.display.flip()
    clock.tick(60) # Menține 60 de cadre pe secundă

pygame.quit()
sys.quit()