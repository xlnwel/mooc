"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random
import queue
from copy import copy


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    return heuristic_func_4(game, player)

def heuristic_func_1(game, player):
    """Simply return the difference between player's legal moves  
    and two times that of its opponent
    """
    
    if game.is_winner(player):
        return float('inf')
    if game.is_loser(player):
        return float('-inf')
    
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    
    return float(own_moves - opp_moves)

def reachable_postion_counter(game, player):
    """ Use breadth-first search to find the number of potentially reachable positions 
    and return 
    """
    board_height = game.height
    board_width = game.width
    
    def get_surrounding_blank_positions(board, pos):
        """ Return the surrounding blank positions of pos """
        row, col = pos
        directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                      (1, -2), (1, 2), (2, -1), (2, 1)]
        blank_positions = [(row + dr, col + dc) for dr, dc in directions
                           if 0 <= row + dr < board_height 
                           and 0 <= col + dc < board_width
                           and board[row + dr + (col + dc) * board_height] == 0]
        return blank_positions

    def explore_position(q, explored_set, pos):
        """ Put pos in q, add it to explored_set, and set pos on board 1"""
        q.put(pos)
        explored_set.add(pos)
        board[pos[0] + pos[1] * board_height] = 1
    
    board = copy(game._board_state[:-3])
    current_pos = game.get_player_location(player)
    
    q = queue.Queue()
    explored_set = set()
    q.put(current_pos)
    count = 0
        
    while not q.empty():
        current_pos = q.get()
        count += 1
        for pos in get_surrounding_blank_positions(board, current_pos):
            if pos not in explored_set:
                explore_position(q, explored_set, pos)
            
    return count

def heuristic_func_2(game, player):
    """ Return the difference between the number of player's 
    potentially reachable moves and that of its opponent
    Note: this function involves breadth-first search, 
    so it comes with higher time cost
    """
    if game.is_winner(player):
        return float('inf')
    if game.is_loser(player):
        return float('-inf')
    
    agent_reachable_pos_total = reachable_postion_counter(game, player)
    opponent = game.get_opponent(player)
    opp_reachable_pos_total = reachable_postion_counter(game, opponent)
    
    return agent_reachable_pos_total - opp_reachable_pos_total

def heuristic_func_3(game, player):
    return max(heuristic_func_1(game, player), heuristic_func_2(game, player))

def heuristic_func_4(game, player):
    board_size = game.width * game.height
    if len(game.get_blank_spaces()) < board_size / 2:
        return heuristic_func_2(game, player)
    else:
        return heuristic_func_1(game, player)

def heuristic_func_5(game, player):
    board_size = game.width * game.height
    if 2 * len(game.get_blank_spaces()) < board_size / 3:
        return heuristic_func_2(game, player)
    else:
        return heuristic_func_1(game, player)
    
def heuristic_func_6(game, player):
    board_size = game.width * game.height
    if len(game.get_blank_spaces()) < board_size / 3:
        return heuristic_func_2(game, player)
    else:
        return heuristic_func_1(game, player)
    
class MyTimeout(Timeout):
    """ This class is used as an exception carrying best_move from iterative deepening search
    """
    def __init__(self, best_move):
        self.best_move = best_move
        
