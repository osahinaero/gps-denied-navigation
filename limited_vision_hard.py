import pygame
import time
import random

# ===== USER INPUT =====
size = int(input("Enter odd grid size, like 15, 21, or 25: "))

# Maze generation works best with odd sizes
if size % 2 == 0:
    size += 1
    print("Even size detected. Using", size, "instead.")

rows = size
cols = size
cell_size = 35
vision_radius = 1

target = (cols - 1, rows - 1)

# ===== CREATE MAZE-LIKE TRUE MAP =====
grid = [[1 for _ in range(cols)] for _ in range(rows)]

def carve_path(x, y):
    grid[y][x] = 0

    directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
    random.shuffle(directions)

    for dx, dy in directions:
        nx = x + dx
        ny = y + dy

        if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 1:
            grid[y + dy // 2][x + dx // 2] = 0
            carve_path(nx, ny)

carve_path(0, 0)

# Ensure target is open and connected
grid[target[1]][target[0]] = 0
if target[0] > 0:
    grid[target[1]][target[0] - 1] = 0
if target[1] > 0:
    grid[target[1] - 1][target[0]] = 0

# ===== ADD EXTRA DEAD-END TRAPS =====
for _ in range(int(rows * cols * 0.08)):
    tx = random.randint(1, cols - 2)
    ty = random.randint(1, rows - 2)

    if grid[ty][tx] == 1:
        grid[ty][tx] = 0

        walls = [
            (tx + 1, ty),
            (tx - 1, ty),
            (tx, ty + 1),
            (tx, ty - 1)
        ]

        random.shuffle(walls)

        for wx, wy in walls[:3]:
            if 0 <= wx < cols and 0 <= wy < rows:
                grid[wy][wx] = 1

grid[0][0] = 0
grid[target[1]][target[0]] = 0

# ===== KNOWN MAP =====
# -1 = unknown, 0 = empty, 1 = wall/obstacle
known_grid = [[-1 for _ in range(cols)] for _ in range(rows)]

# ===== AGENT =====
current = (0, 0)
visited_path = []

moves = [(1, 0), (0, 1), (0, -1), (-1, 0)]

# ===== PYGAME SETUP =====
pygame.init()
width = cols * cell_size
height = rows * cell_size
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Limited Vision Maze Navigation")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (140, 140, 140)
LIGHT_GRAY = (210, 210, 210)

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def update_vision():
    for dy in range(-vision_radius, vision_radius + 1):
        for dx in range(-vision_radius, vision_radius + 1):
            nx = current[0] + dx
            ny = current[1] + dy

            if 0 <= nx < cols and 0 <= ny < rows:
                known_grid[ny][nx] = grid[ny][nx]

def astar(start, target):
    open_set = [start]
    came_from = {}

    g = {start: 0}
    f = {start: heuristic(start, target)}

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

            # Unknown cells are allowed, but risky
            cost = 1
            if known_grid[ny][nx] == -1:
                cost = 5

            tentative_g = g[node] + cost

            if tentative_g < g.get(neighbor, float("inf")):
                came_from[neighbor] = node
                g[neighbor] = tentative_g
                f[neighbor] = tentative_g + heuristic(neighbor, target)

                if neighbor not in open_set:
                    open_set.append(neighbor)

    return []

def draw():
    screen.fill(WHITE)

    for y in range(rows):
        for x in range(cols):
            rect = pygame.Rect(
                x * cell_size,
                y * cell_size,
                cell_size,
                cell_size
            )

            if known_grid[y][x] == -1:
                pygame.draw.rect(screen, GRAY, rect)
            elif known_grid[y][x] == 1:
                pygame.draw.rect(screen, BLACK, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)

            pygame.draw.rect(screen, LIGHT_GRAY, rect, 1)

    # visited trail
    for p in visited_path:
        pygame.draw.rect(
            screen,
            GREEN,
            pygame.Rect(
                p[0] * cell_size,
                p[1] * cell_size,
                cell_size,
                cell_size
            )
        )

    # target
    pygame.draw.rect(
        screen,
        RED,
        pygame.Rect(
            target[0] * cell_size,
            target[1] * cell_size,
            cell_size,
            cell_size
        )
    )

    # agent
    pygame.draw.rect(
        screen,
        BLUE,
        pygame.Rect(
            current[0] * cell_size,
            current[1] * cell_size,
            cell_size,
            cell_size
        )
    )

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
        draw()
        time.sleep(1)
        break

    if current not in visited_path:
        visited_path.append(current)

    path = astar(current, target)

    if path:
        current = path[0]
    else:
        print("No known path. Exploring nearby unknown space.")

        random.shuffle(moves)
        moved = False

        for dx, dy in moves:
            nx = current[0] + dx
            ny = current[1] + dy

            if 0 <= nx < cols and 0 <= ny < rows:
                if known_grid[ny][nx] != 1:
                    current = (nx, ny)
                    moved = True
                    break

        if not moved:
            print("Agent is trapped.")
            break

    draw()
    time.sleep(0.08)

pygame.quit()
