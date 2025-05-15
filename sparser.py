"""
Smalltalk statement parser
"""

from ply import yacc

from lexer import tokens


class ParseStatementList(object):
    def __init__(self, x):
        self.data = x

class ParseStatement(object):
    def __init__(self, x):
        self.data = x

class ParseExecStatement(ParseStatement): pass

class ParseReturnStatement(ParseStatement): pass

class ParseMessage(object):
    def __init__(self, recv, name):
        self.recv = recv
        self.name = name

class ParseUnaryMessage(ParseMessage): pass
        
class ParseExprMessage(ParseMessage):
    def __init__(self, recv, name, send):
        super().__init__(recv, name)
        self.send = send

class ParseLiteral(object):
    def __init__(self, x):
        self.value = x
        
def p_statement_list(p):
    r'''statement_list : statement'''
    p[0] = ParseStatementList(p[1:])

def p_statement(p):
    r'''statement : exec_statement
                  | return_statement'''
    p[0] = p[1] 
    
def p_return_statement(p):
    r'''return_statement : CARET exec_statement'''
    p[0] = ParseReturnStatement(p[2])
    
def p_exec_statement(p):
    r'''exec_statement : expr_message
                       | unary_message
                       | literal'''
    p[0] = ParseExecStatement(p[1])
    
def p_unary_message(p):
    r'''unary_message : literal IDENT'''
    p[0] = ParseUnaryMessage(p[1], p[2])
    
def p_expr_message(p):
    r'''expr_message : literal OPERATOR exec_statement'''
    p[0] = ParseExprMessage(p[1], p[2], p[3])
    
def p_literal(p):
    r'''literal : IDENT
                | DECNUMBER'''
    p[0] = ParseLiteral(p[1])
    
    
# token precedence rules for the parser
# tokens are listed from lowest to highest precedence   
precedence = (
    ('left', 'ASSIGN'),
    ('left', 'IDENT'),
    ('left', 'OPERATOR'),
    ('left', 'DECNUMBER'),
)

# globals
Parser = yacc.yacc()
