## Pathfinding-Visualizer
This repository includes commonly utilized pathfinding algorithms implemented in C++, with a pygame window to demonstrate search patterns and returned paths in a grid environment. Currently, only Dijkstras is implemented, but A* will be added soon!

## Compiling pathfinding.cpp
g++ -std=c++17 -o pathfinding.exe pathfinding.cpp -I/opt/homebrew/include

## Running main pygame window
python3 grid.py