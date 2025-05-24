# Sparse Matrix Operations

Python program for arithmetic operations on sparse matrices. Stores only non-zero values for memory efficiency.

## Features

- Addition, subtraction, and multiplication of sparse matrices
- Memory-efficient storage (coordinate format)
- File I/O with text files
- Interactive command-line interface
- Input validation and error handling

## Usage

1. Place matrix files in `sample_inputs/`
2. Run: `python sparse_matrix.py`
3. Follow prompts to select operation
4. Results saved in `results/`

## File Format

```
rows=3
cols=3
(0, 0, 5.0)
(1, 2, 3.0)
(2, 1, -2.0)
```

## Operations

- **Addition/Subtraction**: Requires same dimensions, O(m + n) complexity
- **Multiplication**: Standard matrix rules apply, optimized for sparse data

Pure Python implementation using only standard libraries.
