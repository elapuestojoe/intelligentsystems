%% Auxiliary functions:

%% Our version of member(H,T)
in_list(_, []):-
	false.
in_list(X, [X | _]):-
	true,!. 								%% Red cut
in_list(X, [_ | T]):-
	in_list(X, T).

%% Appends H,T 
myAppend([H|T], H, T).

%% Eliminates first element from list
eliminate(_, [], R):-
    R = [], !.
eliminate(H, [H|T], R):-
    eliminate(H, T, R),
    !.
eliminate(X, [H|T], [H|Y]):-
    eliminate(X, T, Y).

%% True if A is either number or atomic
numberOrAtomic(A):-
	number(A);atomic(A).

%% True if parameter is a tree(_,_,_)
isTree(tree(_,_,_)).

%% Checks if a tree has an element
hasE(tree(E,_,_),E):-
	true,!.
hasE(tree(_,T1,T2),E):-
	hasE(T1,E); hasE(T2,E),!.

%% Function to get E,I as input
getEI(E,I,T):-
	write('Element? '),
	read(E),
	hasE(T,E),
	write('Increase? '),
	read(I).

%% 4:- duplicate_entries
duplicate_entries([]):-
	false.
duplicate_entries([H | T]):-
	in_list(H, T), \+ duplicate_entries(T).	 %%Green cut

%% 5:- splice
splice([], X, 0,R):-
	R = [X],!.
splice(L, X, 0, R):-
	myAppend(R,X,L),!.
splice([H|T], X, N, R):-
	N2 is N-1,
	R2 = H,
	splice(T,X,N2,R3),
	R = [R2|R3].
splice([], _, N, _):-
	N > 0,
	false,!.

%% 6 remove_dups
remove_dups([], Z):-
    Z = [], !.
remove_dups([H|T], R):-
    in_list(H, T),
    eliminate(H, T, R2),
    remove_dups([H|R2], R),
    !.
remove_dups([H|T1], [H|T2]):-
    remove_dups(T1, T2).

%% 7 find_zero
find_zero([]):-
	false,!.
find_zero([0|_]):-
	true,!.
find_zero([H | T]):-
	find_zero(H); find_zero(T),!.

%% 8.- flatten2 (used 2 to avoid conflicting with native flatten method)
flatten2([],R):-
    R = [], !.
flatten2([H|T], R):-
    is_list(H),
    flatten(H, R2),
    flatten(T, R3),
    append(R2, R3, R),
    !.
flatten2([H|T1], [H|T2]):-
    flatten(T1, T2).

%% 9:- insert
insert(_,[],R):-
	R = [],!.
insert(A,[H|T],[H,A|R2]):-
	numberOrAtomic(H),
	insert(A,T,R2),!.
insert(A,[H|T],[R2|R3]):-
	not(numberOrAtomic(H)),
	insert(A,H,R2),
	insert(A,T,R3),!.

%% 10 LEAVES (Funciona)
leaves(tree(_, nil,nil), 1).
leaves(nil, 0).
leaves(tree(_, T1, T2), H):-
	leaves(T1, H1),
	leaves(T2, H2),
	H is H1+H2,!.

%% 11: increase
increase(T,A):-
	isTree(T),
	getEI(E,I,T),
	increase(T,A,E,I).
increase(tree(E,T1,T2),A,E,I):-
	I2 is I+E,
	increase(T1,T1_2,E,I),
	increase(T2,T2_2,E,I),
	A = tree(I2,T1_2,T2_2),!.
increase(tree(R,T1,T2),A,E,I):-
	not(R==E),
	increase(T1,T1_2,E,I),
	increase(T2,T2_2,E,I),
	A = tree(R,T1_2,T2_2),!.
increase(T,T,_,_):-
	not(isTree(T)).
increase(nil,false,_,_).