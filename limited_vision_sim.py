import pygame
import time
import random

# ===== SETTINGS =====
size = int(input("Enter grid size (e.g. 10): "))
rows = size
cols = size
cell_size = 50

vision_radius = 1

# ===== TRUE MAP (UNKNOWN TO AGENT) =====
grid = [[0 for _ in range(cols)] for _ in range(rows)]

# random obstacles
for _ in range(int(rows * cols * 0.2)):
    x = random.randint(0, cols-1)
    y = random.randint(0, rows-1)
    grid[y][x] = 1

# ===== KNOWN MAP =====
known_grid = [[-1 for _ in range(cols)] for _ in range(rows)]

# ===== AGENT + TARGET =====
current = (0, 0)
target = (cols-1, rows-1)

# ensure start/target not blocked
grid[0][0] = 0
grid[target[1]][target[0]] = 0

moves = [(1,0), (0,1), (0,-1), (-1,0)]

# ===== PYGAME SETUP =====
pygame.init()
width = cols * cell_size
height = rows * cell_size
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Limited Vision Navigation")

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
GRAY = (150,150,150)

# ===== HEURISTIC =====
def h(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# ===== UPDATE VISION =====
def update_vision():
    global known_grid
    for dy in range(-vision_radius, vision_radius+1):
        for dx in range(-vision_radius, vision_radius+1):
            nx = current[0] + dx
            ny = current[1] + dy

            if 0 <= nx < cols and 0 <= ny < rows:
                known_grid[ny][nx] = grid[ny][nx]

# ===== A* USING KNOWN MAP =====
def astar(start, target):
    open_set = [start]
    came_from = {}

    g = {start: 0}
    f = {start: h(start, target)}

    while open_set:
        current_node = min(open_set, key=lambda pos: f.get(pos, float("inf")))

        if current_node == target:
            path = []
            while current_node in came_from:
                path.append(current_node)
                current_node = came_from[current_node]
            return path[::-1]

        open_set.remove(current_node)

        for dx, dy in moves:
            nx = current_node[0] + dx
            ny = current_node[1] + dy
            neighbor = (nx, ny)

            if nx < 0 or nx >= cols or ny < 0 or ny >= rows:
                continue

            # treat unknown as walkable but risky
            if known_grid[ny][nx] == 1:
                continue

            cost = 1
            if known_grid[ny][nx] == -1:
                cost = 3  # penalty for unknown

            tentative_g = g[current_node] + cost

            if tentative_g < g.get(neighbor, float("inf")):
                came_from[neighbor] = current_node
                g[neighbor] = tentative_g
                f[neighbor] = tentative_g + h(neighbor, target)

                if neighbor not in open_set:
                    open_set.append(neighbor)

    return []

# ===== DRAW =====
def draw(path):
    screen.fill(WHITE)

    for y in range(rows):
        for x in range(cols):
            rect = pygame.Rect(x*cell_size, y*cell_size, cell_size, cell_size)

            if known_grid[y][x] == -1:
                pygame.draw.rect(screen, GRAY, rect)
            elif known_grid[y][x] == 1:
                pygame.draw.rect(screen, BLACK, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)

            pygame.draw.rect(screen, (200,200,200), rect, 1)

    for p in path:
        pygame.draw.rect(screen, GREEN,
            pygame.Rect(p[0]*cell_size, p[1]*cell_size, cell_size, cell_size))

    pygame.draw.rect(screen, RED,
        pygame.Rect(target[0]*cell_size, target[1]*cell_size, cell_size, cell_size))

    pygame.draw.rect(screen, BLUE,
        pygame.Rect(current[0]*cell_size, current[1]*cell_size, cell_size, cell_size))

    pygame.display.update()

# ===== MAIN LOOP =====
running = True
path = []

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    update_vision()

    if current == target:
        print("Reached target!")
        break

    path = astar(current, target)

    if path:
        current = path[0]  # move one step
    else:
        print("No path known. Exploring randomly.")
        random.shuffle(moves)
        for dx, dy in moves:
            nx = current[0] + dx
            ny = current[1] + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                if known_grid[ny][nx] != 1:
                    current = (nx, ny)
                    break

    draw(path)
    time.sleep(0.2)

pygame.quit()
