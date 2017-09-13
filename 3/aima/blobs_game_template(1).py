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
        self.top_border = 7
        self.bottom_border = 0
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
        for col in range(6, 0, -1):
            for row in range(1, 7):
                position = (row, col)
                if row <= self.left_border or row >= self.right_border or \
                   col <= self.bottom_border or col >= self.top_border:
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

        bottom = True
        top = True
        left = True
        right = True

        # para casos especiales (en random a veces un movimiento permite varias reducciones)

        while(bottom or top or left or right):
            for x in range(self.left_border + 1, self.right_border):

                b = self.bottom_border + 1
                t = self.top_border - 1
                if((x,b) in self.red_blobs or (x,b) in self.green_blobs):
                    bottom = False
                if((x,t) in self.red_blobs or (x,t) in self.green_blobs):
                    top = False



            for y in range(self.bottom_border + 1, self.top_border):

                l = self.left_border + 1
                r = self.right_border -1
                if((l,y) in self.red_blobs or (l,y) in self.green_blobs):
                    left = False
                if((r,y) in self.red_blobs or (r,y) in self.green_blobs):
                    right = False

            if(bottom):
                self.bottom_border+=1
            if(top):
                self.top_border-=1
            if(left):
                self.left_border+=1
            if(right):
                self.right_border-=1
    
    def move(self, color, direction):
        "moves all the blobs of a color in a direction"
        # move blobs of the specified color eliminating those that fall out of the board

        piecesToMove = []
        opponentPieces = []
        if(color == "R"):
            piecesToMove = self.red_blobs
            opponentPieces = self.green_blobs
        elif(color == "G"):
            piecesToMove = self.green_blobs
            opponentPieces = self.red_blobs

        newPositions = []
        for position in piecesToMove:
            x = position[0]
            y = position[1]

            if(direction == "R"):
                x+=1
            elif(direction == "L"):
                x-=1
            elif(direction == "U"):
                y+=1
            elif(direction == "D"):
                y-=1

            newPosition = (x,y)

            if (x > self.left_border and x < self.right_border and y > self.bottom_border and y < self.top_border):
                newPositions.append(newPosition)

        newPositions = set(newPositions)

        # eliminate corresponding blobs of the opponent
        opponentPieces = opponentPieces.difference(newPositions)

        if(color == "R"):
            self.red_blobs = set(newPositions)
            self.green_blobs = set(opponentPieces)
        elif(color == "G"):
            self.green_blobs = set(newPositions)
            self.red_blobs = set(opponentPieces)

        self.update_borders()

        return self

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

    states = []
    def __init__(self):
        self.initial = GameState(to_move='R', utility=0,
                                 board=BlobsBoard(), moves=['L','R','U','D'])
        self.states.append(self.initial)
    def actions(self, state):
        "Legal moves are always all the four original directions."
        return self.states[-1].moves

    def result(self, move):
        "returns the result of applying a move to a state"
        state = self.states[-1]
        to_move = state.to_move

        if(to_move == "R"):
            to_move = "G"
        else:
            to_move = "R"

        newBoard = state.board.move(to_move, move)
        self.states.append(GameState(to_move=to_move,
                        utility = self.utility(newBoard),
                        board = newBoard,
                        moves = self.actions(newBoard)))

    def utility(self, state): 
        "Return the value to player; 1 for win, -1 for loss, 0 otherwise."
        if(state.red_blobs == 0):
            if(player == "R"):
                return -1
            else:
                return 1

        if(state.green_blobs == 0):
            if(player == "G"):
                return -1
            else:
                return 1

        return 0

    def terminal_test(self):
        "A state is terminal if it is won or there are no empty squares."
        board = self.states[-1].board
        if(len(board.red_blobs) == 0 or len(board.green_blobs) == 0):
            return True

        # NOT SURE IF THIS IS NEEDED SALU2 A TO2
        emptySpaces = False
        for x in range(board.left_border, board.right_border):
            for y in range(board.bottom_border, board.top_border):
                space = (x,y)
                if(space not in board.red_blobs and space not in board.green_blobs):
                    emptySpaces = True
        return not emptySpaces

    def display(self):
        "Displays the current state"
        state = self.states[-1]
        print("to_move", state.to_move)
        state.board.display()


## YOU ALSO NEED TO CREATE AN EVAL_FN AND A PLAYER FOR YOUR GAME THAT USE
## ALPHABETA_SEARCH INSTEAD OF ALPHABETA_FULL_SEARCH.
## YOU DO NOT NEED A CUTOFF_TEST BECAUSE I WILL USE DEPTHS FOR CUTTING THE
## LOOK-AHEAD SEARCH.

b1 = Blobs()
# b1.initial.board.display()
# b1.initial.board.move("R", "R")
# print("-----")
# b1.initial.board.display()

while not b1.terminal_test():
    # move = str(input())
    # if(move == "r"):
    #     print("R")
    #     b1.initial.board.move("R", "R")
    #     print(b1.terminal_test(b1.initial))
    # if(move == "l"):
    #     b1.initial.board.move("R", "L")
    #     print(b1.terminal_test(b1.initial))
    # if(move == "d"):
    #     b1.initial.board.move("R", "D")
    #     print(b1.terminal_test(b1.initial))
    # if(move == "u"):
    #     b1.initial.board.move("R", "U")
    #     print(b1.terminal_test(b1.initial))
    # if(move == "di"):
    #     b1.initial.board.display()
    # if(move == "e"):
    #     break


    # Random player para pruebas
    print("-------------------------")
    b1.result(random_player(b1, b1.states[-1]))
    b1.display()
    print("-------------------------")
    b1.result(random_player(b1, b1.states[-1]))
    b1.display()

print("WIN-------------------------")
b1.initial.board.display()
