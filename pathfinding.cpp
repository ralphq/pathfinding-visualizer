#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <limits>
#include <sstream>

using namespace std;


void dijkstra(const vector<vector<int>>& grid, int start, int end) {
    int rows = grid.size();
    int cols = grid[0].size();
    vector<vector<int>> dist(rows, vector<int>(cols, numeric_limits<int>::max()));
    vector<vector<bool>> visited(rows, vector<bool>(cols, false));
    priority_queue<pair<int, pair<int, int>>, vector<pair<int, pair<int, int>>>, greater<pair<int, pair<int, int>>>> pq;
    vector<vector<pair<int, int>>> prev(rows, vector<pair<int, int>>(cols, {-1, -1})); // To store the path

    // Convert start and end from 1D to 2D coordinates
    int startRow = start / cols; // Ensure start is within bounds
    int startCol = start % cols; // Ensure start is within bounds
    int endRow = end / cols; // Ensure end is within bounds
    int endCol = end % cols; // Ensure end is within bounds

    // Check if start and end are valid
    if (grid[startRow][startCol] == 1 || grid[endRow][endCol] == 1) {
        cout << "Invalid start or end position!" << endl;
        return;
    }

    dist[startRow][startCol] = 0;
    pq.push({0, {startRow, startCol}});

    vector<pair<int, int> > directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    ofstream pqFile("priority_queue.csv"); // Open a file to save the priority queue state
    if (!pqFile.is_open()) {
        cout << "Unable to open file for writing priority queue!" << endl; // Error handling
        return;
    }

    while (!pq.empty()) {
        auto current = pq.top(); // Get the top element
        int currentDist = current.first; // Access the distance
        auto currentCoords = current.second; // Access the coordinates
        int x = currentCoords.first; // Get x coordinate
        int y = currentCoords.second; // Get y coordinate
        pq.pop();

        if (visited[x][y]) continue;
        visited[x][y] = true;

        // Save the current state of the priority queue
        priority_queue<pair<int, pair<int, int>>, vector<pair<int, pair<int, int>>>, greater<pair<int, pair<int, int>>>> tempPQ = pq; // Create a temporary copy of the priority queue
        pqFile << x << "," << y; // Save the current node without parentheses
        while (!tempPQ.empty()) {
            auto [dist, coords] = tempPQ.top();
            tempPQ.pop();
            pqFile << "," << coords.first << "," << coords.second; // Save the rest of the queue without parentheses
        }
        pqFile << endl; // New line for the next state

        // If we reached the end node
        if (x == endRow && y == endCol) {
            //cout << "Shortest path distance: " << currentDist << endl;

            // Reconstruct the path
            vector<pair<int, int>> path;
            for (pair<int, int> at = {endRow, endCol}; at != make_pair(-1, -1); at = prev[at.first][at.second]) {
                path.push_back(at);
            }
            reverse(path.begin(), path.end());

            /*
            cout << "Path: ";
            for (const auto& p : path) {
                cout << "(" << p.first << ", " << p.second << ") ";
            }
            cout << endl;
            */

            // Save path to CSV
            ofstream outFile("path.csv"); // Open a file to save the path
            if (outFile.is_open()) {
                for (const auto& p : path) {
                    outFile << p.first << "," << p.second << endl; // Write each coordinate to the file
                }
                outFile.close(); // Close the file
                //cout << "Path saved to path.csv" << endl; // Confirmation message
            } else {
                //cout << "Unable to open file for writing!" << endl; // Error handling
            }

            pqFile.close(); // Close the priority queue file
            return;
        }

        for (const auto& dir : directions) {
            int newX = x + dir.first;
            int newY = y + dir.second;

            if (newX >= 0 && newX < rows && newY >= 0 && newY < cols && grid[newX][newY] != 1) {
                int newDist = currentDist + 1; // Assuming each step has a cost of 1
                if (newDist < dist[newX][newY]) {
                    dist[newX][newY] = newDist;
                    pq.push({newDist, {newX, newY}});
                    prev[newX][newY] = {x, y}; // Store the previous node
                }
            }
        }
    }

    cout << "No path found!" << endl;
    pqFile.close(); // Close the priority queue file
}

int main() {
    // Load grid from CSV
    ifstream file("grid_state.csv");
    string line;
    vector<vector<int>> grid;

    while (getline(file, line)) {
        stringstream ss(line);
        string cell;
        vector<int> row;
        while (getline(ss, cell, ',')) {
            row.push_back(stoi(cell));
        }
        grid.push_back(row);
    }

    int startNode = -1; // Starting node index
    int endNode = -1;   // Ending node index

    // Find the indices of the elements with values 3 and 2
    for (int i = 0; i < grid.size(); ++i) {
        for (int j = 0; j < grid[i].size(); ++j) {
            if (grid[i][j] == 3) {
                startNode = i * grid[i].size() + j; // Convert to single index
            }
            if (grid[i][j] == 2) {
                endNode = i * grid[i].size() + j; // Convert to single index
            }
        }
    }

    // Check if startNode and endNode were found
    if (startNode == -1 || endNode == -1) {
        cout << "Start or end node not found!" << endl;
        return 1;
    }

    // Check if startNode and endNode are within the grid bounds
    if (startNode < 0 || startNode >= grid.size() * grid[0].size() || 
        endNode < 0 || endNode >= grid.size() * grid[0].size()) {
        cout << "Start or end node is out of bounds!" << endl;
        return 1;
    }

    dijkstra(grid, startNode, endNode);

    return 0;
}
