import pygame
import time

# ===== USER INPUT =====
size = int(input("Enter odd grid size, like 15, 21, or 25: "))

rows = size
cols = size
cell_size = 35
vision_radius = 1

grid = [[0 for _ in range(cols)] for _ in range(rows)]
known_grid = [[-1 for _ in range(cols)] for _ in range(rows)]

start = (0, 0)
target = (cols - 1, rows - 1)
current = start
visited_path = []

moves = [(1, 0), (0, 1), (0, -1), (-1, 0)]

pygame.init()
width = cols * cell_size
height = rows * cell_size + 70
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Blind Custom Environment Navigation")

font = pygame.font.SysFont(None, 30)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (140, 140, 140)
LIGHT_GRAY = (210, 210, 210)
BUTTON_GREEN = (120, 220, 120)

build_mode = True

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def update_vision():
    for dy in range(-vision_radius, vision_radius + 1):
        for dx in range(-vision_radius, vision_radius + 1):
            nx = current[0] + dx
            ny = current[1] + dy

            if 0 <= nx < cols and 0 <= ny < rows:
                known_grid[ny][nx] = grid[ny][nx]

def astar(start_pos, target_pos):
    open_set = [start_pos]
    came_from = {}

    g = {start_pos: 0}
    f = {start_pos: heuristic(start_pos, target_pos)}

    while open_set:
        node = min(open_set, key=lambda pos: f.get(pos, float("inf")))

        if node == target_pos:
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
                cost = 5

            tentative_g = g[node] + cost

            if tentative_g < g.get(neighbor, float("inf")):
                came_from[neighbor] = node
                g[neighbor] = tentative_g
                f[neighbor] = tentative_g + heuristic(neighbor, target_pos)

                if neighbor not in open_set:
                    open_set.append(neighbor)

    return []

def draw():
    screen.fill(WHITE)

    for y in range(rows):
        for x in range(cols):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)

            if build_mode:
                if grid[y][x] == 1:
                    pygame.draw.rect(screen, BLACK, rect)
                else:
                    pygame.draw.rect(screen, WHITE, rect)
            else:
                if known_grid[y][x] == -1:
                    pygame.draw.rect(screen, GRAY, rect)
                elif known_grid[y][x] == 1:
                    pygame.draw.rect(screen, BLACK, rect)
                else:
                    pygame.draw.rect(screen, WHITE, rect)

            pygame.draw.rect(screen, LIGHT_GRAY, rect, 1)

    for p in visited_path:
        pygame.draw.rect(
            screen,
            GREEN,
            pygame.Rect(p[0] * cell_size, p[1] * cell_size, cell_size, cell_size)
        )

    pygame.draw.rect(
        screen,
        RED,
        pygame.Rect(target[0] * cell_size, target[1] * cell_size, cell_size, cell_size)
    )

    pygame.draw.rect(
        screen,
        BLUE,
        pygame.Rect(current[0] * cell_size, current[1] * cell_size, cell_size, cell_size)
    )

    button_rect = pygame.Rect(width // 2 - 70, rows * cell_size + 15, 140, 40)
    pygame.draw.rect(screen, BUTTON_GREEN, button_rect)

    button_text = "START" if build_mode else "RUNNING"
    text = font.render(button_text, True, BLACK)
    screen.blit(text, (button_rect.x + 30, button_rect.y + 9))

    pygame.display.update()
    return button_rect

running = True

while running:
    button_rect = draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if build_mode:
                if my < rows * cell_size:
                    gx = mx // cell_size
                    gy = my // cell_size

                    # Left click: toggle obstacle
                    if event.button == 1:
                        if (gx, gy) != start and (gx, gy) != target:
                            grid[gy][gx] = 0 if grid[gy][gx] == 1 else 1

                    # Right click: set target
                    if event.button == 3:
                        if grid[gy][gx] == 0 and (gx, gy) != start:
                            target = (gx, gy)

                # Click START button
                if button_rect.collidepoint(mx, my):
                    build_mode = False
                    current = start
                    visited_path = []
                    known_grid = [[-1 for _ in range(cols)] for _ in range(rows)]

    if not build_mode:
        update_vision()

        if current == target:
            print("Reached target!")
            draw()
            time.sleep(1)
            running = False
            continue

        if current not in visited_path:
            visited_path.append(current)

        path = astar(current, target)

        if path:
            current = path[0]
        else:
            print("No known path. Exploring nearby unknown space.")
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
                time.sleep(1)
                running = False

        time.sleep(0.08)

pygame.quit()
