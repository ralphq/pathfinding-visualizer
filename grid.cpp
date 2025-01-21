#include <stdexcept>
#include <string>
#include <iostream>
#include <fstream>
#include <sstream>

class Grid {
private:
    std::ifstream file; // Declare an ifstream to read from CSV
    double* data;
    size_t rows;
    size_t cols;

public:
    Grid(const std::string& filename) {
        // Open the CSV file
        std::ifstream file(filename);
        if (!file.is_open()) {
            throw std::runtime_error("Cannot open file: " + filename);
        }

        // Initialize row and column counts
        rows = 0;
        cols = 0;

        std::string line;
        // Count rows and determine the number of columns
        while (std::getline(file, line)) {
            if (rows == 0) {
                std::istringstream rowStream(line);
                std::string value;
                while (std::getline(rowStream, value, ',')) {
                    cols++; // Count columns based on commas
                }
            }
            rows++; // Increment row count
        }

        // Allocate memory for data
        data = new double[rows * cols];

        // Reset file stream to read data again
        file.clear();
        file.seekg(0);

        // Read the data into the array
        size_t i = 0;
        while (std::getline(file, line) && i < rows) {
            std::istringstream rowStream(line);
            for (size_t j = 0; j < cols; ++j) {
                if (!(rowStream >> data[i * cols + j])) {
                    throw std::runtime_error("Error reading data at row " + std::to_string(i));
                }
                rowStream.ignore(); // Ignore the comma
            }
            ++i;
        }

        file.close();
    }

    // Basic row-major access
    const double& at(size_t row, size_t col) const {
        if (row >= rows || col >= cols) {
            throw std::out_of_range("Grid index out of bounds");
        }
        return data[row * cols + col];
    }

    // Getters for dimensions
    size_t getRows() const { return rows; }
    size_t getCols() const { return cols; }

    // Print grid (for debugging)
    void print() const {
        for (size_t i = 0; i < rows; ++i) {
            for (size_t j = 0; j < cols; ++j) {
                std::cout << at(i, j) << " ";
            }
            std::cout << std::endl;
        }
    }
};

// Example main function to test the grid
int main() {
    try {
        Grid grid("grid_state.csv");  // Changed to read from CSV file
        
        // Print dimensions
        std::cout << "Grid dimensions: " << grid.getRows() << "x" << grid.getCols() << std::endl;
        
        // Print the grid
        grid.print();
        
        // Access specific elements
        std::cout << "Element at (1,1): " << grid.at(1, 1) << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    return 0;
} 