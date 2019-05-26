from automata.autos.dfa import DFA
from automata.autos.nfa import NFA
nfa = NFA(states={'0', '1', '2'}, inistate='0', final_states={'0'},
              alphabet={'a', 'b'}, transition_matrix={
            '0': {'a': ('0', '1'), 'b': '0'},
            '1': {'b': '2'},
            '2': {}
        })
print(nfa.accepts_input('abb'))
dfa = DFA.from_nfa(nfa)
dfa = dfa.minimize()
