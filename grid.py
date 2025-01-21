from dataclasses import dataclass
import pygame
import sys
import random
from enum import Enum
import numpy as np
from pathfinding import dijkstras
import os

@dataclass
class CellState:
    EMPTY: int = 0
    WALL: int = 1
    GOAL: int = 2
    PLAYER: int = 3

class Grid:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.grid = np.zeros((rows, cols), dtype=np.int8)
        self.states = CellState()
        self.player_pos = None
        self.goal_pos = None
    
    def generate_walls(self):
        self.grid.fill(self.states.EMPTY)  # Clear grid
        num_wall_blocks = (self.cols * self.rows) // 25
        
        for _ in range(num_wall_blocks):
            block_w = random.randint(2, 4)
            block_h = random.randint(2, 4)
            x = random.randint(0, self.cols - block_w)
            y = random.randint(0, self.rows - block_h)
            
            self.grid[y:y+block_h, x:x+block_w] = self.states.WALL

    def get_random_pos(self):
        while True:
            x = random.randint(0, self.cols-1)
            y = random.randint(0, self.rows-1)
            if self.grid[y, x] == self.states.EMPTY:
                return [x, y]

    def update_grid_state(self):
        # Clear previous player and goal positions
        self.grid[self.grid == self.states.PLAYER] = self.states.EMPTY
        self.grid[self.grid == self.states.GOAL] = self.states.EMPTY
        # Set new positions
        self.grid[self.goal_pos[1], self.goal_pos[0]] = self.states.GOAL
        self.grid[self.player_pos[1], self.player_pos[0]] = self.states.PLAYER

