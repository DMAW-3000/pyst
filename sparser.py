"""
Smalltalk statement parser
"""

class ParseError(Exception): pass

class ParseStatementList(object):
    """
    Represent a list of statements.
    """
    def __init__(self, x):
        self.data = x

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
    

class Parser(object):
    
    def __init__(self, lex):
        self._lex = lex
        self._lkahd = None
        
    def token(self):
        if self._lkahd is not None:
            t = self._lkahd
        else:
            t = self._lex.token()
        self._lkahd = None
        return t
        
    def lookahead(self):
        t = self._lex.token()
        if t is None:
            return t
        self._lkahd = t
        return t.type
            
    def drop(self):
        self._lkahd = None
        
    def parse(self):
        return ParseStatementList(self.parse_statement_list())
        
    def parse_statement_list(self):
        slist = [self.parse_statement()]
        return slist
        
    def parse_statement(self):
        """
        Parse a generic statement.  Splits ^ return
        statements.
        """
        if self.lookahead() == "CARET":
            self.drop()
            s = ParseReturnStatement(self.parse_exec_statement())
        else:
            s = self.parse_exec_statement()
        print(s)
        return s
            
    def parse_exec_statement(self):
        """
        Parse a non-return statement.  Splits :=
        assign statements.
        """
        tok = self.token()
        if self.lookahead() == "ASSIGN":
            self.drop()
            if tok.type != "IDENT":
                raise ParseError("expected ident before :=")
            return ParseAssignStatement(tok.value, self.parse_exec_statement())
        if tok.type == "IDENT":
            s = ParseExecStatement(self.parse_message(tok))
        else:
            s = ParseExecStatement(self.parse_literal(tok))
        print(s)
        return s
        
    def parse_message(self, recv):
        """
        Parse a generic message starting with token recv
        """
        tok = self.token()
        print("parse msg", recv, tok)
        if tok is None:
            s = self.parse_literal(recv)
        elif tok.type == "IDENT":
            s = ParseUnaryMessage(recv, tok.value)
        else:
            raise ParseError("expected ident")
        return s
        
    def parse_literal(self, t):
        """
        Parse a literal value from the given token
        """
        if t.type == "SSTRING":
            val = ParseLiteralString(t.value)
        else:
            val = t.value
        return ParseLiteral(val)
        
        
            
            
        
            
            
