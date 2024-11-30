import pygame
import sys
import random
from enum import Enum

class Direction(Enum):
    UP = 0
    RIGHT = 1 
    DOWN = 2
    LEFT = 3

class GridWorld:
    # constructor
    def __init__(self, width=800, height=600, cell_size=50):
        pygame.init()
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("GridWorld")
        
        # getting grid dims
        self.cols = width // cell_size
        self.rows = height // cell_size
    
        # generate walls
        self.walls = set()    
        self.generate_walls()
        
        # initialize player and goal
        self.player_pos = self.get_random_pos()
        self.goal_pos = self.get_random_pos()
        
        # colors
        self.background_color = (0,0,0)
        self.grid_color = (200, 200, 200)
        self.wall_color = (100, 100, 100)
        self.goal_color = (0, 255, 0)
        self.player_color = (255, 0, 0)

        # game clock
        self.clock = pygame.time.Clock()
        
        # movement
        self.move_cooldown = 200  # milliseconds between moves
        self.last_move_time = 0

    def generate_walls(self):
        self.walls.clear()  # clear existing walls
        num_wall_blocks = (self.cols * self.rows) // 25  # adjust density of walls
        for _ in range(num_wall_blocks):

            # random block size between 2x2 and 4x4
            block_w = random.randint(2, 4)
            block_h = random.randint(2, 4)
            
            # random position for block
            x = random.randint(0, self.cols - block_w)
            y = random.randint(0, self.rows - block_h)
            
            # check if block would overlap with player position
            for i in range(block_w):
                for j in range(block_h):
                    self.walls.add((x + i, y + j))

    def get_random_pos(self):
        while True:
            x = random.randint(0, self.cols-1)
            y = random.randint(0, self.rows-1)
            pos = (x, y)
            
            # Check if position is on a wall
            if pos in self.walls:
                continue
            
            # Check if position overlaps with existing player or goal
            if hasattr(self, 'player_pos') and [x, y] == self.player_pos:
                continue
            if hasattr(self, 'goal_pos') and [x, y] == self.goal_pos:
                continue
            
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
            
        # draw goal as a square
        goal_rect = pygame.Rect(
            self.goal_pos[0] * self.cell_size,
            self.goal_pos[1] * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        pygame.draw.rect(self.screen, self.goal_color, goal_rect)
            
        # draw player as circle
        player_x = self.player_pos[0] * self.cell_size + self.cell_size // 2
        player_y = self.player_pos[1] * self.cell_size + self.cell_size // 2
        pygame.draw.circle(self.screen, self.player_color, (player_x, player_y), self.cell_size // 3)

    # handle player input
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
            
        # check boundaries, walls, and update position if moved
        if moved and (0 <= new_pos[0] < self.cols and 
            0 <= new_pos[1] < self.rows and
            tuple(new_pos) not in self.walls):
            self.player_pos = new_pos
            self.last_move_time = current_time
            
            # check if player reached goal
            if self.player_pos == self.goal_pos:
                # Reset player position and get new goal
                self.generate_walls()  # Generate new walls first
                self.player_pos = self.get_random_pos()  # Changed to use new method
                self.goal_pos = self.get_random_pos()    # Changed to use new method

    # main game loop
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

# main
if __name__ == "__main__":
    grid = GridWorld()
    grid.run()
