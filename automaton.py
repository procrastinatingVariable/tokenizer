import io
import collections

regexi = {
    "identifier": r"([a-zA-Z_]\w*)",
    "decimal": r"(([1-9]\d*)|(0[xX][0-9A-Fa-f]+)|(0[0-7]*))(((l{1,2}|L{1,2})[uU]?)|([uU](l{1,2}|L{1,2})?))?",
    "floating": r"((((\d*\.\d+)|(\d+\.))([eE][\+-]?\d+)?)|(\d+)([eE][\+-]?\d+))[flFL]?",
    "char": r"L?'([^'\n\\]|\\['?\\abfnrtv])+'",
    "string": r'L?"([^"\n\\]|\\["?\\abfnrtv])+"',
    "punctuators": r"\*=|\/=|%=|\+=|-=|<<=|>>=|&=|\^=|\|=|,|##|#|\.\.\.|\[|\]|\(|\)|\{|\}|\.|->|\+\+|--|\*|\+|-|~|\/|%|>>|<<|<=|>=|==|!=|>|<|\^|&&|\|\||\?|:|;|=|!|&|\|"
}

TOKEN_KEYWORD = 0
TOKEN_IDENTIFIER = 1
TOKEN_STRINGLIT = 2
TOKEN_CHARLIT = 3
TOKEN_PUNCTUATOR = 4
TOKEN_DECIMAL = 5
TOKEN_FLOATING = 6
TOKEN_WHITESPACE = 7
TOKEN_COMMENT = 10
TOKEN_DELIMITER = 11


class DFA:
    '''
    Deterministic Finite Automaton implementation
    '''

    class BlockError(Exception):
        pass

    def __init__(self, states:set, alphabet:set, ignoring:set, accepting:set, tfunc:dict, sstate):
        self._states = states
        self._alphabet = alphabet
        self._accepting = accepting
        self._tfunc = tfunc
        self._sstate = sstate
        self._curr_state = sstate
        self._ignoring = ignoring

    def consume(self, input):
        '''
        Consumes a character and transitions the DFA to the next state based
        on the transition function.

        Throws a BlockError exception if there's no mapping on the input
        character for the current state.
        '''
        if input not in alphabet:
            raise DFA.BlockError()

        if input in self._ignoring:
            return

        else :
            try:
                new_state = tfunc[self._curr_state][input]
            except KeyError:
                raise DFA.BlockError()
            self._curr_state = new_state
        
        return self

    def setstate(self, state):
        self._curr_state = state

    def isaccepting(self):
        return self._curr_state in self._accepting

    def check(self):
        return self._curr_state

    def reset(self):
        self._curr_state = sstate


vocab = set([chr(x) for x in range(32, 127)] + ['\n', '\t', '\r', '\a', '\v'])
letters = set([chr(x) for x in list(range(ord('a'), ord('z')+1)) + list(range(ord('A'), ord('Z')+1))])
digits = set([chr(x) for x in range(ord('0'), ord('9')+1)])
nonzero = digits - set('0')
hexas = digits | set('ABCDEFabcdef')
octal = set('01234567')
word = digits | letters
safe_char = vocab - set('\'\n\\')
safe_string = vocab - set('"\n\\')
nonl = vocab - set('\n')
nostar = vocab - set('*')
noslash = vocab - set('/')
sign = set('+-')
escapes = set('\'?\\ntrav')
escapess = set('"?\\ntrav')
whitespace = set('\n\t\r ')

def transit(all:set, to:int):
    set_list = list(all)
    to_list = len(set_list) * [to]
    paired_list = list(zip(set_list, to_list))
    return dict(paired_list)

