"""
Constants
"""
digits = '123456789'
rows = 'ABCDEFGHI'
cols = digits

def cross(a, b):
    return [s+t for s in a for t in b]

squares = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in squares)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in squares)

blank_map = dict((s, digits) for s in squares)



def solve(sudoku_string):
    """
    Args:
        sudoku_string: the string representation of the given sudoku map, comprised of 1-9, if the value is given, and 0 or *, if not
    Return:
        the dictionary form of a complete sudoku map if there is
        False if a contradiction is detected
    """
    def assign(sudoku_map, square, digit):
        """Assign digit to sudoku_map[square], eliminate all other possible digits from that square
    Return:
        modified sudoku_map if assignment proceeds successfully
        False if a contradiction is detected
    """
        other_values = sudoku_map[square].replace(digit, '')
        if all(eliminate(sudoku_map, square, d) for d in other_values):
            return sudoku_map
        else:
            return False
        
    
    def eliminate(sudoku_map, square, digit):
        """Eliminate digit from sudoku_map[square]
        Return:
            modified sudoku_map if elimination proceeds successfully
            False if a contradiction is detected,
        
        """
        if digit not in sudoku_map[square]:
            return sudoku_map   ## already eliminated
        
        sudoku_map[square] = sudoku_map[square].replace(digit, '')
        
        if len(sudoku_map[square]) == 0:
            return False    ## contradiction: remove the last value
        elif len(sudoku_map[square]) == 1:
            ## current square has only one possible value, put that value here and eliminate that value from all its peers
            if not all(eliminate(sudoku_map, s, sudoku_map[square]) for s in peers[square]):
                return False
        
        ## check whether a unit has only one possible place for digit
        for unit in units[square]:
            squares_contain_digit = [s for s in unit if digit in sudoku_map[s]]
            if len(squares_contain_digit) == 0:
                return False    ## contradiction: no place for digit
            elif len(squares_contain_digit) == 1:
                ## current unit has only one possible for digit, put it here
                if not assign(sudoku_map, squares_contain_digit[0], digit):
                    return False
        return sudoku_map
    
    def initiate_sudoku_map(sudoku_string):
        """Convert the string representation of sudoku to dictionary one: {square: digit}"""
        assert(len(sudoku_string) == 81)
        return dict(zip(squares, sudoku_string))
    
    
    def search(sudoku_map):
        """Using depth-first search to find the ultimate answer
        Args:
            sudoku_map(dict): a dictionary of the form {square: digit, ...}
        Return:
            the dictionary form of a complete sudoku map if there is
            False if a contradiction is detected
        """
        if sudoku_map is False:
            return False    ## Failed earlier
        if all(len(sudoku_map[s]) == 1 for s in squares):
            return sudoku_map  ## solved
        
        ## choose the unfilled square with the fewest choices
        choices, square = min((len(sudoku_map[s]), s) for s in squares if len(sudoku_map[s]) > 1)
        for d in sudoku_map[square]:
            new_sudoku_map = sudoku_map.copy()
            assign(new_sudoku_map, square, d)
            result = search(new_sudoku_map)
            if result:
                return result
        return False
    
    sudoku_map = blank_map.copy()
    
    for square, digit in initiate_sudoku_map(sudoku_string).items():
        if digit in digits and not assign(sudoku_map, square, digit):
            return False
    
    return search(sudoku_map)

def display(sudoku_map):
    """Display sudoku map in 2-D form"""
    width = 1+max(len(sudoku_map[s]) for s in squares)
    line = '+'.join(['-'*width*3]*3)
    for r in rows:
        print(''.join(sudoku_map[r+c].center(width) + ('|' if c in '36' else '') for c in cols))
        
        if r in 'CF':
            print(line)
    print()
    
diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
display(solve(diag_sudoku_grid))