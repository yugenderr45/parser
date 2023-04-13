"""
This module implements a lexical analyzer and includes a unit test for that
lexer.
"""
from enum import Enum,auto
from collections import namedtuple


class Token(Enum):
    """
    Tokens of our language.
    """
    INVALID = auto()
    EOF = auto()
    leftParenthesis = auto()
    rightParenthesis = auto()
    COMMA = auto()
    #leftBrace = auto()
    #rightBrace = auto()
    
    lessThan = auto()
    greaterThan = auto()
    lessThanEqual=auto()
    greaterThanEqual = auto()
    
    PROC = auto()
    PLUS = auto()
    MINUS = auto()
    TIMES = auto()
    DIVIDE = auto()
    EXPONENT=auto()
    
    intNumb = auto()
    floatNumb = auto()
    CHARACTER = auto()

    ASSIGN = auto()
    EQUAL = auto()
    NUMBER = auto()
    WHILE = auto()
    ID = auto()
    notEqual=auto()
    END=auto()
    IF = auto()
    ELSE=auto()
    PRINT=auto()
    RETURN = auto()
    
    SWAP=auto()
    READ=auto()
    BEGIN=auto()





# The lexeme named tuple stores our lexical element records
Lexeme = namedtuple("Lexeme", ("token", "lex", "value", "line", "col"))


def floatNumb(s):
    pass


