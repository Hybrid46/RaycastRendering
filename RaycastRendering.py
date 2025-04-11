import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FOV = math.pi / 3  # Field of view (60 degrees)
HALF_FOV = FOV / 2
CASTED_RAYS = WIDTH // 2
STEP_ANGLE = FOV / CASTED_RAYS
SCALE = WIDTH // CASTED_RAYS

# Mini-map settings
MAP_SCALE = 10  # Pixels per map cell
MAP_SIZE = 16    # Size of map (16x16)
MAP_POS = (WIDTH - MAP_SIZE*MAP_SCALE - 10, 10)  # Upper right corner

# 16x16 map (4x larger than original)
MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,0,1,0,0,1,0,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,0,1,0,1,1,0,1,0,0,1,0,1],
    [1,0,0,1,0,0,0,0,0,0,0,0,1,0,0,1],
    [1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1],
    [1,0,1,0,1,0,0,0,0,0,0,1,0,1,0,1],
    [1,0,1,0,1,0,0,0,0,0,0,1,0,1,0,1],
    [1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1],
    [1,0,0,1,0,0,0,0,0,0,0,0,1,0,0,1],
    [1,0,1,0,0,1,0,1,1,0,1,0,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,0,1,0,0,1,0,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# Player settings
player_x = 1.5
player_y = 1.5
player_angle = 0

# Colors
COLORS = {
    'sky': (100, 100, 255),
    'ground': (50, 50, 50),
    'wall1': (200, 0, 0),
    'wall2': (180, 0, 0),
    'wall_light': 2
}

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Raycaster")

clock = pygame.time.Clock()

def draw_minimap():
    # Draw map background
    pygame.draw.rect(screen, (30, 30, 30), (*MAP_POS, MAP_SIZE*MAP_SCALE, MAP_SIZE*MAP_SCALE))
    
    # Draw walls and empty spaces
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            if MAP[y][x] == 1:
                rect = (MAP_POS[0] + x*MAP_SCALE, MAP_POS[1] + y*MAP_SCALE, MAP_SCALE, MAP_SCALE)
                pygame.draw.rect(screen, (100, 100, 100), rect)
    
    # Draw player position
    player_map_x = int(MAP_POS[0] + player_x * MAP_SCALE)
    player_map_y = int(MAP_POS[1] + player_y * MAP_SCALE)
    pygame.draw.circle(screen, (0, 255, 0), (player_map_x, player_map_y), 3)
    
    # Draw direction line
    line_length = 15
    end_x = player_map_x + math.cos(player_angle) * line_length
    end_y = player_map_y + math.sin(player_angle) * line_length
    pygame.draw.line(screen, (255, 255, 255), (player_map_x, player_map_y), (end_x, end_y), 2)


def cast_rays():
    start_angle = player_angle - HALF_FOV
    for ray in range(CASTED_RAYS):
        for depth in range(1, 40):
            target_x = player_x + math.cos(start_angle) * depth
            target_y = player_y + math.sin(start_angle) * depth
            
            # Convert coordinates to map indices
            col = int(target_x)
            row = int(target_y)
            
            # Check map boundaries
            if row < 0 or row >= len(MAP) or col < 0 or col >= len(MAP[0]):
                break
            
            # Ray hits the wall
            if MAP[row][col] == 1:
                # Calculate distance and fix fish-eye effect
                distance = depth * math.cos(player_angle - start_angle)
                wall_height = int(HEIGHT / (distance + 0.0001))
                
                # Create wall rectangles
                color = COLORS['wall1'] if (row + col) % 2 else COLORS['wall2']
                if depth > COLORS['wall_light']:
                    color = tuple(c // 2 for c in color)
                
                pygame.draw.rect(
                    screen,
                    color,
                    (
                        ray * SCALE,
                        HEIGHT // 2 - wall_height // 2,
                        SCALE,
                        wall_height
                    )
                )
                break
        start_angle += STEP_ANGLE

running = True
while running:
    screen.fill(COLORS['sky'])
    pygame.draw.rect(screen, COLORS['ground'], (0, HEIGHT//2, WIDTH, HEIGHT))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Player controls (WSAD style)
    keys = pygame.key.get_pressed()
    
    # Rotation (A/D keys)
    if keys[pygame.K_a]: player_angle -= 0.1  # Left turn
    if keys[pygame.K_d]: player_angle += 0.1  # Right turn
    
    # Movement (W/S keys)
    move_step = 0.05
    if keys[pygame.K_w]:
        new_x = player_x + math.cos(player_angle) * move_step
        new_y = player_y + math.sin(player_angle) * move_step
        if 0 <= new_x < len(MAP[0]) and 0 <= new_y < len(MAP):
            if MAP[int(new_y)][int(new_x)] == 0:
                player_x, player_y = new_x, new_y

    if keys[pygame.K_s]:
        new_x = player_x - math.cos(player_angle) * move_step
        new_y = player_y - math.sin(player_angle) * move_step
        if 0 <= new_x < len(MAP[0]) and 0 <= new_y < len(MAP):
            if MAP[int(new_y)][int(new_x)] == 0:
                player_x, player_y = new_x, new_y
    
    cast_rays()
    draw_minimap()
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()