leaves(tree(_, nil,nil), H):-
	H is 1.

leaves(nil, H):-
	H is 0.
leaves(tree(_, T1, T2), H):-
	leaves(T1, H1),
	leaves(T2, H2),
	H is H1+H2.