# Pathfinding-Visualizer
This repository includes commonly utilized pathfinding algorithms implemented in C++, with a pygame window to demonstrate search patterns and returned paths in a grid environment. Currently, only Dijkstras is implemented, but A* will be added soon!

## How to Run 

### Compiling pathfinding.cpp
`g++ -std=c++17 -o pathfinding.exe pathfinding.cpp -I/opt/homebrew/include`

### Running main pygame window
`python3 grid.py`

## How it Works
`pathfinding.cpp` contains the implemented algorithms, while `grid.py` runs the pygame window for visualization. The communication of data between the two files is done using temporary csv files (which are deleted automatically after the final path is visualized) as follows

1. `grid.py` randomly generates a grid with walls, a start node, and an end node. The player can also move the starting position manually at this stage.

2. When the user requests a certain pathfinding algorithm be visualized, the grid is saved off to a csv file where each node can take on one of the following values:
```
class CellState:
    EMPTY: int = 0
    WALL: int = 1
    GOAL: int = 2
    PLAYER: int = 3
```
`pathfinding.exe` is run at this point.
3. The pathfinding executable reads in grid_state.csv and returns two csv files

`priority_queue.csv` stores the values of priority_queue at each iteration of the requested algorithm in a row

`path.csv` contains the final path returned by the algorithm, where each *node* occupies a row

3. `grid.py` reads in the aforementioned csv files and plots the former in *pink* iteratively until the end node is found, at which point the latter is plotted in *blue.*