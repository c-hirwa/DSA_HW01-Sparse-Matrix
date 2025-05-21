import re
import os

class SparseMatrix:
    def __init__(self, matrix_file_path=None, num_rows=None, num_cols=None):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.elements = {}
        if matrix_file_path:
            self._read_matrix_from_file(matrix_file_path)
    
    def _read_matrix_from_file(self, matrix_file_path):
        try:
            with open(matrix_file_path, 'r') as file:
                lines = file.readlines()
                self.num_rows = int(lines[0].split('=')[1].strip())
                self.num_cols = int(lines[1].split('=')[1].strip())
                for line in lines[2:]:
                    if line.strip():
                        entry = line.strip('()\n')
                        row, col, value = map(int, entry.split(','))
                        self.elements[(row, col)] = value
        except Exception as e:
            raise ValueError(f"Input file has wrong format: {e}")
    
    def get_element(self, row, col):
        return self.elements.get((row, col), 0)
    
    def set_element(self, row, col, value):
        if value != 0:
            self.elements[(row, col)] = value
        elif (row, col) in self.elements:
            del self.elements[(row, col)]
    
    def __str__(self):
        result = [f"rows={self.num_rows}", f"cols={self.num_cols}"]
        for (row, col), value in sorted(self.elements.items()):
            result.append(f"({row}, {col}, {value})")
        return '\n'.join(result)
    
    def __add__(self, other):
        if self.num_rows != other.num_rows or self.num_cols != other.num_cols:
            raise ValueError("Matrices dimensions do not match for addition")
        
        result = SparseMatrix(num_rows=self.num_rows, num_cols=self.num_cols)
        # Add all elements from self
        for (row, col), value in self.elements.items():
            result.elements[(row, col)] = value
        
        # Add or update elements from other
        for (row, col), value in other.elements.items():
            result.elements[(row, col)] = result.get_element(row, col) + value
            if result.elements[(row, col)] == 0:
                del result.elements[(row, col)]
                
        return result
    
    def __sub__(self, other):
        if self.num_rows != other.num_rows or self.num_cols != other.num_cols:
            raise ValueError("Matrices dimensions do not match for subtraction")
        
        result = SparseMatrix(num_rows=self.num_rows, num_cols=self.num_cols)
        # Add all elements from self
        for (row, col), value in self.elements.items():
            result.elements[(row, col)] = value
        
        # Subtract elements from other
        for (row, col), value in other.elements.items():
            result.set_element(row, col, result.get_element(row, col) - value)
                
        return result
    
    def __mul__(self, other):
        if self.num_cols != other.num_rows:
            raise ValueError("Matrices dimensions do not match for multiplication")
        
        result = SparseMatrix(num_rows=self.num_rows, num_cols=other.num_cols)
        
        # Group elements by row in self and by column in other for faster access
        self_by_row = {}
        other_by_col = {}
        
        for (row, col), value in self.elements.items():
            if row not in self_by_row:
                self_by_row[row] = {}
            self_by_row[row][col] = value
            
        for (row, col), value in other.elements.items():
            if col not in other_by_col:
                other_by_col[col] = {}
            other_by_col[col][row] = value
        
        # Perform multiplication only where needed
        for i in self_by_row:
            for j in other_by_col:
                product_sum = sum(self_by_row[i].get(k, 0) * other_by_col[j].get(k, 0) 
                               for k in set(self_by_row[i]) & set(other_by_col[j]))
                if product_sum != 0:
                    result.elements[(i, j)] = product_sum
                    
        return result


def matrix_operation(input_dir, output_dir, operation_name, operation_func, dimension_check):
    """Generic function to handle matrix operations with proper validations"""
    matrix_files = [f for f in os.listdir(input_dir) if f.startswith('matrix') and f.endswith('.txt')]
    if not matrix_files:
        print("No matrix files found in the input directory.")
        return
    
    # Find compatible matrices
    compatible_pairs = []
    for i, file1 in enumerate(matrix_files):
        matrix1 = SparseMatrix(os.path.join(input_dir, file1))
        for j, file2 in enumerate(matrix_files):
            if i != j:
                matrix2 = SparseMatrix(os.path.join(input_dir, file2))
                if dimension_check(matrix1, matrix2):
                    compatible_pairs.append((i, j))
    
    # Display available matrices with recommendations
    print(f"\nSelect matrices for {operation_name}:")
    print("Available matrix files:")
    for i, file in enumerate(matrix_files):
        recommendation = " (recommended)" if any(i in pair for pair in compatible_pairs) else ""
        print(f"{i + 1}. {file}{recommendation}")
    
    # Get user selections
    try:
        choice1 = int(input("Select first matrix (by number): ")) - 1
        choice2 = int(input("Select second matrix (by number): ")) - 1
        if choice1 < 0 or choice1 >= len(matrix_files) or choice2 < 0 or choice2 >= len(matrix_files):
            print("Invalid selection. Please choose a number from the list.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Load matrices and perform operation
    matrix1 = SparseMatrix(os.path.join(input_dir, matrix_files[choice1]))
    matrix2 = SparseMatrix(os.path.join(input_dir, matrix_files[choice2]))
    
    if not dimension_check(matrix1, matrix2):
        print(f"{operation_name.capitalize()} Error: Matrices dimensions do not match")
        return
    
    try:
        result = operation_func(matrix1, matrix2)
        print(f"\n{operation_name.capitalize()} Result:")
        print(result)
        with open(os.path.join(output_dir, f'result_{operation_name}.txt'), 'w') as file:
            file.write(str(result))
    except ValueError as e:
        print(f"{operation_name.capitalize()} Error: {e}")


def main():
    # Define directories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.abspath(os.path.join(script_dir, '../sample_inputs/'))
    output_dir = os.path.abspath(os.path.join(script_dir, '../results/'))
    
    # Ensure directories exist
    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' does not exist.")
        return
    os.makedirs(output_dir, exist_ok=True)
    
    # Define operation parameters
    operations = {
        1: {
            'name': 'addition',
            'func': lambda a, b: a + b,
            'check': lambda a, b: a.num_rows == b.num_rows and a.num_cols == b.num_cols
        },
        2: {
            'name': 'subtraction',
            'func': lambda a, b: a - b,
            'check': lambda a, b: a.num_rows == b.num_rows and a.num_cols == b.num_cols
        },
        3: {
            'name': 'multiplication',
            'func': lambda a, b: a * b,
            'check': lambda a, b: a.num_cols == b.num_rows
        }
    }
    
    # Let user choose operation
    print("Choose an operation:")
    for op_num, op_details in operations.items():
        print(f"{op_num}. {op_details['name'].capitalize()}")
    
    try:
        choice = int(input("Enter the operation number: "))
        if choice not in operations:
            print("Invalid choice. Please select a valid operation.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Perform selected operation
    operation = operations[choice]
    matrix_operation(input_dir, output_dir, operation['name'], operation['func'], operation['check'])


if __name__ == "__main__":
    main()