states = list(range(74))
alphabet = vocab
accepting = [
    (6, TOKEN_DELIMITER),
    (9, TOKEN_IDENTIFIER),
    (11, TOKEN_WHITESPACE),
    (12, TOKEN_IDENTIFIER),
    (17, TOKEN_FLOATING),
    (21, TOKEN_DECIMAL),
    (22, TOKEN_DECIMAL),
    (24, TOKEN_DECIMAL),
    (25, TOKEN_DECIMAL),
    (28, TOKEN_IDENTIFIER),
    (29, TOKEN_IDENTIFIER),
    (30, TOKEN_FLOATING),
    (34, TOKEN_WHITESPACE),
    (35, TOKEN_STRINGLIT),
    (39, TOKEN_CHARLIT),
    (44, TOKEN_FLOATING),
    (45, TOKEN_DECIMAL),
    (46, TOKEN_FLOATING),
    (48, TOKEN_FLOATING),
    (49, TOKEN_DECIMAL),
    (50, TOKEN_COMMENT),
    (54, TOKEN_DECIMAL),
    (55, TOKEN_DECIMAL),
    (56, TOKEN_DECIMAL),
    (57, TOKEN_DECIMAL),
    (58, TOKEN_DECIMAL),
    (60, TOKEN_DECIMAL),
    (61, TOKEN_FLOATING),
    (65, TOKEN_FLOATING),
    (67, TOKEN_COMMENT),
    (69, TOKEN_DECIMAL),
    (70, TOKEN_DECIMAL),
    (72, TOKEN_FLOATING),
    (73, TOKEN_FLOATING)
]
tfunc = {
    0: {'"': 1, '\'': 2, '.': 3, '/': 4, '0': 5, ';': 6, **transit(nonzero, 7), 'L': 8, '_': 9, **transit(digits, 10), **transit(whitespace, 11), **transit(letters, 12)},
    1: {**transit(safe_string, 13), '\\': 14},
    2: {**transit(safe_char, 15), '\\': 16},
    3: {**transit(digits, 17)},
    4: {'/': 18, '*': 19},
    5: {**transit(octal, 20), 'L': 21, 'U': 22, 'X': 23, 'l': 24, 'u': 25, 'x': 26},
    7: {'L': 21, 'U': 22, **transit(digits, 27), 'l': 24, 'u': 25},
    8: {'"': 1, '\'': 2},
    9: {'_': 28, **transit(word, 29)},
    10: {'.': 30, 'E': 31, **transit(digits, 32), 'e': 33},
    11: {**transit(whitespace, 34)},
    12: {'_': 28, **transit(word, 29)},
    13: {'"': 35, **transit(safe_string, 36), '\\': 37},
    14: {**transit(escapes, 38)},
    15: {'\'': 39, **transit(safe_char, 40), '\\': 41},
    16: {**transit(escapes, 42)},
    17: {'E': 43, 'F': 44, 'L': 45, **transit(digits, 46), 'e': 47, 'f': 48, 'l': 49},
    18: {'\n': 50, **transit(nonl, 51)},
    19: {**transit(nostar, 52), '*': 53},
    20: {**transit(octal, 20), 'L': 21, 'U': 22, 'l': 24, 'u': 25},
    21: {'L': 54, 'U': 55, 'u': 56},
    22: {'L': 57, 'l': 58},
    23: {**transit(hexas, 59)},
    24: {'U': 55, 'l': 60, 'u': 56},
    25: {'L': 57, 'l': 58},
    26: {**transit(hexas, 59)},
    27: {'L': 21, 'U': 22, **transit(digits, 27), 'l': 24, 'u': 25},
    28: {'_': 28, **transit(word, 29)},
    29: {'_': 28, **transit(word, 29)},
    30: {'E': 43, 'F': 44, 'L': 45, **transit(digits, 17), 'e': 47, 'f': 48, 'l': 49},
    31: {'digit': 61, **transit(sign, 62)},
    32: {'.': 30, 'E': 31, **transit(digits, 32), 'e': 33},
    34: {**transit(whitespace, 34)},
    36: {'"': 35, **transit(safe_string, 36), '\\': 37},
    37: {**transit(escapes, 63)},
    38: {'"': 35, **transit(safe_string, 36), '\\': 37},
    40: {'\'': 39, **transit(safe_char, 40), '\\': 41},
    41: {**transit(escapes, 64)},
    42: {'\'': 39, **transit(safe_char, 40), '\\': 41},
    43: {**transit(digits, 65), **transit(sign, 66)},
    46: {'E': 43, 'F': 44, 'L': 45, **transit(digits, 46), 'e': 47, 'f': 48, 'l': 49},
    47: {**transit(digits, 65), **transit(sign, 66)},
    51: {'\n': 50, **transit(nonl, 51)},
    52: {**transit(nostar, 52), '/': 67, '*': 53},
    53: {**transit(noslash, 68), '/': 67},
    54: {'U': 55, 'u': 56},
    57: {'L': 69},
    58: {'l': 70},
    59: {'L': 21, 'U': 22, **transit(hexas, 71), 'l': 24, 'u': 25},
    60: {'U': 55, 'u': 56},
    61: {'F': 44, 'L': 45, **transit(digits, 72), 'f': 48, 'l': 49},
    62: {**transit(digits, 61)},
    63: {'"': 35, **transit(safe_string, 36), '\\': 37},
    64: {'\'': 39, **transit(safe_char, 40), '\\': 41},
    65: {'F': 44, 'L': 45, **transit(digits, 73), 'f': 48, 'l': 49},
    66: {**transit(digits, 65)},
    68: {'*': 53, **transit(nostar, 52)},
    71: {'L': 21, 'U': 22, **transit(hexas, 71), 'l': 24, 'u': 25},
    72: {'F': 44, 'L': 45, **transit(digits, 72), 'f': 48, 'l': 49},
    73: {'F': 44, 'L': 45, **transit(digits, 73), 'f': 48, 'l': 49}
}
sstate = 0

