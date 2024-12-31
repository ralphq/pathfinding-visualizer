#include <boost/iostreams/device/mapped_file.hpp>
#include <stdexcept>
#include <string>
#include <iostream>

class Grid {
private:
    boost::iostreams::mapped_file_source mmap;
    const double* data;
    size_t rows;
    size_t cols;

public:
    Grid(const std::string& filename) {
        // Open and map the file
        mmap.open(filename);
        if (!mmap.is_open()) {
            throw std::runtime_error("Cannot open file: " + filename);
        }

        // First 2 size_t values in the file are rows and cols
        const size_t* header = reinterpret_cast<const size_t*>(mmap.data());
        rows = header[0];
        cols = header[1];

        // Data starts after the header
        data = reinterpret_cast<const double*>(mmap.data() + 2 * sizeof(size_t));
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
        Grid grid("grid_data.bin");
        
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
} `