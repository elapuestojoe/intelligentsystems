import random
import copy
from games import (GameState, Game, query_player, random_player, 
                    alphabeta_player, play_game,
                    alphabeta_full_search, alphabeta_search, TicTacToe)

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

        # Origin = (0,0)

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

            # if(len(self.red_blobs) == 0 or len(self.green_blobs) == 0):
            #     break
    
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
        
class Blobs(Game):
    """Play Blobs on an 6 x 6 board, with Max (first player) playing the red
    Blobs with marker 'R'.
    A state has the player to move, a cached utility, a list of moves in
    the form of the four directions (left 'L', right 'R', up 'U', and down 'D'),
    and a board, in the form of a BlobsBoard object.
    Marker is 'R' for the Red Player and 'G' for the Green Player. An empty
    position appear as '.' in the display and a 'o' represents an out of the
    board position."""

    moves = None
    def __init__(self):
        self.initial = GameState(to_move='R', utility=0,
                                 board=BlobsBoard(), moves=['L','D','R','U'])
        self.currentState = self.initial
        self.moves = self.initial.moves

    def actions(self, state):
        "Legal moves are always all the four original directions."
        return state.moves
        # random.shuffle(self.moves)
        # return self.moves

    def result(self, state, move):
        "returns the result of applying a move to a state"
        # Calculates who is the next player to move
        to_move = state.to_move

        if(to_move == "R"):
            to_move = "G"
        else:
            to_move = "R"

        # Copies the current state
        newBoard = copy.copy(state.board)

        # Applies the move to the copy
        newBoard.move(to_move, move)

        # Returns the copy (THE ORIGINAL STATE IS NOT AFFECTED)
        return GameState(to_move = to_move,
                        utility = self.compute_utility(newBoard, move, state.to_move), #Calculates the value of the move by the player who made the move
                        board = newBoard,
                        moves = self.moves)

    def utility(self, state, player): 
        "Return the value to player; 1 for win, -1 for loss, 0 otherwise."
        return state.utility #if player == "R" else -state.utility

    def EVAL_FN3(self,state):
        if(state.to_move == "G"):
            # return len(state.board.red_blobs)
            return (len(state.board.green_blobs) - len(state.board.red_blobs))
        else:
            # return len(state.board.green_blobs)
            return (len(state.board.red_blobs) - len(state.board.green_blobs))

    def EVAL_FN2(self, state):
        if(state.utility < 0):
            return state.utility
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
        print("ADJACENT", adjacent)
        if(state.to_move == "R"):
            return adjacent
        else:
            return -adjacent

    def EVAL_FN1(self, state):
        print("USELESS")
        return 0
        # Tercer intento:
        # if(len(state.board.green_blobs) == 0):
        #     if(state.to_move == "R"):
        #         return 1000
        #     else:
        #         return -1000
        # if(len(state.board.red_blobs) == 0):
        #     if(state.to_move == "G"):
        #         return 1000
        #     else:
        #         return -1000
        
        # diff = len(state.board.green_blobs) - len(state.board.red_blobs)
        # if(state.to_move == "G"):
        #     return diff
        # else:
        #     return -diff

        # CUARTO INTENTO
        # player = state.to_move
        # pieces = 0
        # opponentPieces = 0

        # pieces = len(state.board.red_blobs)
        # opponentPieces = len(state.board.green_blobs)

        # if(pieces == 0): return -1
        # if(opponentPieces == 0): return 1
        # xSum = 0
        # ySum = 0
        # for piece in state.board.red_blobs:
        #     xSum += piece[0]
        #     ySum += piece[1]

        # xSum /= pieces
        # ySum /= pieces

        # xSum2 = 0
        # ySum2 = 0
        # for piece in state.board.green_blobs:
        #     xSum2 +=piece[0]
        #     ySum2 +=piece[1]

        # xSum2 /= opponentPieces
        # ySum2 /= opponentPieces

        # if(xSum - xSum2 == 0 or ySum - ySum2 == 0): return 0
        # avgX = xSum / abs(xSum - xSum2)
        # avgY = ySum / abs(ySum - ySum2)


        # if(player == "R"):
        #     return (avgX + avgY) / 2
        # else:
        #     return -10

        # if(player == "G"):
        #     pieces = len(state.board.green_blobs)
        #     opponentPieces = len(state.board.red_blobs)

        #     if(pieces == 0): return -1
        #     if(opponentPieces == 0): return 1
        #     xSum = 0
        #     ySum = 0
        #     for piece in state.board.green_blobs:
        #         xSum += piece[0]
        #         ySum += piece[1]

        #     xSum /= pieces
        #     ySum /= pieces

        #     xSum2 = 0
        #     ySum2 = 0
        #     for piece in state.board.red_blobs:
        #         xSum2 +=piece[0]
        #         ySum2 +=piece[1]

        #     xSum2 /= opponentPieces
        #     ySum2 /= opponentPieces

        #     if(xSum - xSum2 == 0 or ySum - ySum2 == 0): return 0

        #     avgX = xSum / abs(xSum - xSum2)
        #     avgY = ySum / abs(ySum - ySum2)

        #     return (avgX + avgY) / 2



    def terminal_test(self, state):
        "A state is terminal if it is won or there are no empty squares."

        # print("GREEN", len(state.board.green_blobs))
        # print("REED", len(state.board.red_blobs))
        f= state.utility != 0 or len(state.board.green_blobs) == 0 or len(state.board.red_blobs) == 0 or \
            state.board.left_border >= state.board.right_border or state.board.bottom_border >= state.board.top_border

        # print("F", f)
        return f
        # return(self.compute_utility(state.board, None, "R") != 0)


    def display(self, state):
        "Displays the current state"
        print("to_move", state.to_move)
        state.board.display()

    def to_move(self, state):
        return state.to_move

    def compute_utility(self, board, move, player):
        v = 0
        if(len(board.green_blobs) == 0):
            if(player == "R"):
                v = 1
            else:
                v = -1

        if(len(board.red_blobs) == 0):
            if(player == "G"):
                v = 1
            else:
                v = -1
        return v 

    def move(self, move):
        self.currentState = self.result(self.currentState, move)


