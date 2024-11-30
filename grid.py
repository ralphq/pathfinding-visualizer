import pygame
import sys
import random
from enum import Enum

class Direction(Enum):
    UP = 0
    RIGHT = 1 
    DOWN = 2
    LEFT = 3

class Grid:
    def __init__(self, width=800, height=600, cell_size=50):
        pygame.init()
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Grid Environment")
        
        # Calculate grid dimensions
        self.cols = width // cell_size
        self.rows = height // cell_size
        
        # Player properties
        self.player_pos = [1, 1]  # Start at cell (1,1)
        self.player_color = (255, 0, 0)
        
        # Initialize walls first so we can check them when placing goal
        self.walls = set()
        
        # Colors
        self.background_color = (0,0,0)
        self.grid_color = (200, 200, 200)
        self.wall_color = (100, 100, 100)
        
        self.clock = pygame.time.Clock()
        
        # Movement cooldown
        self.move_cooldown = 200  # milliseconds between moves
        self.last_move_time = 0

        # Goal properties - initialize before generating walls
        self.goal_color = (0, 255, 0)
        self.goal_pos = [1, 1]  # Set initial position
        
        # Generate walls
        self.generate_walls()
        
        # Now update goal position after walls are generated
        self.goal_pos = self.get_random_goal_pos()

    def generate_walls(self):
        self.walls.clear()  # Clear existing walls
        num_wall_blocks = (self.cols * self.rows) // 25  # Adjust density of walls
        for _ in range(num_wall_blocks):
            # Random block size between 2x2 and 4x4
            block_w = random.randint(2, 4)
            block_h = random.randint(2, 4)
            
            # Random position for block
            x = random.randint(0, self.cols - block_w)
            y = random.randint(0, self.rows - block_h)
            
            # Check if block would overlap with start or goal
            start_overlap = any((x+i,y+j) == (1,1) for i in range(block_w) for j in range(block_h))
            goal_overlap = any((x+i,y+j) == tuple(self.goal_pos) for i in range(block_w) for j in range(block_h))
            
            if not start_overlap and not goal_overlap:
                for i in range(block_w):
                    for j in range(block_h):
                        self.walls.add((x + i, y + j))

    def get_random_goal_pos(self):
        while True:
            x = random.randint(0, self.cols-1)
            y = random.randint(0, self.rows-1)
            # Make sure goal isn't at player start position or on a wall
            if [x, y] != [1, 1] and (x, y) not in self.walls:
                return [x, y]

    def draw_grid(self):
        self.screen.fill(self.background_color)
        
        # Draw vertical lines
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.height))
            
        # Draw horizontal lines
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.width, y))
            
        # Draw walls
        for wall in self.walls:
            wall_rect = pygame.Rect(
                wall[0] * self.cell_size,
                wall[1] * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(self.screen, self.wall_color, wall_rect)
            
        # Draw goal as a square
        goal_rect = pygame.Rect(
            self.goal_pos[0] * self.cell_size,
            self.goal_pos[1] * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        pygame.draw.rect(self.screen, self.goal_color, goal_rect)
            
        # Draw player
        player_x = self.player_pos[0] * self.cell_size + self.cell_size // 2
        player_y = self.player_pos[1] * self.cell_size + self.cell_size // 2
        pygame.draw.circle(self.screen, self.player_color, (player_x, player_y), self.cell_size // 3)

    def handle_input(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < self.move_cooldown:
            return
            
        keys = pygame.key.get_pressed()
        
        new_pos = self.player_pos.copy()
        moved = False
        
        if keys[pygame.K_LEFT]:
            new_pos[0] -= 1
            moved = True
        if keys[pygame.K_RIGHT]:
            new_pos[0] += 1
            moved = True
        if keys[pygame.K_UP]:
            new_pos[1] -= 1
            moved = True
        if keys[pygame.K_DOWN]:
            new_pos[1] += 1
            moved = True
            
        # Check boundaries, walls, and update position if moved
        if moved and (0 <= new_pos[0] < self.cols and 
            0 <= new_pos[1] < self.rows and
            tuple(new_pos) not in self.walls):
            self.player_pos = new_pos
            self.last_move_time = current_time
            
            # Check if player reached goal
            if self.player_pos == self.goal_pos:
                # Reset player position and get new goal
                self.player_pos = [1, 1]
                self.generate_walls()  # Generate new walls first
                self.goal_pos = self.get_random_goal_pos() # Then place goal

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            self.handle_input()
            self.draw_grid()
            
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    grid = Grid()
    grid.run()
