import random
import copy

from games import (GameState, Game, infinity, query_player, random_player)

# ______________________________________________________________________________
# Alpha-Beta Minimax Search

def alphabeta_search(state, game, d=4, cutoff_test=None, eval_fn=None):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""

    player = game.to_move(state)

    # Functions used by alphabeta
    def max_value(state, alpha, beta, depth):
        #print('max_value')
        if cutoff_test(state, depth):
            v = eval_fn(state, player) # needs the max player
            #print('max:',v)
            return v
        v = -infinity
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a),
                                 alpha, beta, depth + 1))
            if v >= beta:
                #print('max:',v)
                return v
            alpha = max(alpha, v)
        #print('max:',v)
        return v

    def min_value(state, alpha, beta, depth):
        #print('min_value')
        if cutoff_test(state, depth):
            v = eval_fn(state, player) # needs the max player
            #print('min:',v)
            return v
        v = infinity
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a),
                                 alpha, beta, depth + 1))
            if v <= alpha:
                #print('min:',v)
                return v
            beta = min(beta, v)
        #print('min:',v)
        return v

    # Body of alphabeta_search starts here:
    # The default test cuts off at depth d or at a terminal state
    cutoff_test = (cutoff_test or
                   (lambda state, depth: depth == d or game.terminal_test(state)))
    eval_fn = eval_fn or (lambda state: game.utility(state, player))
    best_score = -infinity
    beta = infinity
    best_action = None
    for a in game.actions(state):
        v = min_value(game.result(state, a), best_score, beta, 1)
        if v > best_score:
            best_score = v
            best_action = a
    return best_action

#_______________________________________________________________________________
# Blobs Game functions

class BlobsBoard(object):
    """Blobs game class to generate and manipulate boards"""
    def __init__(self):
        "creates a new random 6x6 board with 12 red and 12 green Blobs"
        # board limits
        self.left_border = 0
        self.right_border = 7
        self.top_border = 0
        self.bottom_border = 7
        self.red_blobs = None
        self.green_blobs = None
        self.new_random_board()

    def new_random_board(self):
        "generate 12 random positions for each Blob color on the board"
        positions = [(row,col) for row in range(1, 7) for col in range(1, 7)]
        random.shuffle(positions)
        self.red_blobs = set(positions[0:12])
        self.green_blobs = set(positions[12:24])

    def display(self):
        "displays the board"
        for row in range(1, 7):
            for col in range(1, 7):
                position = (row, col)
                if row <= self.top_border or row >= self.bottom_border or \
                   col <= self.left_border or col >= self.right_border:
                    print('o', end=' ')
                elif position in self.red_blobs: print('R', end=' ')
                elif position in self.green_blobs: print('G', end=' ')
                else: print('.', end=' ')
            print()

    def update_borders(self):
        "update the positions of the board borders"
        # update left border: moves right on left empty columns
        # update right border: moves left on right empty columns
        # update top border: moves down on top empty rows
        # update bottom border: moves up on bottom empty rows
        raise NotImplementedError
    
    def move(self, color, direction):
        "moves all the blobs of a color in a direction"
        # move blobs of the specified color eliminating those that fall out of the board
        # eliminate corresponding blobs of the opponent
        # update borders
        raise NotImplementedError

    # other methods???
        
class Blobs(Game):
    """Play Blobs on an 6 x 6 board, with Max (first player) playing the red
    Blobs with marker 'R'.
    A state has the player to move, a cached utility, a list of moves in
    the form of the four directions (left 'L', right 'R', up 'U', and down 'D'),
    and a board, in the form of a BlobsBoard object.
    Marker is 'R' for the Red Player and 'G' for the Green Player. An empty
    position appear as '.' in the display and a 'o' represents an out of the
    board position."""

    def __init__(self, board = None):
        self.initial = GameState(to_move='R', utility=0,
                                 board=BlobsBoard(), moves=['L','R','U','D'])

    def actions(self, state):
        "Legal moves are always all the four original directions."
        raise NotImplementedError

    def result(self, state, move):
        "returns the resulting state of applying a move to the current state"
        raise NotImplementedError

    def utility(self, state, player):
        "Return the value to player; 1 for win, -1 for loss, 0 otherwise."
        raise NotImplementedError

    def terminal_test(self, state):
        "A state is terminal if some player already lost the game."
        raise NotImplementedError

    def display(self, state):
        "Displays the current state"
        raise NotImplementedError

# ______________________________________________________________________________
# evaluation function of a team

def eval_fn(state, player):
    """returns a positive value is the given player (red or green) is supposed
    to win the game or negative if the player is supposed to lose"""
    # raise NotImplemented
    return 0

# ______________________________________________________________________________
# Players for Games

def team_player(depth, eval_fn):
    """A team player that decides after depth plies and evaluates
    the states using the eval_fn function of the team"""
    return (lambda game, state:
            alphabeta_search(state, game, d=depth, eval_fn=eval_fn))

def EVALFN4(self, state):
    # if(state.utility < 0):
    #     return state.utility
    up = 0
    down = 0
    left = 0
    right = 0

    adjacent = 0
    for position in state.board.red_blobs:
        x = position[0]
        y = position[1]

        if((x+1,y) in state.board.green_blobs):
            right+=1
            adjacent+=1
        if((x-1,y) in state.board.green_blobs):
            left+=1
            adjacent+=1
        if((x,y+1) in state.board.green_blobs):
            up+=1
            adjacent+=1
        if((x,y-1) in state.board.green_blobs):
            down+=1
            adjacent+=1

    # maxAdjacent = max(up,down,left,right)
    # minAdjacent = min(up,down,left,right)
    if(state.to_move == "R"):
        return adjacent
    else:
        return -adjacent

def display_move(player, direction):
    "Display a player's move"
    if player == 'R':
        print('Red', end=' ')
    else:
        print('Green', end=' ')
    print('Blobs player moves', end=' ')
    if direction == 'U':
        print('UP')
    elif direction == 'D':
        print('Down')
    elif direction == 'L':
        print('Left')
    elif direction == 'R':
        print('Right')
    else:
        print('Wrong')

def play_game(game, *players):
    """Plays a 2-player Blobs game."""
    state = game.initial
    print('INITIAL BOARD')
    plays = 0
    while plays < 30:  # Maximum number of plays to finish a game
        plays += 1
        print('PLAY #', plays)
        for player in players:
            game.display(state)
            move = player(game, state)
            display_move(state.to_move, move)
            state = game.result(state, move)
            if game.terminal_test(state):
                game.display(state)
                utility = game.utility(state, game.to_move(game.initial))
                if utility > 0:
                    print('Red player wins!!')
                elif utility < 0:
                    print('Green player wins!!')
                else:
                    print('Tie: Nobody wins!!')
                return utility
    print('=> Reach maximum number of plays')
    utility = game.utility(state, game.to_move(game.initial))
    if utility > 0:
        print('Red player wins!!')
    elif utility < 0:
        print('Green player wins!!')
    else:
        print('Tie: Nobody wins!!')
    return utility

game = Blobs()
player1 = team_player(4, eval_fn)
player2 = team_player(8, EVALFN4)

play_game(game, player1, player2)