def state2token(state): 
    acc_states = list(zip(*accepting))[0]
    acc_tokens = list(zip(*accepting))[1]
    state_index = acc_states.index(state)
    return acc_tokens[state_index]


class DFAHistStack:

    def __init__(self):
        self._stack = []

    def push(self, token, isaccepting = False):
        self._stack.append((*token, isaccepting))

    def pop(self):
        return self._stack.pop()

    def buildtoken(self):
        try:
            split_stack = list(zip(*self._stack))
            values = split_stack[1]
            lai = self.find_lastacc_index()
            return ''.join(values[:lai+1])
        except:
            return None
            
    def find_lastacc_index(self):
        split_stack = list(zip(*self._stack))
        try :
            acceptings = split_stack[2]
        except:
            acceptings = []
        return len(acceptings) - acceptings[::-1].index(True) - 1

    def clear(self):
        self._stack.clear()

    def stack(self):
        return self._stack

class PushbackBuffer():

    def __init__(self, source):
        self._deque = collections.deque()
        self._source = source
        self.feed(next(self._source))

    def feed(self, iter):
        self._deque.extend(iter)

    def pushback(self, iter):
        self._deque.extendleft(reversed(iter))

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self._deque.popleft()
        except:
            return self._tryfromsource()
            
    def _tryfromsource(self):
        try:
            self.feed(next(self._source))
            return self._deque.popleft()
        except:
            raise StopIteration()




class Scanner :

    class SyntaxError(Exception):

        def __init__(self, pos):
            self.pos = pos

    def __init__(self, input:iter, dfa:DFA):
        self._dfa = dfa
        self._dfa.reset()

        self._dfastack = DFAHistStack()
        self._buffer = PushbackBuffer(input)


    def gettoken(self):
        for c in self._buffer:
            try:
                self._dfa.consume(c)
                isaccepting = self._dfa.isaccepting()
                self._dfastack.push((self._dfa.check(), c), isaccepting)
            except:
                self._buffer.pushback(c)
                break

        if self._dfa.isaccepting():
            token = self._dfastack.buildtoken()
        else:
            token = self._dfastack.buildtoken()
            self._pushback_noacc_stack()

        if token:
            dfa.reset()
            self._dfastack.clear()
            return token
        else:
            raise SyntaxError()

    def _pushback_noacc_stack(self):
        stack = self._dfastack.stack()
        try:
            lai = self._dfastack.find_lastacc_index()
        except ValueError:
            lai = -1
        for i in reversed(stack[lai+1:]):
            self._buffer.pushback(i[1])
            self._dfa.setstate(i[0])
            self._dfastack.pop()




acc_states = list(zip(*accepting))[0]
dfa = DFA(states, alphabet, set(), acc_states, tfunc, sstate)

f = open('in.c', 'r')
scanner = Scanner(f, dfa)
while (True): 
    tok = scanner.gettoken()
    print(tok)
        
