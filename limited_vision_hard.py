import pygame
import time
import random

# ===== USER INPUT =====
size = int(input("Enter grid size (e.g. 15): "))
rows = size
cols = size
cell_size = 40

vision_radius = 1

# ===== TARGET =====
target = (cols-1, rows-1)

# ===== TRUE MAP =====
grid = [[0 for _ in range(cols)] for _ in range(rows)]

# ===== CREATE HARD GUARANTEED PATH =====
path_cells = set()
x, y = 0, 0
path_cells.add((x, y))

while (x, y) != target:
    moves_options = []

    # bias toward target
    if x < target[0]:
        moves_options.append((1, 0))
    if y < target[1]:
        moves_options.append((0, 1))

    # allow detours
    if x > 0:
        moves_options.append((-1, 0))
    if y > 0:
        moves_options.append((0, -1))

    dx, dy = random.choice(moves_options)

    nx = x + dx
    ny = y + dy

    if 0 <= nx < cols and 0 <= ny < rows:
        x, y = nx, ny
        path_cells.add((x, y))

# ===== ADD OBSTACLES (DENser) =====
for _ in range(int(rows * cols * 0.35)):
    ox = random.randint(0, cols-1)
    oy = random.randint(0, rows-1)

    if (ox, oy) not in path_cells:
        grid[oy][ox] = 1

# ===== ADD DEAD-END TRAPS =====
for _ in range(int(rows * cols * 0.1)):
    tx = random.randint(1, cols-2)
    ty = random.randint(1, rows-2)

    if (tx, ty) not in path_cells:
        grid[ty][tx] = 0
        grid[ty-1][tx] = 1
        grid[ty+1][tx] = 1
        grid[ty][tx-1] = 1

# ensure start/target clear
grid[0][0] = 0
grid[target[1]][target[0]] = 0

# ===== KNOWN MAP =====
known_grid = [[-1 for _ in range(cols)] for _ in range(rows)]

# ===== AGENT =====
current = (0, 0)
visited_path = []

moves = [(1,0), (0,1), (0,-1), (-1,0)]

# ===== PYGAME SETUP =====
pygame.init()
width = cols * cell_size
height = rows * cell_size
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Hard Navigation Simulation")

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
    for dy in range(-vision_radius, vision_radius+1):
        for dx in range(-vision_radius, vision_radius+1):
            nx = current[0] + dx
            ny = current[1] + dy

            if 0 <= nx < cols and 0 <= ny < rows:
                known_grid[ny][nx] = grid[ny][nx]

# ===== A* ON PARTIAL MAP =====
def astar(start, target):
    open_set = [start]
    came_from = {}

    g = {start: 0}
    f = {start: h(start, target)}

    while open_set:
        node = min(open_set, key=lambda pos: f.get(pos, float("inf")))

        if node == target:
            path = []
            while node in came_from:
                path.append(node)
                node = came_from[node]
            return path[::-1]

        open_set.remove(node)

        for dx, dy in moves:
            nx = node[0] + dx
            ny = node[1] + dy
            neighbor = (nx, ny)

            if nx < 0 or nx >= cols or ny < 0 or ny >= rows:
                continue

            if known_grid[ny][nx] == 1:
                continue

            cost = 1
            if known_grid[ny][nx] == -1:
                cost = 4  # higher penalty for unknown

            tentative_g = g[node] + cost

            if tentative_g < g.get(neighbor, float("inf")):
                came_from[neighbor] = node
                g[neighbor] = tentative_g
                f[neighbor] = tentative_g + h(neighbor, target)

                if neighbor not in open_set:
                    open_set.append(neighbor)

    return []

# ===== DRAW =====
def draw():
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

    # visited trail
    for p in visited_path:
        pygame.draw.rect(screen, GREEN,
            pygame.Rect(p[0]*cell_size, p[1]*cell_size, cell_size, cell_size))

    # target
    pygame.draw.rect(screen, RED,
        pygame.Rect(target[0]*cell_size, target[1]*cell_size, cell_size, cell_size))

    # agent
    pygame.draw.rect(screen, BLUE,
        pygame.Rect(current[0]*cell_size, current[1]*cell_size, cell_size, cell_size))

    pygame.display.update()

# ===== MAIN LOOP =====
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    update_vision()

    if current == target:
        print("Reached target!")
        break

    visited_path.append(current)

    path = astar(current, target)

    if path:
        current = path[0]
    else:
        # exploration fallback
        random.shuffle(moves)
        for dx, dy in moves:
            nx = current[0] + dx
            ny = current[1] + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                if known_grid[ny][nx] != 1:
                    current = (nx, ny)
                    break

    draw()
    time.sleep(0.12)

pygame.quit()
