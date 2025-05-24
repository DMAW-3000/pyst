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
        
    def parse(self):
        return ParseStatementList(self.parse_statement_list())
        
    def parse_statement_list(self):
        slist = []
        while True:
            tlist = []
            tok = self._lex.token()
            while (tok is not None) and (tok.type != "PERIOD"):
                tlist.append(tok)
                tok = self._lex.token()
            if len(tlist):
                print(tlist)
                slist.append(self.parse_statement(tlist))
            else:
                break
        return slist
        
    def parse_statement(self, tlist):
        if tlist[0].type == "CARET":
            if len(tlist) > 1:
                return ParseReturnStatement(self.parse_exec_statement(tlist[1:]))
            else:
                raise ParseError("empty return statement")
        elif (tlist[0].type == "IDENT") and \
             (len(tlist) > 1) and \
             (tlist[1].type == "ASSIGN"):
                return ParseAssignStatement(tlist[0].value, self.parse_exec_statement(tlist[2:]))
        else:
            return self.parse_exec_statement(tlist)
            
    def parse_exec_statement(self, tlist):
        return ParseExecStatement(ParseLiteral(tlist[0].value))
            
            
