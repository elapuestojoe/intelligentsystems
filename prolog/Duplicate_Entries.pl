in_list(_, []):-
	false.
in_list(X, [X | _]):-
	true,!. 								%% Red cut
in_list(X, [_ | T]):-
	in_list(X, T).

duplicate_entries([]):-
	false.
duplicate_entries([H | T]):-
	in_list(H, T), \+ duplicate_entries(T).	 %%Green cut

splice(L, X, 0, R):-
	R = [X|L],!.
splice([H|T], X, N, R):-
	N2 is N-1,
	splice(T, [H,X],N2,R).
	%% Falta corregir algo pero no c q es MORRO LOCO
splice([], _, N, _):-
	N > 0,
	false,!.

%% TODO ESTÁ MAL NADA ESTÁ BIEN
%% remove_dups([], R):-
%% 	R,!.
%% remove_dups(T, R):-
%% 	R = [R|T].
%% remove_dups([H|T], R):-
%% 	remove_dups(T, [R|H]).
%% %% remove_dups([H|T],R):-
%% %% 	in_list(H,R) == true,
%% %% 	remove_dups(T, R).

%% flatten([H|T], R):-
%% 	H is atom,
%% 	R = [R,H].

increase(tree(N,R1,R2), A):-
	write('Element? '),
	read(I1),
	nl,
	write('Increase? '),
	read(I2),
	nl.