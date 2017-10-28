
:- include('assignment6').
:- begin_tests(assignment6).

test(duplicate_entries) :-
	duplicate_entries([a,b,a,c,d]),
	duplicate_entries([[a,b],b,c,[a,b]]).
test(duplicate_entries, [fail]):-
	duplicate_entries([a,b,[a],c,d]).

test(splice):-
	splice([a,b,c],x,0,[x,a,b,c]),
	splice([a,b,c],x,2,[a,b,x,c]).

test(splice, [fail]):-
	splice([a, b, c],x,5,_).

test(remove_dups):-
	remove_dups([a,b,[a],c,d], [a,b,[a],c,d]),
	remove_dups([[a,b],b,c,[a,b],[a,b]], [[a,b],b,c]).

test(find_zero):-
	find_zero([a,[b,0],c]).
test(find_zero,[fail]):-
	find_zero([a,[b,c],d]).

test(flatten2):-
	flatten2([1,2,[[3,4],5]], [1,2,3,4,5]),
	flatten2([a,[b,c],[[[d],e,f]]], [a,b,c,d,e,f]).

test(insert):-
	insert(a,[1,2,3],[1,a,2,a,3,a]),
	insert(5,[a,[b,[c],d]],[a,5,[b,5,[c,5],d,5]]).

test(leaves):-
	leaves(tree(8, tree(5, tree(2,nil,nil), tree(7,nil,nil)),tree(9, nil, tree(15, tree(11, nil, nil), nil))), 3).

test(increase):-
	%% Simulamos inputs
	T = tree(8,tree(5,tree(2,nil,nil),tree(7,nil,nil)),tree(9, nil, tree(15, tree(11, nil, nil), nil))),
	A = tree(8,tree(5,tree(6,nil,nil),tree(7,nil,nil)),tree(9, nil, tree(15, tree(11, nil, nil), nil))),
	increase(T,A,2,4).

test(increase,[fail]):-
	T = tree(8,tree(5,tree(2,nil,nil),tree(7,nil,nil)),tree(9, nil, tree(15, tree(11, nil, nil), nil))),
	hasE(T,3).
:- end_tests(assignment6).