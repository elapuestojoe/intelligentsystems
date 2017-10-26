in_list(_, []):-
	false.
in_list(X, [X | _]):-
	true,!. 								%% Red cut
in_list(X, [_ | T]):-
	in_list(X, T).

myAppend([H|T], H, T).

%% 4:- duplicate_entries LISTO
duplicate_entries([]):-
	false.
duplicate_entries([H | T]):-
	in_list(H, T), \+ duplicate_entries(T).	 %%Green cut

%% 5:- splice LISTO
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

%% Cuasi funciona
%% 6.5
remove_dups([],R):-
	R = [],!.	
remove_dups([H|T], R):-
	not(in_list(H,T)),
	remove_dups(T, R2),
	R = [H|R2],!.
remove_dups([H|T], R):-
	in_list(H,T),
	remove_dups(T,R),!.
	%% Duplicados se desordenan, resolver

%% 7.- Find Zero funciona!
find_zero([]):-
	false,!.
find_zero([0|_]):-
	true,!.
find_zero([H | T]):-
	find_zero(H); find_zero(T),!.

%% 8.- flatten
flatten2([],R):-
	R = [],!.
flatten2([H|[]],R):-
	flatten2(H,R).
flatten2([H|T],R):-
	flatten2(H,R2),
	flatten2(T,R3),
	R = [R2|R3],!.
flatten2(A,R):-
	number(A),
	R = A.



%% 9:- insert listo Funciona
numberOrAtomic(A):-
	number(A);atomic(A).
insert(_,[],R):-
	R = [],!.
insert(A,[H|T],[H,A|R2]):-
	numberOrAtomic(H),
	insert(A,T,R2),!.
insert(A,[H|T],[R2|R3]):-
	not(numberOrAtomic(H)),
	insert(A,H,R2),
	insert(A,T,R3),!.

isTree(tree(_,_,_)).

%% Increase
%% Esto recursivamente aumenta TODOS los elementos del árbol, haciendo que un cut no sea muy eficiente...
%% Quizá lo que busca el profesor es que solo sea el primer elemento? en ese caso un cut tendría sentido...
%% Urge legislar

%% Funciona
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
increase(nil,nil,_,_).

hasE(tree(E,_,_),E):-
	true,!.
hasE(tree(_,T1,T2),E):-
	hasE(T1,E); hasE(T2,E),!.

getEI(E,I,T):-
	write('Element? '),
	read(E),
	hasE(T,E),
	write('Increase? '),
	read(I).

%% 10 LEAVES (Funciona)
leaves(tree(_, nil,nil), 1).
leaves(nil, 0).
leaves(tree(_, T1, T2), H):-
	leaves(T1, H1),
	leaves(T2, H2),
	H is H1+H2,!.






