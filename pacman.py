import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pac-Man RL")

# Set up the clock for a decent frame rate
clock = pygame.time.Clock()

# Define tile size
tile_size = 40

# Define Pac-Man
pacman_size = 20
pacman_color = (255, 255, 0)  # Yellow
pacman_speed = tile_size // 4  # Adjust speed

def draw_pacman(x, y):
    pygame.draw.circle(screen, pacman_color, (x, y), pacman_size)

# Define Ghosts
ghost_size = 20
ghost_color = (255, 0, 0)  # Red
ghost_speed = tile_size // 4  # Adjust speed

def draw_ghost(x, y):
    pygame.draw.circle(screen, ghost_color, (x, y), ghost_size)

def move_ghost(ghost_x, ghost_y, pacman_x, pacman_y):
    directions = [(0, -ghost_speed), (0, ghost_speed), (-ghost_speed, 0), (ghost_speed, 0)]
    best_move = None
    min_distance = float('inf')

    if random.random() < 0.9:  # 90% chance to make a random move
        random.shuffle(directions)
        for direction in directions:
            new_x = ghost_x + direction[0]
            new_y = ghost_y + direction[1]
            if not check_collision(new_x, new_y):
                return new_x, new_y
    else:  # 10% chance to make a greedy move
        for direction in directions:
            new_x = ghost_x + direction[0]
            new_y = ghost_y + direction[1]
            if not check_collision(new_x, new_y):
                distance = abs(new_x - pacman_x) + abs(new_y - pacman_y)
                if distance < min_distance:
                    min_distance = distance
                    best_move = (new_x, new_y)

    if best_move:
        return best_move
    return ghost_x, ghost_y

# Define Pellets
pellet_size = 5
pellet_color = (255, 255, 255)  # White

def draw_pellets(pellets):
    for pellet in pellets:
        pygame.draw.circle(screen, pellet_color, pellet, pellet_size)

# Generate a new random maze
def generate_maze():
    maze = [[1 for _ in range(16)] for _ in range(11)]
    for row in range(1, 10):
        for col in range(1, 15):
            if random.random() > 0.2:
                maze[row][col] = 0
    return maze

# Draw the maze
def draw_maze(maze):
    for row_idx, row in enumerate(maze):
        for col_idx, tile in enumerate(row):
            if tile == 1:
                pygame.draw.rect(screen, (0, 0, 255), (col_idx * tile_size, row_idx * tile_size, tile_size, tile_size))

def check_collision(x, y):
    row = y // tile_size
    col = x // tile_size
    if maze[row][col] == 1:
        return True
    return False

# Check for collision with pellets
def check_pellet_collision(pacman_x, pacman_y, pellets):
    for pellet in pellets:
        if abs(pacman_x - pellet[0]) < pacman_size and abs(pacman_y - pellet[1]) < pacman_size:
            return pellet
    return None

# Check for collision with ghosts
def check_ghost_collision(pacman_x, pacman_y, ghost_x, ghost_y):
    return abs(pacman_x - ghost_x) < pacman_size and abs(pacman_y - ghost_y) < pacman_size

# Initialize game state
def initialize_game():
    global maze, pacman_x, pacman_y, ghost_x, ghost_y, pellets
    maze = generate_maze()
    while True:
        pacman_x = random.randint(1, 14) * tile_size
        pacman_y = random.randint(1, 9) * tile_size
        if not check_collision(pacman_x, pacman_y):
            break
    while True:
        ghost_x = random.randint(1, 14) * tile_size
        ghost_y = random.randint(1, 9) * tile_size
        if not check_collision(ghost_x, ghost_y):
            break
    pellets = [(col * tile_size + tile_size // 2, row * tile_size + tile_size // 2)
               for row in range(len(maze)) for col in range(len(maze[0])) if maze[row][col] == 0]

# Main game loop
def main():
    global pacman_x, pacman_y, pellets, ghost_x, ghost_y, maze
    score = 0
    initialize_game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if not check_collision(pacman_x - pacman_speed, pacman_y):
                pacman_x -= pacman_speed
        if keys[pygame.K_RIGHT]:
            if not check_collision(pacman_x + pacman_speed, pacman_y):
                pacman_x += pacman_speed
        if keys[pygame.K_UP]:
            if not check_collision(pacman_x, pacman_y - pacman_speed):
                pacman_y -= pacman_speed
        if keys[pygame.K_DOWN]:
            if not check_collision(pacman_x, pacman_y + pacman_speed):
                pacman_y += pacman_speed

        # Move ghost
        ghost_x, ghost_y = move_ghost(ghost_x, ghost_y, pacman_x, pacman_y)

        # Check for collisions
        collided_pellet = check_pellet_collision(pacman_x, pacman_y, pellets)
        if collided_pellet:
            pellets.remove(collided_pellet)
            score += 1

        if check_ghost_collision(pacman_x, pacman_y, ghost_x, ghost_y):
            print("Game Over")
            pygame.quit()
            sys.exit()

        # Check for win condition
        if not pellets:
            print(f"Level complete! Score: {score}")
            initialize_game()

        # Fill the screen with black
        screen.fill((0, 0, 0))

        # Draw the maze
        draw_maze(maze)

        # Draw Pac-Man
        draw_pacman(pacman_x, pacman_y)

        # Draw Ghost
        draw_ghost(ghost_x, ghost_y)

        # Draw Pellets
        draw_pellets(pellets)

        # Draw the score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(30)

if __name__ == "__main__":
    main()
