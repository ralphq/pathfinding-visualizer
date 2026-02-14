from dataclasses import dataclass
import pygame
import sys
import random
from enum import Enum
import numpy as np
import os
import csv
import subprocess
import os

# dataclass for each node in grid
@dataclass
class CellState:
    EMPTY: int = 0
    WALL: int = 1
    GOAL: int = 2
    PLAYER: int = 3

"""
Grid class is for the grid itself, but does not handle the 
pygame window at all (see GridWorld). It has methods for

- initializing grid
- generating pseudo-randomized walls
- creating random positions (used for start and end nodes)
- updating grid state (called when "New Grid" button is pressed)
"""
class Grid:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.grid = np.zeros((rows, cols), dtype=np.int8)
        self.states = CellState()
        self.player_pos = None
        self.goal_pos = None
    
    def generate_walls(self):
        self.grid.fill(self.states.EMPTY)  # clear grid
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
        # clear previous player and goal positions
        self.grid[self.grid == self.states.PLAYER] = self.states.EMPTY
        self.grid[self.grid == self.states.GOAL] = self.states.EMPTY
        # set new positions
        self.grid[self.goal_pos[1], self.goal_pos[0]] = self.states.GOAL
        self.grid[self.player_pos[1], self.player_pos[0]] = self.states.PLAYER

