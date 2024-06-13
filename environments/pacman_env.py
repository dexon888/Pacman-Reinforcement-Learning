import gym
from gym import spaces
import numpy as np
import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Define tile size
tile_size = 40

class PacmanEnv(gym.Env):
    def __init__(self):
        super(PacmanEnv, self).__init__()

        # Define action and observation space
        self.action_space = spaces.Discrete(4)  # Up, Down, Left, Right
        self.observation_space = spaces.Box(low=0, high=255, shape=(600, 800, 3), dtype=np.uint8)

        # Set up display
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Pac-Man RL")

        # Set up the clock for a decent frame rate
        self.clock = pygame.time.Clock()

        # Define Pac-Man
        self.pacman_size = 20
        self.pacman_color = (255, 255, 0)  # Yellow
        self.pacman_speed = tile_size // 4  # Adjust speed

        # Define Ghosts
        self.ghost_size = 20
        self.ghost_color = (255, 0, 0)  # Red
        self.ghost_speed = tile_size // 4  # Adjust speed

        # Define Pellets
        self.pellet_size = 5
        self.pellet_color = (255, 255, 255)  # White

        self.score = 0
        self.done = False

        self.reset()

    def reset(self):
        self.maze = self.generate_maze()
        self.pacman_x, self.pacman_y = self.get_random_position()
        self.ghost_x, self.ghost_y = self.get_random_position()
        self.pellets = [(col * tile_size + tile_size // 2, row * tile_size + tile_size // 2)
                        for row in range(len(self.maze)) for col in range(len(self.maze[0])) if self.maze[row][col] == 0]
        self.score = 0
        self.done = False
        return self.get_state()

    def step(self, action):
        if action == 0 and not self.check_collision(self.pacman_x, self.pacman_y - self.pacman_speed):  # Up
            self.pacman_y -= self.pacman_speed
        elif action == 1 and not self.check_collision(self.pacman_x, self.pacman_y + self.pacman_speed):  # Down
            self.pacman_y += self.pacman_speed
        elif action == 2 and not self.check_collision(self.pacman_x - self.pacman_speed, self.pacman_y):  # Left
            self.pacman_x -= self.pacman_speed
        elif action == 3 and not self.check_collision(self.pacman_x + self.pacman_speed, self.pacman_y):  # Right
            self.pacman_x += self.pacman_speed

        self.ghost_x, self.ghost_y = self.move_ghost(self.ghost_x, self.ghost_y, self.pacman_x, self.pacman_y)

        reward = -1  # Small negative reward for each step
        if self.check_ghost_collision(self.pacman_x, self.pacman_y, self.ghost_x, self.ghost_y):
            reward = -100  # Large negative reward for ghost collision
            self.done = True

        collided_pellet = self.check_pellet_collision(self.pacman_x, self.pacman_y, self.pellets)
        if collided_pellet:
            self.pellets.remove(collided_pellet)
            reward = 10  # Positive reward for collecting a pellet
            self.score += 1

        if not self.pellets:
            reward = 100  # Large positive reward for collecting all pellets
            self.done = True

        state = self.get_state()
        return state, reward, self.done, {}

    def render(self, mode='human'):
        self.screen.fill((0, 0, 0))
        self.draw_maze(self.maze)
        self.draw_pacman(self.pacman_x, self.pacman_y)
        self.draw_ghost(self.ghost_x, self.ghost_y)
        self.draw_pellets(self.pellets)
        pygame.display.flip()
        self.clock.tick(30)

    def get_state(self):
        return pygame.surfarray.array3d(pygame.display.get_surface())

    def generate_maze(self):
        maze = [[1 for _ in range(16)] for _ in range(11)]
        for row in range(1, 10):
            for col in range(1, 15):
                if random.random() > 0.2:
                    maze[row][col] = 0
        return maze

    def get_random_position(self):
        while True:
            x = random.randint(1, 14) * tile_size
            y = random.randint(1, 9) * tile_size
            if not self.check_collision(x, y):
                return x, y

    def check_collision(self, x, y):
        row = y // tile_size
        col = x // tile_size
        return self.maze[row][col] == 1

    def check_pellet_collision(self, pacman_x, pacman_y, pellets):
        for pellet in pellets:
            if abs(pacman_x - pellet[0]) < self.pacman_size and abs(pacman_y - pellet[1]) < self.pacman_size:
                return pellet
        return None

    def check_ghost_collision(self, pacman_x, pacman_y, ghost_x, ghost_y):
        return abs(pacman_x - ghost_x) < self.pacman_size and abs(pacman_y - ghost_y) < self.pacman_size

    def move_ghost(self, ghost_x, ghost_y, pacman_x, pacman_y):
        directions = [(0, -self.ghost_speed), (0, self.ghost_speed), (-self.ghost_speed, 0), (self.ghost_speed, 0)]
        best_move = None
        min_distance = float('inf')

        if random.random() < 0.9:  # 90% chance to make a random move
            random.shuffle(directions)
            for direction in directions:
                new_x = ghost_x + direction[0]
                new_y = ghost_y + direction[1]
                if not self.check_collision(new_x, new_y):
                    return new_x, new_y
        else:  # 10% chance to make a greedy move
            for direction in directions:
                new_x = ghost_x + direction[0]
                new_y = ghost_y + direction[1]
                if not self.check_collision(new_x, new_y):
                    distance = abs(new_x - pacman_x) + abs(new_y - pacman_y)
                    if distance < min_distance:
                        min_distance = distance
                        best_move = (new_x, new_y)

        if best_move:
            return best_move
        return ghost_x, ghost_y

    def draw_pacman(self, x, y):
        pygame.draw.circle(self.screen, self.pacman_color, (x, y), self.pacman_size)

    def draw_ghost(self, x, y):
        pygame.draw.circle(self.screen, self.ghost_color, (x, y), self.ghost_size)

    def draw_pellets(self, pellets):
        for pellet in pellets:
            pygame.draw.circle(self.screen, self.pellet_color, pellet, self.pellet_size)

    def draw_maze(self, maze):
        for row_idx, row in enumerate(maze):
            for col_idx, tile in enumerate(row):
                if tile == 1:
                    pygame.draw.rect(self.screen, (0, 0, 255), (col_idx * tile_size, row_idx * tile_size, tile_size, tile_size))

