
% 4
duplicate_entries([]):-
    false.
duplicate_entries([H|T]):-
    member(H, T),
    duplicate_entries(T),
    !.



% 6
eliminate(_, [], R):-
    R = [], !.
eliminate(H, [H|T], R):-
    eliminate(H, T, R),
    !.
eliminate(X, [H|T], [H|Y]):-
    eliminate(X, T, Y).


remove_dups([], Z):-
    Z = [], !.
remove_dups([H|T], R):-
    member(H, T),
    eliminate(H, T, R2),
    remove_dups([H|R2], R),
    !.
remove_dups([H|T1], [H|T2]):-
    remove_dups(T1, T2).



% 8
flatten([],R):-
    R = [], !.
flatten([H|T], R):-
    is_list(H),
    flatten(H, R2),
    flatten(T, R3),
    append(R2, R3, R),
    !.
flatten([H|T1], [H|T2]):-
    flatten(T1, T2).