"""
The GridWorld class wraps a Grid, and is used for rendering and handling user input
with pygame. It has methods for

- pygame window 
- handling user input
    - generating new grid
    - calling pathfinding executable
- saving to/reading from csv files

"""
class GridWorld:
    def __init__(self, width=800, height=800, cell_size=25):
        """
        Class attributes for pygame window
        """
        pygame.init()
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("GridWorld")
        
        # grid dimensions
        self.grid_height = height - 100  # space for buttons
        self.grid_width = width
        self.cols = width // cell_size
        self.rows = self.grid_height // cell_size
        
        # initialize grid
        self.grid = Grid(self.cols, self.rows)
        
        # game clock
        self.clock = pygame.time.Clock()
        self.move_cooldown = 200
        self.last_move_time = 0
        
        """
        Class attributes for drawing grid
        """
        # colors mapping
        self.colors = {
            self.grid.states.EMPTY: (0, 0, 0),      # background
            self.grid.states.WALL: (100, 100, 100),  # wall
            self.grid.states.GOAL: (0, 255, 0),      # goal
            self.grid.states.PLAYER: (255, 0, 0)     # player
        }
        self.grid_color = (50, 50, 50)
        
        # initialize game state
        self.grid.generate_walls()
        self.grid.player_pos = self.grid.get_random_pos()
        self.grid.goal_pos = self.grid.get_random_pos()
        self.grid.update_grid_state()
        
        # store the path here
        self.path = []  

        """
        Class attributes for buttons
        """
        # button properties
        self.button_height = 50  # height for button area
        self.button_width = 120
        self.button_margin = 25
        self.button_color = (150, 150, 150)
        self.button_hover_color = (180, 180, 180)
        self.button_font = pygame.font.Font(None, 32)
        
        # define buttons (x, y, width, height, text)
        self.buttons = [
            pygame.Rect(self.button_margin, height - self.button_height - self.button_margin, 
                       self.button_width, self.button_height),
            pygame.Rect(2 * self.button_margin + self.button_width, height - self.button_height - self.button_margin,
                       self.button_width, self.button_height),
            pygame.Rect(3 * self.button_margin + 2 * self.button_width, height - self.button_height - self.button_margin,
                       self.button_width, self.button_height)                       
        ]
        self.button_texts = ["New Grid", "Dijkstra's", "A*"]

        self.queue_color = (0, 0, 0) 
        self.path_color = (0, 0, 0) 

    def draw_grid(self):
        # draw cells
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
                
        # draw path if it exists
        for node in self.path:
            path_x, path_y = node
            path_circle_x = path_x * self.cell_size + self.cell_size // 2
            path_circle_y = path_y * self.cell_size + self.cell_size // 2
            pygame.draw.circle(self.screen, self.path_color, (path_circle_x, path_circle_y), self.cell_size // 4)

        # draw grid lines
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.grid_height))
        for y in range(0, self.grid_height, self.cell_size):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.width, y))
            
        # draw player as circle (on top of the cell)
        player_x = self.grid.player_pos[0] * self.cell_size + self.cell_size // 2
        player_y = self.grid.player_pos[1] * self.cell_size + self.cell_size // 2
        pygame.draw.circle(self.screen, self.colors[self.grid.states.PLAYER], 
                         (player_x, player_y), self.cell_size // 3)

        # draw buttons in the bottom section
        mouse_pos = pygame.mouse.get_pos()
        for button, text in zip(self.buttons, self.button_texts):
            color = self.button_hover_color if button.collidepoint(mouse_pos) else self.button_color
            pygame.draw.rect(self.screen, color, button)
            
            text_surface = self.button_font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=button.center)
            self.screen.blit(text_surface, text_rect)

    def handle_input(self):
        current_time = pygame.time.get_ticks()
        
        # handle mouse clicks for buttons
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # left click
                mouse_pos = pygame.mouse.get_pos()
                if self.buttons[0].collidepoint(mouse_pos):
                    print("New Grid button clicked")  # debug print
                    self.reset_grid()  # method to reset grid and positions
                elif self.buttons[1].collidepoint(mouse_pos) or self.buttons[2].collidepoint(mouse_pos):
                    # save the current grid state to CSV
                    self.save_to_csv('grid_state.csv')
                    
                    # get the current directory and construct full path to pathfinding.exe
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    exe_path = os.path.join(current_dir, 'pathfinding.exe')
                    
                    # running cpp file
                    try:
                        if(self.buttons[1].collidepoint(mouse_pos)):
                            print("Dijkstra's button clicked")
                            subprocess.run([exe_path, 'false'], check=True)
                            self.path_color = (0, 191, 255)  
                            self.queue_color = (255, 105, 180)
                        else:
                            print("A* button clicked")
                            subprocess.run([exe_path, 'true'], check=True)
                            self.path_color = (255, 165, 0)  
                            self.queue_color = (150, 100, 200) 
                    except subprocess.CalledProcessError as e:
                        print(f"Error running pathfinding.exe: {e}")
                    except FileNotFoundError:
                        print(f"pathfinding.exe not found at: {exe_path}")

                    # plot priority queue from csv file generated by pathfinding.cpp
                    self.plot_priority_queue()

                    # read the path from the CSV file
                    path = []
                    with open('path.csv', 'r') as f:
                        for line in f:
                            x, y = map(int, line.strip().split(','))
                            path.append((x, y))
                    
                    # store the path for drawing, ensuring each position is its own line
                    # note: have to switch the indices for some reason, still working on it
                    self.path = [(x, y) for y, x in path]

                    # delete the CSV files after processing
                    os.remove('path.csv')
                    os.remove('grid_state.csv')
                    os.remove('priority_queue.csv')
                    
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
        # check if the player has moved and if the new position is within grid bounds and not a wall
        if moved and (0 <= new_pos[0] < self.grid.cols and 
                     0 <= new_pos[1] < self.grid.rows and
                     self.grid.grid[new_pos[1], new_pos[0]] != self.grid.states.WALL):
            # update the player's position to the new position
            self.grid.player_pos = new_pos
            # update the last move time to the current time
            self.last_move_time = current_time
            
            # check if the player has reached the goal position
            if self.grid.player_pos == self.grid.goal_pos:
                # reset grid and positions when the player reaches the goal
                self.reset_grid()  # call to reset_grid method
            
            # update the grid state to reflect the new player position
            self.grid.update_grid_state()

    def run(self):
        running = True
        while running:
            # remove the event handling from here since it's in handle_input()
            self.handle_input()
            self.draw_grid()
            
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()
    
    def save_to_csv(self, filename):
        """save the current grid state to a CSV file."""
        # save to CSV file
        np.savetxt(filename, self.grid.grid, delimiter=",", fmt='%d')

    def plot_priority_queue(self):
        with open('priority_queue.csv', 'r') as file:
            reader = csv.reader(file)
            previous_pairs = []  # store previous pairs to erase them
            for row in reader:
                # extract pairs from the row, ensuring each pair is treated as a single tuple
                pairs = [(int(row[i]), int(row[i + 1])) for i in range(0, len(row), 2)]  # create tuples from pairs

                # plot each pair as a pink dot
                for x, y in pairs:
                    circle_x = x * self.cell_size + self.cell_size // 2
                    circle_y = y * self.cell_size + self.cell_size // 2
                    pygame.draw.circle(self.screen, self.queue_color, (circle_y, circle_x), self.cell_size // 4)

                previous_pairs = pairs  # update previous pairs for the next iteration
                
                pygame.display.flip()  # update the display
                pygame.time.delay(20)  # display each row for 1 second

    def reset_grid(self):
        """reset the grid and generate new player and goal positions."""
        self.grid.grid.fill(self.grid.states.EMPTY)  # clear the grid first
        self.grid.generate_walls()
        self.grid.player_pos = self.grid.get_random_pos()
        self.grid.goal_pos = self.grid.get_random_pos()
        self.grid.update_grid_state()  # update grid state after resetting
        self.path = []  # clear path when new grid button is pressed

# main
if __name__ == "__main__":
    gridworld = GridWorld()
    gridworld.run()