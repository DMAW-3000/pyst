"""
Smalltalk statement parser
"""

from ply import yacc

from lexer import tokens

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
    
        
def p_statement_list(p):
    r'''statement_list : statement_list PERIOD statement
                       | statement'''
    if len(p) == 2:
        p[0] = ParseStatementList(p[1])
    else:
        p[1].data.append(p[3])
        p[0] = p[1]

def p_statement(p):
    r'''statement : exec_statement
                  | assign_statement
                  | return_statement'''
    p[0] = p[1] 
    
def p_return_statement(p):
    r'''return_statement : CARET exec_statement'''
    p[0] = ParseReturnStatement(p[2])
    
def p_assign_statement(p):
    r'''assign_statement : IDENT ASSIGN exec_statement'''
    p[0] = ParseAssignStatement(p[1], p[3])
    
def p_exec_statement(p):
    r'''exec_statement : sub_statement
                       | argument_message
                       | expr_message
                       | unary_message
                       | literal'''
    p[0] = ParseExecStatement(p[1])
    
def p_sub_statement(p):
    r'''sub_statement : LPARENS exec_statement RPARENS'''
    p[0] = p[2]
    
def p_unary_message(p):
    r'''unary_message : unary_message IDENT
                      | literal IDENT'''
    p[0] = ParseUnaryMessage(p[1], p[2])
    
def p_expr_message(p):
    r'''expr_message : exec_statement OPERATOR literal
                     | exec_statement OPERATOR unary_message'''
    p[0] = ParseExprMessage(p[1], p[2], p[3])
    
def p_argument_message(p):
    r'''argument_message : exec_statement message_arg_list'''
    print("parse arg msg", p[1].data.value, p[2])
    p[0] = ParseArgumentMessage(p[1], p[2])
    
def p_message_arg_list(p):
    r'''message_arg_list : message_arg_list message_arg
                         | message_arg'''
    print("parse arg list", len(p), p[1])
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]
    
def p_message_arg(p):
    r'''message_arg : MESSAGEARG sub_statement
                    | MESSAGEARG unary_message
                    | MESSAGEARG expr_message
                    | MESSAGEARG literal'''
    print("parse msg arg", p[1], p[2])
    p[0] = ParseMessageArg(p[1], p[2])
    
def p_literal(p):
    r'''literal : block_literal
                | string_literal
                | IDENT
                | DECNUMBER'''
    print("parse lit", p[1])
    p[0] = ParseLiteral(p[1])
    
def p_block_literal(p):
    r'''block_literal : LBRACK statement_list RBRACK
                      | LBRACK RBRACK'''
    if len(p) == 3:
        p[0] = ParseLiteralBlock(None)
    else:
        p[0] = ParseLiteralBlock(p[2])
    
def p_string_literal(p):
    r'''string_literal : SSTRING'''
    p[0] = ParseLiteralString(p[1])
    
def p_error(t):
    raise ParseError("syntax error at %s(%s)" % (t.value, t.type))
    
    
# token precedence rules for the parser
# tokens are listed from lowest to highest precedence   
precedence = (
    ('left', 'OPERATOR'),
    ('left', 'IDENT'),
    ('left', 'MESSAGEARG'),
    ('left', 'LBRACK', 'RBRACK'),
    ('left', 'LPARENS', 'RPARENS'),
)

# globals

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
            
            
