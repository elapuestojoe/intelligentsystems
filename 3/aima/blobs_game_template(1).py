import random

from games import (GameState, Game, query_player, random_player, 
                    alphabeta_player, play_game,
                    alphabeta_full_search, alphabeta_search)

#_______________________________________________________________________________
# Auxiliary functions

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

        # for row in range(1,7):
        #     for col in range(1,7):
        #         position = (row,col)
        #         if(position in )


        # if(color == "R"):
        #     for position in self.red_blobs:
        #         listP = list(position)
        #         if(direction == "R"):
        #             listP[0] += 1
        #             tupleP= tuple(listP)
        #             if tupleP in self.green_blobs:
        #                 self.green_blobs.remove(tupleP)
        #                 self.red_blobs.remove(position)
        #                 self.red_blobs.add(tupleP)
        # elif(color == "G"):
        #     print("G")

        # raise NotImplementedError

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

    def __init__(self):
        self.initial = GameState(to_move='R', utility=0,
                                 board=BlobsBoard(), moves=['L','R','U','D'])
    def actions(self, state):
        "Legal moves are always all the four original directions."
        return self.initial.moves

    def result(self, state, move):
        "returns the result of applying a move to a state"
        raise NotImplementedError

    def utility(self, state, player):
        "Return the value to player; 1 for win, -1 for loss, 0 otherwise."
        raise NotImplementedError

    def terminal_test(self, state):
        "A state is terminal if it is won or there are no empty squares."
        raise NotImplementedError

    def display(self, state):
        "Displays the current state"
        print("DISPLAY")
        raise NotImplementedError

## YOU ALSO NEED TO CREATE AN EVAL_FN AND A PLAYER FOR YOUR GAME THAT USE
## ALPHABETA_SEARCH INSTEAD OF ALPHABETA_FULL_SEARCH.
## YOU DO NOT NEED A CUTOFF_TEST BECAUSE I WILL USE DEPTHS FOR CUTTING THE
## LOOK-AHEAD SEARCH.

b1 = Blobs()
b1.initial.board.display()
b1.initial.board.move("R", "R")
print("-----")
b1.initial.board.display()
