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

class ParsePrimitive(object):
    def __init__(self, x):
        self.data = x

def p_statement(p):
    r'''statement : exec_statement
                  | return_statement'''
    p[0] = p[1] 
    
def p_return_statement(p):
    r'''return_statement : CARET exec_statement'''
    p[0] = ParseReturnStatement(p[2])
    
def p_exec_statement(p):
    r'''exec_statement : primitive'''
    p[0] = ParseExecStatement(p[1])
    
def p_primitive(p):
    r'''primitive : IDENT
                  | DECNUMBER'''
    p[0] = ParsePrimitive(p[1])

# globals
Parser = yacc.yacc()
