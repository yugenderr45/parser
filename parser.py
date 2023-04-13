import sys
from lexer import Token,Lexer

def main(lexer):
    
    parser=Parser(lexer)
    if not parser.parse():
        print("Parsing failed with %d errors."%(parser.errors))

class Parser:
    def __init__(self,lexer):
        self.lexer=lexer
        self.errors=0

    def next(self):
        lexer.next()
    def match(self,token):

        #iterable logic
        if hasattr(token,'__iter__'):
            return self.lexer.cur_tok.token in token

        #singular comparison logic
        return self.lexer.cur_tok.token==token

    def have(self,token):

        if self.match(token):
            self.next()
            return True
        return False

    def must_be(self,token,error_msg="Unexpected Token"):

        #check for success
        if self.match(token):
            self.next()
            return
        #error
        self.errors+=1
        error_tok=self.lexer.cur_tok
        self.next()
        print("Error %s %s:\"%s\" at Line %d Column %d"%(error_msg,
            error_tok.token,error_tok.lex,error_tok.line,error_tok.col))

    def parse(self):

        #get first token
        self.next()

        #call the start symbol's parser function
        self.parse_program()
        #return true if we had no error, false otherwise
        return self.errors==0

    def parse_program(self):
        self.parse_function_def()
        while not self.have(Token.EOF):
            self.parse_function_def()



    def parse_function_def(self):
        self.parse_signature()
        self.parse_block()

    def parse_signature(self):
        self.parse_type()
        self.must_be(Token.ID)
        self.must_be(Token.leftParenthesis)
        #handle signature'
        if self.have(Token.rightParenthesis):
            #blank param list
            return
        self.parse_params()
        self.must_be(Token.rightParenthesis,"Mismatched Parenthesis")

    def parse_params(self):
        self.parse_decl()
        #param'
        while self.have(Token.COMMA):
            self.parse_decl()

    def parse_block(self):
        self.must_be(Token.BEGIN)
        if self.have(Token.END):
            # null block
            return
        self.parse_statement_list()
        if self.have(Token.RETURN):
            self.parse_statement_list()
        self.must_be(Token.END," miss match")

        

    def parse_statement_list(self):

        self.parse_statement()
        first=(Token.NUMBER,Token.ID,
            Token.intNumb,Token.floatNumb,Token.leftParenthesis,Token.WHILE,Token.IF,Token.PRINT,Token.READ)
        while self.match(first):
            self.parse_statement()

    def parse_statement(self):      
        if self.match((Token.NUMBER,Token.CHARACTER)):
            self.parse_decl()
        elif self.match(Token.WHILE):
            self.parse_while()
        elif self.match(Token.IF):
            self.parse_if()
        elif self.match(Token.PRINT):
            self.parse_print()
        elif self.match(Token.READ):
            self.parse_read()
        elif self.have(Token.ID):
            #statement'

            if self.have(Token.ASSIGN):
                self.parse_expr()
            elif self.have(Token.SWAP):
                self.must_be(Token.ID,"Unable to swap")
            elif self.have(Token.ID):
                print(Token.ID,"Immediate IDS dected")
            elif self.have(Token.leftParenthesis):
                
                self.parse_call2()
            else:
                self.parse_expr2()
        else:
            self.parse_expr()

    def parse_print(self):
        self.must_be(Token.PRINT)
        self.must_be(Token.leftParenthesis)
        self.parse_expr()
        self.must_be(Token.rightParenthesis)
    def parse_read(self):
        self.must_be(Token.READ)
        self.must_be(Token.leftParenthesis)
        self.must_be(Token.ID)
        self.must_be(Token.rightParenthesis)

    def parse_call2(self):
        if self.have(Token.rightParenthesis):
            #empty arg list
            return
        self.parse_args()
        self.must_be(Token.rightParenthesis,"Mismatched Parenthesis")
    def parse_decl(self):

        self.parse_type()
        self.must_be(Token.ID)

    def parse_type(self):

        if self.have(Token.NUMBER):
            return
        elif self.have(Token.CHARACTER):
            return
        self.must_be(Token.PROC,"Must be PROC")

    def parse_args(self):

        self.parse_expr()
        while self.have(Token.COMMA):
            self.parse_expr()

    def parse_while(self):

        self.must_be(Token.WHILE)
        self.must_be(Token.leftParenthesis)
        self.parse_expr()
        self.must_be(Token.rightParenthesis,"Mismatched Parenthesis")
        self.parse_body()

    def parse_if(self):
        self.must_be(Token.IF)
        self.must_be(Token.leftParenthesis)
        self.parse_expr()
        self.must_be(Token.rightParenthesis)
        self.parse_body()

    def parse_body(self):
        self.parse_block()
    

    def parse_expr(self):
        self.parse_sum()
        self.parse_expr2()

    def parse_expr2(self):
        first=(Token.lessThan,Token.lessThanEqual,Token.greaterThan,Token.greaterThanEqual,Token.EQUAL,Token.notEqual)
        while self.match(first):
            if self.have(Token.notEqual):
                self.parse_sum()
            elif self.have(Token.lessThan):
                self.parse_sum()
            elif self.have(Token.lessThanEqual):
                self.parse_sum()
            elif self.have(Token.greaterThan):
                self.parse_sum()
            elif self.have(Token.greaterThanEqual):
                self.parse_sum()
            elif self.have(Token.EQUAL):
                self.parse_sum()
            else:
                print("Satement Error at Line %d Column %d"%(lexer.cur_tok.line,lexer.cur_tok.col))

    def parse_sum(self):
        self.parse_mul()

        #sum'
        first=(Token.PLUS,Token.MINUS)
        while self.match(first):
            if self.match(Token.PLUS):
                self.parse_mul()
            elif self.match(Token.MINUS):
                self.parse_mul()
            else:
                print("Satement Error at Line %d Column %d"%(lexer.cur_tok.line,lexer.cur_tok.col))


    def parse_mul(self):
        self.parse_value()
        #mul'
        first=(Token.TIMES,Token.DIVIDE,Token.PLUS,Token.MINUS,Token.EXPONENT)
        while self.match(first):
            if self.have(Token.TIMES):
                self.parse_value()
            elif self.have(Token.DIVIDE):
                self.parse_value()
            elif self.have(Token.MINUS):
                self.parse_value()
            elif self.have(Token.PLUS):
                self.parse_value()
            elif self.have(Token.EXPONENT):
                self.parse_value()
            else:
                print("Satement Error at Line %d Column %d"%(lexer.cur_tok.line,lexer.cur_tok.col))


    def parse_value(self):
        #number
        if self.have(Token.intNumb):
            #integer
            return
        elif self.have(Token.floatNumb):
            #float
            return
        if self.have(Token.ID):
            #value'
            if self.have(Token.leftParenthesis):
                self.parse_call2()
            return
        if self.have(Token.leftParenthesis):
            self.parse_expr()
            self.must_be(Token.rightParenthesis,"Mismatched Parenthesis")

if __name__=='__main__':
    file=open(sys.argv[1])
    lexer=Lexer(file)
    main(lexer)