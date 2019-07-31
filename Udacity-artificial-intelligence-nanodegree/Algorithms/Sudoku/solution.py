from numpy import square
digits = '123456789'
rows = 'ABCDEFGHI'
cols = digits

def cross(a, b):
    return [s+t for s in a for t in b]

def pair(a, b):
    assert len(a) == len(b)
    result = []
    for i in range(len(a)):
        result.append(a[i]+b[i])
    return result
squares = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in squares)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in squares)

diagonal_units = [[r+c for r, c in zip(rows, cols)], [r+c for r, c in zip(rows, cols[::-1])]]
diagonal_unitlist = unitlist + diagonal_units
diagonal_units = dict((s, [u for u in diagonal_unitlist if s in u]) for s in squares)
diagonal_peers = dict((s, set(sum(diagonal_units[s],[]))-set([s])) for s in squares)

blank_map = dict((s, digits) for s in squares)

assignments = []

def assign_value(sudoku_map, box, value):
    """
    Please use this function to update your sudoku_map dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    sudoku_map[box] = value
    if len(value) == 1:
        assignments.append(sudoku_map.copy())
    return sudoku_map

def naked_twins(sudoku_map):
    """Eliminate values using the naked twins strategy.
    Args:
        sudoku_map(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the sudoku_map with the naked twins eliminated from peers.
    """
    for unit in unitlist:
        squares_with_two_values = [s for s in unit if len(sudoku_map[s]) == 2]
        twins = []
        length = len(squares_with_two_values)
        # Find naked twins in the unit
        for i, square1 in enumerate(squares_with_two_values, 1):
            for square2 in squares_with_two_values[i:]:
                if sudoku_map[square1] == sudoku_map[square2]:
                    twins.append((square1, square2))
                    break
                
        # Eliminate twins from other squares in the same unit
        for x, y in twins:
            for value in sudoku_map[x]:
                squares_contain_value = [s for s in unit if s != x and s != y and value in sudoku_map[s]]
                for s in squares_contain_value:
                    sudoku_map[s] = sudoku_map[s].replace(value, '')
    return sudoku_map

def cross(A, B):
    """Cross product of elements in A and elements in B."""
    return [a+b for a in A for b in B]

def grid_values(grid):
    """Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Return:
        A grid in dictionary form
            Keys: The squares, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert(len(grid) == 81)
    chars = []
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    return dict(zip(squares, chars))
    

def display(sudoku_map):
    """Display the values as a 2-D grid.
    Args:
        sudoku_map(dict): The sudoku in dictionary form
    """
    width = 1+max(len(sudoku_map[s]) for s in squares)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(sudoku_map[r+c].center(width) + ('|' if c in '36' else '') for c in cols))
        
        if r in 'CF':
            print(line)
    print


def eliminate(sudoku_map):
    """Go through all the squares, and whenever there is a square with a value, eliminate this value from the values of all its peers."""
    solved_squares = [s for s in squares if len(sudoku_map[s]) == 1]
    
    for square in solved_squares:
        value = sudoku_map[square]
        for peer in diagonal_peers[square]:
            sudoku_map[peer] = sudoku_map[peer].replace(value, '')
    return sudoku_map

def only_choice(sudoku_map):
    """Go through all the units, and whenever there is a unit with a value that only fits in one square, assign the value to this square."""
    for unit in diagonal_unitlist:
        for digit in '123456789':
            squares_contain_digit = [s for s in unit if digit in sudoku_map[s]]
            if len(squares_contain_digit) == 1:
                assign_value(sudoku_map, squares_contain_digit[0], digit)
    
    return sudoku_map

def reduce_puzzle(sudoku_map):
    stalled = False
    while not stalled:
        # Check how many squares have a determined value
        solved_squares_before = len([s for s in squares if len(sudoku_map[s]) == 1])

        # Use the Eliminate Strategy
        eliminate(sudoku_map)
        # Use the Only Choice Strategy
        only_choice(sudoku_map)
        # Check how many squares have a determined value, after our Strategies are applied
        solved_squares_after = len([s for s in squares if len(sudoku_map[s]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_squares_before == solved_squares_after
        # Sanity check, return False if there is a square with zero available values:
        if len([s for s in squares if len(sudoku_map[s]) == 0]):
            return False
    return sudoku_map

def search(sudoku_map):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    sudoku_map = reduce_puzzle(sudoku_map)
    if sudoku_map is False:
        return False ## Failed earlier
    if all(len(sudoku_map[s]) == 1 for s in squares): 
        return sudoku_map ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(sudoku_map[s]), s) for s in squares if len(sudoku_map[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in sudoku_map[s]:
        new_sudoku = sudoku_map.copy()
        assign_value(new_sudoku, s, value)
        attempt = search(new_sudoku)
        if attempt:
            return attempt
        

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    sudoku_map = grid_values(grid)
    return search(sudoku_map)
    

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
