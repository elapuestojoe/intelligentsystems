
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

test(find_zero):-
	find_zero([a,[b,0],c]).
test(find_zero,[fail]):-
	find_zero([a,[b,c],d]).

test(leaves):-
	leaves(tree(8, tree(5, tree(2,nil,nil), tree(7,nil,nil)),tree(9, nil, tree(15, tree(11, nil, nil), nil))), 3).

test(insert):-
	insert(a,[1,2,3],[1,a,2,a,3,a]),
	insert(5,[a,[b,[c],d]],[a,5,[b,5,[c,5],d,5]]).

:- end_tests(assignment6).