class Lexer:
 
    def __init__(self, file):
        self.file = file
        self.line = 1
        self.col = 0
        self.cur_char = ' '
        self.cur_tok = None


    def read(self):
        """
        Read a single character from the file stream.  Store the character in
        cur_char.  Updates column.
        """
        self.cur_char = self.file.read(1)
        if self.cur_char:
            self.col += 1

    def consume(self):
        """
        Advance to the next character, keeping track of line and col. The next
        character is stored in cur_char.
        """
        self.read()

        # detect the end of the line
        if self.cur_char == '\n':
            self.line += 1
            self.col = 0
        """HANDLE TO CONSUME THE LINE """
    def line_consumer(self):
        while (self.cur_char != '\n'):
            # read the char untilll got the \n
            self.read()
        self.read()


    def skip_space(self):
        """
        Consume characters until we reach either EOF or a non-space character.
        """
        while self.cur_char.isspace():
            self.consume()


    def group1(self):
        """
        Match the group 1 tokens. Group 1 tokens are single character tokens
        which are not prefixes of any other token.
        """
        tokens = (
                  
                  ('(', Token.leftParenthesis),
                  (')', Token.rightParenthesis),
                  (',', Token.COMMA),
                  ('*', Token.TIMES), ('/', Token.DIVIDE),
                  ('+', Token.PLUS), ('-', Token.MINUS),
                   ('=', Token.EQUAL))

        # scan for a match
        for lex,t in tokens:
            if self.cur_char == lex:
                self.cur_tok = Lexeme(t, lex, lex, self.line, self.col)
                self.consume()
                return True

        return False


    def group2(self):
        """
        Match the group 2 tokens. Group 2 tokens have fixed width and can have
        shared prefixes, but they are not the prefix of any group 3 token.
        """
        tokens = ((':=:', Token.SWAP), ('~=', Token.notEqual),('<', Token.lessThan), ('<=', Token.lessThanEqual),
                  ('>', Token.greaterThan), ('>=', Token.greaterThanEqual),(':=', Token.ASSIGN),
                  ('**', Token.EXPONENT))

        # preserve the start position
        line = self.line
        col = self.col

        # create the remain filter
        remain = lambda s : [tok for tok in tokens if tok[0].startswith(s)]

        # continue until we no longer would match
        s = ''
        while len(remain(s + self.cur_char)) > 0:
            # add the character to our string and consume
            s = s + self.cur_char
            self.consume()

        # if our string is empty, no match
        if len(s) == 0:
            return False

        # get the final candidates
        tokens = remain(s)

        # find the token which we match
        for tok in tokens:
            if tok[0] == s:
                self.cur_tok = Lexeme(tok[1], s, s, line, col)
                return True

        # if we make it here, then this is a partially formed token
        self.cur_tok = Lexeme(Token.INVALID, s, None, line, col)
        return True


    def group3(self):
        """
        Match the group 3 tokens. Group 3 tokens have variable width and can
        have shared prefixes. There are some tokens in this group which can be
        a prefix of a variable width token, but which are themselves fixed
        (keywords).
        """

        if self.cur_char.isalpha():
            return self.group3_letter()
        elif self.cur_char.isdigit():
            return self.group3_number()
        return False
    def handle_(self):
        # IN ORDER TO ENSURE THAT IT IS ID

        ss = ""
        ss+=self.cur_char
        while (self.cur_char == '_' or self.cur_char.isalpha() == True or self.cur_char.isdigit() == True):
            ss+=self.cur_char
            self.consume()
        return ss


    def group3_letter(self):
        """
        Match either a keyword or an ID.
        """

        tokens = (('WHILE', Token.WHILE),('END', Token.END), ('BEGIN', Token.BEGIN),('NUMBER', Token.NUMBER), ('CHARACTER', Token.CHARACTER),('ELSE', Token.ELSE), ('IF', Token.IF),
                  ('PROC', Token.PROC), ('RETURN', Token.RETURN),('PRINT', Token.PRINT))

        # read all the letters, remembering where we started
        line = self.line
        col = self.col
        s = ""
        while self.cur_char.isalpha():
            s = s + self.cur_char
            self.consume()

        # if we have a blank string, we do not match
        if len(s) == 0:
            return False


        # check for keyword matches
        for lex,t in tokens:
            if lex == s:
                self.cur_tok = Lexeme(t, s, s, line, col)
                return True


        temp=""
        temp=self.handle_()
        s=s+temp
        self.cur_tok = Lexeme(Token.ID, s, s, line, col)
        return True



    def group3_number(self):
        """
        Matches either an intNumb or a floatNumb
        """
        # preserve position
        line = self.line
        col = self.col

        # start in the intNumb state
        token = Token.intNumb

        # consume all the numbers
        s = ''
        while self.cur_char.isdigit():
            s = s + self.cur_char
            self.consume()

        # check for no match
        if len(s) == 0:
            return False

        # check to see if this is our final state
        if self.cur_char != '.':
            self.cur_tok = Lexeme(token, s, int(s), line, col)
            return True

        # continue processing
        token = Token.INVALID
        s = s + '.'
        self.consume()

        # consume the fraction part
        while self.cur_char.isdigit():
            token = Token.floatNumb
            s = s + self.cur_char
            self.consume()

        # get the value
        if token == Token.floatNumb:
            value = floatNumb(s)
        else:
            value = None

        # update the token
        self.cur_tok = Lexeme(token, s, value, line, col)
        return True
    """ defined method will handle the comments in case if he got it will ignore the line"""
    def commentHandler(self):
        # it will handle the comments
        run=1
        while run:
            # skip the space
            self.skip_space()
            # skip comments
            if self.cur_char == '#':
                self.line_consumer()
            if(self.cur_char==' ' or self.cur_char=='#'):
                ignore=''
            else:
                break




    def next(self):
        """
        Advance the lexer to the next token in the stream.
        """
        self.commentHandler()
        # handle the end of the file
        if not self.cur_char:
            self.cur_tok = Lexeme(Token.EOF, None, None, self.line, self.col)
            return self.cur_tok

        # try each lexing possibility
        if self.group1():
            return self.cur_tok
        elif self.group2():
            return self.cur_tok
        elif self.group3():
            return self.cur_tok
        else:
            # must be an invalid token
            self.cur_tok = Lexeme(Token.INVALID, self.cur_char, None, self.line, self.col)
            self.consume()
            return self.cur_tok





