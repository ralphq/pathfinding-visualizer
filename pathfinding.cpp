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
    vector<vector<pair<int, int>>> prev(rows, vector<pair<int, int>>(cols, {-1, -1})); // to store the path

    // convert start and end from 1D to 2D coordinates
    // ensure start is within bounds
    int startRow = start / cols;
    // ensure start is within bounds
    int startCol = start % cols;
    // ensure end is within bounds
    int endRow = end / cols;
    // ensure end is within bounds
    int endCol = end % cols;

    // check if start and end are valid
    // invalid start or end position!
    if (grid[startRow][startCol] == 1 || grid[endRow][endCol] == 1) {
        cout << "invalid start or end position!" << endl;
        return;
    }

    dist[startRow][startCol] = 0;
    pq.push({0, {startRow, startCol}});

    vector<pair<int, int> > directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    // open a file to save the priority queue state
    ofstream pqFile("priority_queue.csv");
    if (!pqFile.is_open()) {
        cout << "unable to open file for writing priority queue!" << endl; // error handling
        return;
    }

    while (!pq.empty()) {
        auto current = pq.top(); // get the top element
        int currentDist = current.first; // access the distance
        auto currentCoords = current.second; // access the coordinates
        int x = currentCoords.first; // get x coordinate
        int y = currentCoords.second; // get y coordinate
        pq.pop();

        if (visited[x][y]) continue;
        visited[x][y] = true;

        // save the current state of the priority queue
        priority_queue<pair<int, pair<int, int>>, vector<pair<int, pair<int, int>>>, greater<pair<int, pair<int, int>>>> tempPQ = pq; // create a temporary copy of the priority queue
        pqFile << x << "," << y; // save the current node without parentheses
        while (!tempPQ.empty()) {
            auto [dist, coords] = tempPQ.top();
            tempPQ.pop();
            pqFile << "," << coords.first << "," << coords.second; // save the rest of the queue without parentheses
        }
        pqFile << endl; // new line for the next state

        // if we reached the end node
        if (x == endRow && y == endCol) {
            //cout << "Shortest path distance: " << currentDist << endl;

            // reconstruct the path
            vector<pair<int, int>> path;
            for (pair<int, int> at = {endRow, endCol}; at != make_pair(-1, -1); at = prev[at.first][at.second]) {
                path.push_back(at);
            }
            reverse(path.begin(), path.end());

            // save path to CSV
            ofstream outFile("path.csv"); // open a file to save the path
            if (outFile.is_open()) {
                for (const auto& p : path) {
                    outFile << p.first << "," << p.second << endl; // write each coordinate to the file
                }
                outFile.close(); // close the file
                //cout << "Path saved to path.csv" << endl; // confirmation message
            } else {
                //cout << "Unable to open file for writing!" << endl; // error handling
            }

            pqFile.close(); // close the priority queue file
            return;
        }

        for (const auto& dir : directions) {
            int newX = x + dir.first;
            int newY = y + dir.second;

            if (newX >= 0 && newX < rows && newY >= 0 && newY < cols && grid[newX][newY] != 1) {
                int newDist = currentDist + 1; // assuming each step has a cost of 1
                if (newDist < dist[newX][newY]) {
                    dist[newX][newY] = newDist;
                    pq.push({newDist, {newX, newY}});
                    prev[newX][newY] = {x, y}; // store the previous node
                }
            }
        }
    }

    cout << "No path found!" << endl;
    pqFile.close(); // close the priority queue file
}

int main() {
    // load grid from CSV
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

    int startNode = -1; // starting node index
    int endNode = -1;   // ending node index

    // find the indices of the elements with values 3 and 2
    for (int i = 0; i < grid.size(); ++i) {
        for (int j = 0; j < grid[i].size(); ++j) {
            if (grid[i][j] == 3) {
                startNode = i * grid[i].size() + j; // convert to single index
            }
            if (grid[i][j] == 2) {
                endNode = i * grid[i].size() + j; // convert to single index
            }
        }
    }

    // check if startNode and endNode were found
    if (startNode == -1 || endNode == -1) {
        cout << "Start or end node not found!" << endl;
        return 1;
    }

    // check if startNode and endNode are within the grid bounds
    if (startNode < 0 || startNode >= grid.size() * grid[0].size() || 
        endNode < 0 || endNode >= grid.size() * grid[0].size()) {
        cout << "Start or end node is out of bounds!" << endl;
        return 1;
    }

    dijkstra(grid, startNode, endNode);

    return 0;
}