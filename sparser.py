"""
Smalltalk statement parser
"""

from ply import yacc

from lexer import tokens


class ParseStatement(object):
    def __init__(self, x):
        self.data = x

class ParseExecStatement(ParseStatement): pass

class ParseReturnStatement(ParseStatement): pass

class ParseMessage(object):
    def __init__(self, recv, *args):
        self.recv = recv
        self.name = [*args]

class ParseLiteral(object):
    def __init__(self, x):
        self.value = x

def p_statement(p):
    r'''statement : exec_statement
                  | return_statement'''
    p[0] = p[1] 
    
def p_return_statement(p):
    r'''return_statement : CARET exec_statement'''
    p[0] = ParseReturnStatement(p[2])
    
def p_exec_statement(p):
    r'''exec_statement : unary_message
                       | literal'''
    p[0] = ParseExecStatement(p[1])
    
def p_unary_message(p):
    r'''unary_message : IDENT IDENT'''
    p[0] = ParseMessage(p[1], p[2])
    
def p_literal(p):
    r'''literal : IDENT
                  | DECNUMBER'''
    p[0] = ParseLiteral(p[1])

# globals
Parser = yacc.yacc()
