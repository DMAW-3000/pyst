"""
Smalltalk statement parser
"""

from lexer import tokens

class ParseError(Exception): pass

class ParseStatementList(object):
    """
    Represent a list of statements.
    """
    def __init__(self, x):
        self.data = [x]

class ParseStatement(object):
    """
    Represent a single statement
    """
    def __init__(self, x):
        self.data = x

class ParseExecStatement(ParseStatement):
    """
    Represent a statement with no return
    or assign.
    """
    pass

class ParseReturnStatement(ParseStatement):
    """
    Represent a return statement
    """
    pass

class ParseAssignStatement(ParseStatement):
    """
    Represent an assignment statement
    """
    def __init__(self, var, x):
        super().__init__(x)
        self.var = var

class ParseMessage(object):
    """
    Represent a message to a receiver
    """
    def __init__(self, recv):
        self.recv = recv

class ParseUnaryMessage(ParseMessage):
    """
    Represent a unary message
    """
    def __init__(self, recv, name):
        super().__init__(recv)
        self.name = name
        
class ParseExprMessage(ParseMessage):
    """
    Represent a binary expression message
    """
    def __init__(self, recv, name, send):
        super().__init__(recv)
        self.name = name
        self.send = send
        
class ParseArgumentMessage(ParseMessage):
    """
    Represent an argument list message
    """
    def __init__(self, recv, args):
        super().__init__(recv)
        self.args = args
        
class ParseMessageArg(object):
    """
    Represent a message argument/value pair
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value

class ParseLiteral(object):
    """
    Represent a literal value
    """
    def __init__(self, x):
        self.value = x
        
class ParseLiteralString(ParseLiteral):
    """
    Represent a 'string literal' value
    """
    pass
        
class ParseLiteralBlock(ParseLiteral):
    """
    Represent a [block] value
    """
    pass
 
class ParseError(Exception):
    """
    Signal a parser error
    """

class Parser(object):
    """
    Parser implementation
    """
    
    def __init__(self, lexer):
        self._lex = lexer
        self._la = [None] * 4
        self._la_first = 0
        self._la_size = 0
    
    def reset(self):
        self._la = [None] * 4
        self._la_first = 0
        self._la_size = 0
        self.lookahead(1)
        
    def lookahead(self, n):
        while self._la_size < n:
            i = (self._la_first + self._la_size) % 4
            self._la[i] = self._lex.token()
            self._la_size += 1
            print("[%d]: %s" % (i, self._la[i]))

    def consume(self, n):
        self._la_first = (self._la_first + n) % 4
        self._la_size -= n
        
    def lex(self):
        self.consume(1)
        self.lookahead(1)
        
    def token(self, n):
        i = (self._la_first + n) % 4
        return self._la[i].type
        
    def val(self, n):
        i = (self._la_first + n) % 4
        return self._la[i].value
        
    def lex_skip_if(self, tok):
        if self.token(0) != tok:
            return False
        else:
            self.lex()
            return True
        
    def parse_statements(self):
        sList = []
        while True:
            carFlag = self.lex_skip_if("CARET")
            if carFlag:
                s = self.parse_req_expr()
                sList.append(s)
            else:
                s = self.parse_expr()
                if s is None:
                    break
                sList.append(s)
            if (not self.lex_skip_if("PERIOD")) or carFlag:
                break
        return ParseStatementList(sList)
        
    def parse_req_expr(self):
        return None
        
    def parse_expr(self):
        return None
            