class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)  This parameter should be ignored when iterative = True.

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).  When True, search_depth should
        be ignored and no limit to search depth.

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
        """
        transposition_talbe stores some initial moves from experience
        key : (frozenset(occupied positions), player position)
        value : next move position
        """
        self.transposition_table = {}

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            DEPRECATED -- This argument will be removed in the next release

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        
        def search(game, max_depth = 4):
            """ Do search based on self.iterative and self.method
            """
            if self.iterative:
                depth = 0
                try:
                    while True:
                        _, best_move = getattr(CustomPlayer, self.method)(self, game, depth)
                        depth += 1
                except Timeout:
                    # time out, raise an exception carrying best_move
                    raise MyTimeout(best_move)
            else:
                _, best_move = getattr(CustomPlayer, self.method)(self, game, max_depth)
            return best_move
            
        def transformation_table_key(game):
            """ Return transformation table key in form of 
            (frozenset(occupied positions), player position)
            """
            def get_occupied_positions(game):
                """ Return a frozenset of the occupied positions in the board """
                def to_position(index):
                    """ Convert index to position """
                    return index // game.width, index % game.width
                
                occupied_positions = set()
                for index in range(len(game._board_state) - 3):
                    # add the position to the set if it is occupied
                    if game._board_state[index]:
                        occupied_positions.add(to_position(index))
                        
                return frozenset(occupied_positions)
            
            agent_position = game.get_player_location(self)
            occupied_positions = get_occupied_positions(game)
            
            return occupied_positions, agent_position
            
        def add_to_transformation_table(board_info, move):
            """ Add a bunch of (key, value) pairs to transformation_table
            (key, value)s are derived from (board_info, move)
            by doing some additional work, such as reflection and rotation
            """
            # add (board_info, move)
            self.transposition_table[board_info] = move

            def reflect(pos):
                """ Return the symmetric point of pos relative to center horizontal axis """
                # although we checked if there are legal moves before, alpha-beta search may still return nothing
                # when all legal moves result states out of range [alpha, beta]
                # for those empty move, we don't apply reflection
                if pos == tuple():
                    return pos
                return pos[0], game.height - 1 - pos[1]

            # reflection
            reflected_board_info = (frozenset(reflect(pos) for pos in board_info[0]), reflect(board_info[1]))
            reflected_move = reflect(move)
            self.transposition_table[reflected_board_info] = reflected_move

            if game.width != game.height:
                print("not a square board.")
                return

            def rotate(pos):
                """ Return a point resulting from 90-degree clockwise rotation of pos """
                # although we checked if there are legal moves before, alpha-beta search may still return nothing
                # when all legal moves result states out of range [alpha, beta]
                # for those empty move, we don't apply rotation
                if pos == tuple():
                    return pos
                return pos[1], game.width - 1 - pos[0]

            # rotation
            # clockwise rotate 90 degrees at each iteration
            rotated_board_info = board_info
            rotated_move = move
            for _ in range(3):
                rotated_board_info = (frozenset(rotate(pos) for pos in rotated_board_info[0]), rotate(rotated_board_info[1]))
                rotated_move = rotate(rotated_move)
                self.transposition_table[rotated_board_info] = rotated_move
                rotated_reflected_board_info = (frozenset(reflect(pos) for pos in rotated_board_info[0]), reflect(rotated_board_info[1]))
                rotated_reflected_move = reflect(rotated_move)
                self.transposition_table[rotated_reflected_board_info] = rotated_reflected_move

        def agent_first_move():
            """ Agent picks its first move """
            center = (game.width // 2, game.height // 2)
            # move to the center if possible
            if game.move_is_legal(center):
                return center
            else:
                # move to a position unreachable from the center
                legal_moves_from_center = game.get_legal_moves(game.get_opponent(self))
                # remove center-reachable moves from legal_moves
                for move in legal_moves_from_center:
                    legal_moves.remove(move)
                return random.choice(legal_moves)
            
        def table_lookup(board_info):
            """ check on transposition table fot board_info
            if it exists in table return the next move
            if not, compute the next move, store it into the
            table, and return it
            """
            if board_info in self.transposition_table:
                return self.transposition_table[board_info]
            else:
                best_move = search(game)
                # update transposition table
                add_to_transformation_table(board_info, best_move)
                return best_move

        self.time_left = time_left

        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves
        
        legal_moves = game.get_legal_moves()
        # no legal move, return (-1, -1)
        if len(legal_moves) == 0:
            return (-1, -1)

        # agent's first move
        if len(game.get_blank_spaces()) > game.width * game.height - 2:
            self.move = agent_first_move()
            return self.move
        
        try:
            # The try/except block will automatically catch the exception 
            # raised by the search method when the timer gets close to expiring
            
            best_move = None
            if len(game.get_blank_spaces()) > game.width * game.height - 6 or len(game.get_blank_spaces()) <= 10:
                # we only save the first 6 plies
                #  and the last 10 plies <== it will unexpected terminate if recording the last 10 plies
                board_info = transformation_table_key(game)
                return table_lookup(board_info)
            else:
                # general strategy for other moves
                best_move = search(game)
                return best_move
            
        except MyTimeout as e:
            best_move = e.best_move
            # record best_move to table if it's the first 6 plies
            # or the last 10 plies <== it will unexpected terminate if recording the last 10 plies
            if len(game.get_blank_spaces()) > game.width * game.height - 6 or len(game.get_blank_spaces()) <= 10:
                add_to_transformation_table(board_info, best_move)
            return best_move
        except Timeout:
            # this shouldn't happen.
            print("Unexpectedly reach here", best_move)
            return best_move

        # Return the best move from the last completed search iteration

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        is_end, utility_value = self.check_end(game, depth)
        if is_end:
            return utility_value, (-1, -1)
        
        best_move = tuple()
        if maximizing_player:
            # maximize the utility value
            utility_value = float('-inf')
            for move in game.get_legal_moves():
                forecasting_board = game.forecast_move(move)
                successor_value, _ = self.minimax(forecasting_board, depth-1, maximizing_player=False)
                if utility_value < successor_value:
                    utility_value = successor_value
                    best_move = move
        else:
            # minimize the utility value
            utility_value = float('inf')
            for move in game.get_legal_moves():
                forecasting_board = game.forecast_move(move)
                successor_value, _ = self.minimax(forecasting_board, depth-1)
                if utility_value > successor_value:
                    utility_value = successor_value
                    best_move = move
        return utility_value, best_move

    #maximizing_player does not matter if min_value and max_value are implemented separately
    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """

        def min_value(game, depth, alpha, beta):
            """ Return a minimum utility value and the best move
            Update beta if the utility value is in [alpha, beta)
            During search, if any of utility values from its successors is less than alpha
            Prune the rest successors and return this value
            """
            is_end, utility_value = self.check_end(game, depth)
            if is_end:
                return utility_value, (-1, -1)
            
            utility_value = float('inf')
            best_move = tuple()
            
            for move in game.get_legal_moves():
                forecasting_board = game.forecast_move(move)
                successor_value, _ = max_value(forecasting_board, depth-1, alpha, beta)
                if utility_value > successor_value:
                    utility_value = successor_value
                    best_move = move
                # heuristic value is not greater than alpha, prune the rest successors
                if utility_value <= alpha:
                    return utility_value, best_move
                beta = min(beta, utility_value)
                
            return utility_value, best_move
            
        def max_value(game, depth, alpha, beta):
            """ Return a max utility value and the best move
            Update alpha if the utility value is in (alpha, beta]
            During search, if any of utility values from its successors is larger than beta
            Prune the rest successors and return this value
            """
            is_end, utility_value = self.check_end(game, depth)
            if is_end:
                return utility_value, (-1, -1)
            
            utility_value = float('-inf')
            best_move = tuple()
            
            for move in game.get_legal_moves():
                forecasting_board = game.forecast_move(move)
                successor_value, _ = min_value(forecasting_board, depth-1, alpha, beta)
                if utility_value < successor_value:
                    utility_value = successor_value
                    best_move = move
                # utility value is not less than beta, prune the rest successors
                if utility_value >= beta:
                    return utility_value, best_move
                alpha = max(alpha, utility_value)
                
            return utility_value, best_move
        
        return max_value(game, depth, alpha, beta)
        
    def check_end(self, game, depth):
            """ Return (True, utility value) if game hits the end or search tree reaches the depth
            (False, 0), otherwise
            if time's out, raise Timeout()
            """
            if self.time_left() < self.TIMER_THRESHOLD:
                raise Timeout()
            # calculate the heuristic value and return 
            # if game hits the end or search tree reaches the maximum depth
            if game.utility(self) or depth == 0:
                return True, self.score(game, self)
            return False, 0

