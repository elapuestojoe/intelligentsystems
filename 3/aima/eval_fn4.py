from games import(alphabeta_search)
def eval_fn4(state):
    "Evaluates a state acording to adjacent pieces and current player"
    adjacent = 0
    s = []
    e = []
    if(state.to_move=="R"):
        s = state.board.red_blobs
        e = state.board.green_blobs
    else:
        e = state.board.red_blobs
        s = state.board.green_blobs
    for position in s:
        x = position[0]
        y = position[1]

        if((x+1,y) in e):
            adjacent+=1
        if((x-1,y) in e):
            adjacent+=1
        if((x,y+1) in e):
            adjacent+=1
        if((x,y-1) in e):
            adjacent+=1
    return adjacent + len(s) - len(e)
def player4(game,state):
	return alphabeta_search(state, game, eval_fn = eval_fn4)
