#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <limits>
#include <sstream>
#include <cmath>
#include <algorithm>

using namespace std;

void pathfinding(const vector<vector<int>>& grid, int start, int end, bool heuristic = false) {
    int rows = grid.size();
    int cols = grid[0].size();
    vector<vector<int>> dist(rows, vector<int>(cols, numeric_limits<int>::max()));
    vector<vector<bool>> visited(rows, vector<bool>(cols, false));
    // priority queue holds pairs of (fScore, (x, y))
    priority_queue<pair<int, pair<int, int>>, vector<pair<int, pair<int, int>>>, greater<pair<int, pair<int, int>>>> pq;
    vector<vector<pair<int, int>>> prev(rows, vector<pair<int, int>>(cols, {-1, -1})); // to store the path

    // convert start and end from 1D to 2D coordinates
    int startRow = start / cols;
    int startCol = start % cols;
    int endRow = end / cols;
    int endCol = end % cols;

    // check if start and end positions are valid (not on a wall)
    if (grid[startRow][startCol] == 1 || grid[endRow][endCol] == 1) {
        cout << "invalid start or end position!" << endl;
        return;
    }

    // For a standard A* implementation, the starting f value is f = g + h.
    // Here, g(start)=0 and h(start)= (if heuristic enabled) heuristicWeight * ManhattanDistance.
    int heuristicWeight = heuristic ? 10 : 0; // Increased weight makes A* more aggressive
    int startHeuristic = heuristic ? heuristicWeight * (abs(endRow - startRow) + abs(endCol - startCol)) : 0;
    dist[startRow][startCol] = startHeuristic;
    pq.push({startHeuristic, {startRow, startCol}});

    vector<pair<int, int>> directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    // open a file to save the priority queue state
    ofstream pqFile("priority_queue.csv");
    if (!pqFile.is_open()) {
        cout << "unable to open file for writing priority queue!" << endl;
        return;
    }

    // Initialize the heuristic grid if needed
    vector<vector<int>> heuristicGrid(rows, vector<int>(cols, 0));
    if (heuristic) {
        // Calculate Euclidean distance for each cell
        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < cols; ++j) {
                heuristicGrid[i][j] = sqrt(pow(endRow - i, 2) + pow(endCol - j, 2));
            }
        }
    }

    while (!pq.empty()) {
        auto current = pq.top();
        int currentF = current.first;
        auto [x, y] = current.second;
        pq.pop();

        if (visited[x][y])
            continue;
        visited[x][y] = true;

        // Save the current state of the priority queue to file.
        priority_queue<pair<int, pair<int, int>>, vector<pair<int, pair<int, int>>>, greater<pair<int, pair<int, int>>>> tempPQ = pq;
        pqFile << x << "," << y;
        while (!tempPQ.empty()) {
            auto [d, coords] = tempPQ.top();
            tempPQ.pop();
            pqFile << "," << coords.first << "," << coords.second;
        }
        pqFile << endl;

        // If reached the goal, reconstruct and save the path.
        if (x == endRow && y == endCol) {
            vector<pair<int, int>> path;
            for (pair<int, int> at = {endRow, endCol}; at != make_pair(-1, -1); at = prev[at.first][at.second]) {
                path.push_back(at);
            }
            reverse(path.begin(), path.end());

            ofstream outFile("path.csv");
            if (outFile.is_open()) {
                for (const auto& p : path) {
                    outFile << p.first << "," << p.second << endl;
                }
                outFile.close();
            }
            pqFile.close();
            return;
        }

        // Expand neighbors
        for (const auto& dir : directions) {
            int newX = x + dir.first;
            int newY = y + dir.second;

            if (newX >= 0 && newX < rows && newY >= 0 && newY < cols && grid[newX][newY] != 1) {
                // gCost is the actual cost from the start (each move costs 1)
                int gCost = (currentF - (heuristic ? heuristicWeight * heuristicGrid[x][y] : 0)) + 1;
                // hCost is the Euclidean distance multiplied by our aggressive weight
                int hCost = heuristic ? heuristicWeight * heuristicGrid[newX][newY] : 0;
                int newF = gCost + hCost;
                
                if (newF < dist[newX][newY]) {
                    dist[newX][newY] = newF;
                    pq.push({newF, {newX, newY}});
                    prev[newX][newY] = {x, y};
                }
            }
        }
    }

    cout << "No path found!" << endl;
    pqFile.close();
}

int main(int argc, char* argv[]) {
    ifstream file("grid_state.csv");
    string line;
    vector<vector<int>> grid;

    bool heuristic = false; // default
    if (argc > 1) {
        heuristic = (string(argv[1]) == "true");
    }

    while (getline(file, line)) {
        stringstream ss(line);
        string cell;
        vector<int> row;
        while (getline(ss, cell, ',')) {
            row.push_back(stoi(cell));
        }
        grid.push_back(row);
    }

    int startNode = -1; // starting node index
    int endNode = -1;   // ending node index

    // Locate start (3) and end (2) in the grid
    for (int i = 0; i < grid.size(); ++i) {
        for (int j = 0; j < grid[i].size(); ++j) {
            if (grid[i][j] == 3) {
                startNode = i * grid[i].size() + j;
            }
            if (grid[i][j] == 2) {
                endNode = i * grid[i].size() + j;
            }
        }
    }

    if (startNode == -1 || endNode == -1) {
        cout << "Start or end node not found!" << endl;
        return 1;
    }

    if (startNode < 0 || startNode >= grid.size() * grid[0].size() || 
        endNode < 0 || endNode >= grid.size() * grid[0].size()) {
        cout << "Start or end node is out of bounds!" << endl;
        return 1;
    }

    pathfinding(grid, startNode, endNode, heuristic);
    return 0;
}