## YOU ALSO NEED TO CREATE AN EVAL_FN AND A PLAYER FOR YOUR GAME THAT USE
## ALPHABETA_SEARCH INSTEAD OF ALPHABETA_FULL_SEARCH.
## YOU DO NOT NEED A CUTOFF_TEST BECAUSE I WILL USE DEPTHS FOR CUTTING THE
## LOOK-AHEAD SEARCH.

# def alphabeta_search(state, game, d=4, cutoff_test=None, eval_fn=None):
def AlphaBetaImprovedPlayer(game, state):
    # state.moves = random.shuffle(state.moves)
    return alphabeta_search(state, game, eval_fn = game.EVAL_FN1)

def AlphaBeta2(game,state):
    return alphabeta_search(state, game, eval_fn = game.EVAL_FN2)
def AlphaBeta3(game,state):
    return alphabeta_search(state, game, eval_fn = game.EVAL_FN3)

print("GAME")
b4 = Blobs()
print("INITIAL")
b4.display(b4.currentState)
print("------------")
# play_game(b4,alphabeta_player, alphabeta_player)
# play_game(b4, AlphaBetaImprovedPlayer, random_player)
# play_game(b4, alphabeta_player, alphabeta_player)
# play_game(b4, random_player, alphabeta_player)
# play_game(b4, AlphaBetaImprovedPlayer, AlphaBetaImprovedPlayer)
# play_game(b4, AlphaBetaImprovedPlayer, alphabeta_player)

# play_game(b4, AlphaBeta2, random_player)
# play_game(b4, alphabeta_player, AlphaBeta2)
# play_game(b4, AlphaBeta2, alphabeta_player)
# play_game(b4, AlphaBeta3, AlphaBeta2)
play_game(b4,AlphaBeta2, AlphaBeta3)