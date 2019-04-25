import io
import collections
import sys

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

tokdict = {
    TOKEN_KEYWORD: "keyword",
    TOKEN_IDENTIFIER: "identifier",
    TOKEN_STRINGLIT: "string literal",
    TOKEN_CHARLIT: "char literal",
    TOKEN_PUNCTUATOR: "punctuator",
    TOKEN_DECIMAL: "decimal",
    TOKEN_FLOATING: "floating",
    TOKEN_WHITESPACE: "whitespace",
    TOKEN_COMMENT: "comment",
    TOKEN_DELIMITER: "delimiter"
}


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
punctuators = set('[](){}.-+&*~!/%<>^|?:#,')
keywords = set([
    'auto',
    'break',
    'case',
    'char',
    'const',
    'continue',
    'default',
    'do',
    'double',
    'else',
    'enum',
    'extern',
    'float',
    'for',
    'goto',
    'if',
    'inline',
    'int',
    'long',
    'register',
    'restrict',
    'return',
    'short',
    'signed',
    'sizeof',
    'static',
    'struct',
    'switch',
    'typedef',
    'union',
    'unsigned',
    'void',
    'volatile',
    'while'
])


states = list(range(17))
alphabet = vocab

accepting = [
    (1, TOKEN_IDENTIFIER),
    (2, TOKEN_DECIMAL),
    (3, TOKEN_PUNCTUATOR),
    (4, TOKEN_PUNCTUATOR),
    (5, TOKEN_WHITESPACE),
    (6, TOKEN_DELIMITER),
    (10, TOKEN_COMMENT),
    (12, TOKEN_STRINGLIT),
    (13, TOKEN_FLOATING),
    (16, TOKEN_FLOATING)
]

tfunc = {
   0: {**transit(letters, 1), **transit(digits, 2), '/': 3, **transit(whitespace, 5), ';': 6, **transit(set('+*()={}<>=&^#|'), 4), '"': 11},
   1: {**transit(word, 1)},

   2: {**transit(digits, 2), '.': 13, **transit(set('eE'), 14)},
   3: {'*': 8},
   5: {**transit(whitespace, 5)},
   8: {**transit(nostar, 8), '*': 9},
   9: {**transit(noslash, 8), '/': 10},
   11: {**transit(safe_string, 11), '"': 12},
   13: {**transit(digits, 13), **transit(set('eE'), 14)},
   14: {**transit(sign, 15), **transit(digits, 16)},
   15: {**transit(digits, 16)},
   16: {**transit(digits, 16)}
}


sstate = 0


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
        self._row = 1
        self.feed(next(self._source))

    def feed(self, iter):
        self._deque.extend(iter)

    def pushback(self, iter):
        self._deque.extendleft(reversed(iter))

    def isempty(self):
        return len(self._deque) == 0

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
            self._row = self._row + 1
            return self._deque.popleft()
        except:
            raise StopIteration()




class Scanner :

    class SyntaxException(Exception):

        def __init__(self, r, c):
            self.col = c
            self.row = r

    def __init__(self, input:iter, dfa:DFA):
        self._dfa = dfa
        self._dfa.reset()

        self._dfastack = DFAHistStack()
        self._buffer = PushbackBuffer(input)

        self._tokenvalues = []


    def gettoken(self):
        for c in self._buffer:

            try:
                self._dfa.consume(c)
                isaccepting = self._dfa.isaccepting()
                self._dfastack.push((self._dfa.check(), c), isaccepting)
            except:
                token = self._buildtoken()
                toktype = token[0] if token else None
                if toktype != TOKEN_COMMENT and toktype != TOKEN_WHITESPACE:
                    self._buffer.pushback(c)
                    break
                else:
                    self._buffer.pushback(c)
                    self._dfa.reset()
                    self._dfastack.clear()
        
        token = self._buildtoken()
        if not self._dfa.isaccepting():
            self._pushback_noacc_stack()

        if token:
            dfa.reset()
            self._dfastack.clear()
            return token
        else:
            if self._buffer.isempty():
                raise EOFError()
            else:
                raise Scanner.SyntaxException(self._buffer._row, 0)


    def _buildtoken(self):
        tokenval = self._dfastack.buildtoken()
        tokval_cacheindex = self._cachetoken(tokenval)
        tokentype = self._type4state(self._dfa.check())
        if tokentype == TOKEN_IDENTIFIER:
            if tokenval in keywords:
                tokentype = TOKEN_KEYWORD
        return (tokentype, tokval_cacheindex) if tokentype != None and tokenval != None else None

    def tok2readable(self, token):
        toketype_val = token[0]
        tokval_cacheindex = token[1]

        return (tokdict[toketype_val], self._tokenvalues[tokval_cacheindex])

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

    def _type4state(self, dfastate):
        zipped = list(zip(*accepting))
        accstates = zipped[0]
        types = zipped[1]
        try:
            return types[accstates.index(dfastate)]
        except:
            return None

    def _cachetoken(self, tokval):
        try:
            return self._tokenvalues.index(tokval)
        except:
            self._tokenvalues.append(tokval)
            return len(self._tokenvalues) - 1


# MAIN

def parseargs():
    if len(sys.argv) != 3:
        print('USAGE: lexer <input file> <output file>')

    infilename = sys.argv[1]
    outfilename = sys.argv[2]
    global ifile
    global ofile

    try:
        ifile = open(infilename, 'r')
    except:
        print("Coudln't open input file")
    try:
        ofile = open(outfilename, 'w')
    except:
        print("Couldn't open output file")

    

acc_states = list(zip(*accepting))[0]
dfa = DFA(states, alphabet, set(), acc_states, tfunc, sstate)

parseargs()

scanner = Scanner(ifile, dfa)
while(True):
    try:
        tok = scanner.gettoken()
        toktype = tok[0]
        if toktype != TOKEN_COMMENT and toktype != TOKEN_WHITESPACE:
            ofile.write('{}\n'.format(scanner.tok2readable(tok)))
    except EOFError:
        print('Done scanning!')
        break
    except Scanner.SyntaxException as e:
        print("Syntax error on line {}".format(e.row))
        break

ifile.close()
ofile.close()
        
