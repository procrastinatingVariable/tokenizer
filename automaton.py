
class DFA:
    '''
    Deterministic Finite Automaton implementation
    '''

    ST_ERROR = -1

    def __init__(self, states:set, alphabet:set, accepting:set, tfunc:dict, sstate):
        self._states = states
        self._alphabet = alphabet
        self._accepting = accepting
        self._tfunc = tfunc
        self._sstate = sstate
        self._curr_state = sstate

        self._instring = ""
        self._curr_pos = 0

    def consume(self, input):
        if input not in alphabet or self._curr_state == DFA.ST_ERROR:
            self._curr_state = DFA.ST_ERROR
        else :
            try:
                new_state = tfunc[self._curr_state][input]
            except KeyError:
                new_state = DFA.ST_ERROR
            self._curr_state = new_state
        
        return self

    # def gettoken(self):
    #     if self._curr_pos == len(self._instring):
    #         raise DFA.FeedError()

    #     token_val = []
    #     for feedpos, c in enumerate(input):
    #         last_state = self._curr_state
    #         self.advance(input)
    #         if self._curr_state == DFA.ST_ERROR:
    #             if last_state in self._accepting:
    #                 return ''.join(token_val)
    #             else:
    #                 raise DFA.TokenError(feedpos)
    #         else:
    #             token_val.append(c)


    # def feed(self, input):
    #     self._instring = input
    #     self._curr_pos = 0

    def isaccepting(self):
        return self._curr_state in self._accepting

    def check(self):
        return self._curr_state

    def reset(self):
        self._curr_state = sstate
    
vocab = set([chr(x) for x in range(32, 127)])
def transition(all:set, to:int):
    set_list = list(all)
    to_list = len(set_list) * [to]
    paired_list = list(zip(set_list, to_list))
    return dict(paired_list)

def not_symbols(symbols:iter):
    return vocab - set(symbols)

states = [0,1,2,3,4]
alphabet = vocab
accepting = [4]
tfunc = {
    0: {'/': 1},
    1: {'*': 2},
    2: {'*': 3, **transition(not_symbols('*'), 2)},
    3: {'/': 4, **transition(not_symbols('/'), 2)}
}
sstate = 0
dfa = DFA(states, alphabet, accepting, tfunc, sstate)



        
