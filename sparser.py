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
        
def p_statement_list(p):
    r'''statement_list : statement'''
    p[0] = ParseStatementList(p[1:])

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
    r'''expr_message : exec_statement OPERATOR exec_statement'''
    p[0] = ParseExprMessage(p[1], p[2], p[3])
    
def p_argument_message(p):
    r'''argument_message : unary_message message_arg_list
                         | literal message_arg_list'''
    p[0] = ParseArgumentMessage(p[1], p[2])
    
def p_message_arg_list(p):
    r'''message_arg_list : message_arg_list message_arg
                         | message_arg'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]
    
def p_message_arg(p):
    r'''message_arg : MESSAGEARG sub_statement
                    | MESSAGEARG literal'''
    p[0] = ParseMessageArg(p[1], p[2])
    
def p_literal(p):
    r'''literal : string_literal
                | IDENT
                | DECNUMBER'''
    p[0] = ParseLiteral(p[1])
    
def p_string_literal(p):
    r'''string_literal : SSTRING'''
    p[0] = tuple(p[1])
    
def p_error(t):
    raise ParseError("syntax error at %s(%s)" % (t.value, t.type))
    
    
# token precedence rules for the parser
# tokens are listed from lowest to highest precedence   
precedence = (
    ('left', 'DECNUMBER'),
    ('left', 'OPERATOR'),
    ('left', 'ASSIGN'),
    ('left', 'IDENT'),
    ('left', 'MESSAGEARG'),
    ('left', 'LPARENS', 'RPARENS'),
    ('left', 'SSTRING'),
)

# globals
Parser = yacc.yacc()