class GridWorld:
    def __init__(self, width=800, height=600, cell_size=25):
        pygame.init()
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("GridWorld")
        
        # Grid dimensions
        cols = width // cell_size
        rows = height // cell_size
        
        # Initialize grid
        self.grid = Grid(cols, rows)
        
        # Colors mapping
        self.colors = {
            self.grid.states.EMPTY: (0, 0, 0),      # Background
            self.grid.states.WALL: (100, 100, 100),  # Wall
            self.grid.states.GOAL: (0, 255, 0),      # Goal
            self.grid.states.PLAYER: (255, 0, 0)     # Player
        }
        self.grid_color = (50, 50, 50)
        
        # Initialize game state
        self.grid.generate_walls()
        self.grid.player_pos = self.grid.get_random_pos()
        self.grid.goal_pos = self.grid.get_random_pos()
        self.grid.update_grid_state()
        # self.print_grid()
        
        # Game clock
        self.clock = pygame.time.Clock()
        self.move_cooldown = 200
        self.last_move_time = 0
        
        # Button properties
        self.button_height = 40
        self.button_width = 120
        self.button_margin = 20
        self.button_color = (150, 150, 150)
        self.button_hover_color = (180, 180, 180)
        self.button_font = pygame.font.Font(None, 32)
        
        # Define buttons (x, y, width, height, text)
        self.buttons = [
            pygame.Rect(self.button_margin, height - self.button_height - self.button_margin, 
                       self.button_width, self.button_height),
            pygame.Rect(2 * self.button_margin + self.button_width, height - self.button_height - self.button_margin,
                       self.button_width, self.button_height)
        ]
        self.button_texts = ["New Grid", "Dijkstra's"]

        self.path = []  # Store the path here

    def draw_grid(self):
        # Draw cells
        for y in range(self.grid.rows):
            for x in range(self.grid.cols):
                cell_rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                cell_state = self.grid.grid[y, x]
                pygame.draw.rect(self.screen, self.colors[cell_state], cell_rect)
                
        # Draw path if it exists
        for node in self.path:
            path_x, path_y = node
            path_circle_x = path_x * self.cell_size + self.cell_size // 2
            path_circle_y = path_y * self.cell_size + self.cell_size // 2
            pygame.draw.circle(self.screen, (0, 191, 255), (path_circle_x, path_circle_y), self.cell_size // 4)

        # Draw grid lines
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.width, y))
            
        # Draw player as circle (on top of the cell)
        player_x = self.grid.player_pos[0] * self.cell_size + self.cell_size // 2
        player_y = self.grid.player_pos[1] * self.cell_size + self.cell_size // 2
        pygame.draw.circle(self.screen, self.colors[self.grid.states.PLAYER], 
                         (player_x, player_y), self.cell_size // 3)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button, text in zip(self.buttons, self.button_texts):
            color = self.button_hover_color if button.collidepoint(mouse_pos) else self.button_color
            pygame.draw.rect(self.screen, color, button)
            
            text_surface = self.button_font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=button.center)
            self.screen.blit(text_surface, text_rect)

    def handle_input(self):
        current_time = pygame.time.get_ticks()
        
        # Handle mouse clicks for buttons
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                if self.buttons[0].collidepoint(mouse_pos):
                    print("New Grid button clicked")  # Add debug print
                    self.grid.grid.fill(self.grid.states.EMPTY)  # Clear the grid first
                    self.grid.generate_walls()
                    self.grid.player_pos = self.grid.get_random_pos()
                    self.grid.goal_pos = self.grid.get_random_pos()
                    self.grid.update_grid_state()
                    self.path = []  # Clear the path when a new grid is generated
                    #self.print_grid()
                elif self.buttons[1].collidepoint(mouse_pos):
                    print("Dijkstra's button clicked")
                    # Create a dictionary with the required parameters
                    grid_data = {
                        'grid': self.grid.grid.tolist(),
                        'start': self.grid.player_pos,
                        'goal': self.grid.goal_pos
                    }
                    # Pass the dictionary as a single argument
                    # self.path = dijkstras(grid_data)  # Store the path
                    # if self.path:
                    #     print(f"Path found: {self.path}")
                    # else:
                    #     print("No path found!")

                    # You can keep the existing binary save/subprocess code if needed
                    self.save_to_csv('grid_state.csv')
                    import subprocess
                    import os
                    
                    # Get the current directory and construct full path to pathfinding.exe
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    exe_path = os.path.join(current_dir, 'pathfinding.exe')
                    
                    try:
                        subprocess.run([exe_path], check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Error running pathfinding.exe: {e}")
                    except FileNotFoundError:
                        print(f"pathfinding.exe not found at: {exe_path}")
        
        if current_time - self.last_move_time < self.move_cooldown:
            return
            
        keys = pygame.key.get_pressed()
        new_pos = self.grid.player_pos.copy()
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
            
        if moved and (0 <= new_pos[0] < self.grid.cols and 
                     0 <= new_pos[1] < self.grid.rows and
                     self.grid.grid[new_pos[1], new_pos[0]] != self.grid.states.WALL):
            self.grid.player_pos = new_pos
            self.last_move_time = current_time
            
            if self.grid.player_pos == self.grid.goal_pos:
                self.grid.generate_walls()
                self.grid.player_pos = self.grid.get_random_pos()
                self.grid.goal_pos = self.grid.get_random_pos()
                self.grid.update_grid_state()
                #self.print_grid()
            
            self.grid.update_grid_state()

    def run(self):
        running = True
        while running:
            # Remove the event handling from here since it's in handle_input()
            self.handle_input()
            self.draw_grid()
            
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

    def print_grid(self):
        # Print column numbers
        print("\n")
        print('   ', end='')  # Extra space for alignment
        for x in range(self.grid.cols):
            print(f'{x:2} ', end='')  # Added space after each number
        print()  # newline
        
        # Print grid with row numbers
        for y in range(self.grid.rows):
            print(f'{y:2} ', end='')  # Row number with space
            for x in range(self.grid.cols):
                print(f'{self.grid.grid[y,x]:2} ', end='')  # Added consistent spacing
            print()  # newline

    def save_to_csv(self, filename):
        """Save the current grid state to a CSV file."""
        # Save to CSV file
        np.savetxt(filename, self.grid.grid, delimiter=",", fmt='%d')

    def load_from_binary(self, filename):
        """Load grid state from a binary file."""
        # Read the file
        with open(filename, 'rb') as f:
            # Read header
            header = np.fromfile(f, dtype=np.uint64, count=2)
            rows, cols = header
            
            # Read data
            data = np.fromfile(f, dtype=np.float64)
            self.grid.grid = data.reshape((rows, cols))

# main
if __name__ == "__main__":
    gridworld = GridWorld()
    gridworld.run()