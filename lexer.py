"""
Token definitions for parsing Smalltalk code text
"""

import ply.lex as lex

states = ( ('dstring', 'exclusive'),
           ('sstring', 'exclusive'), )

tokens = [
    'BASENUMBER',
    'FLTNUMBER',
    'DECNUMBER',
    'DSTRING',
    'SSTRING',
    'LBRACK',
    'RBRACK',
    'RSHIFT',
    'CARET',
    'PERIOD',
    'ASSIGN',
    'MESSAGEARG',
    'OPERATOR',
    'IDENT',
]

def t_BASENUMBER(t):
    r'\d+r[\dA-F]+'
    tstr = t.value.split('r')
    base = int(tstr[0])
    t.value = int(tstr[1], base)
    return t

def t_FLTNUMBER(t):
    r'-?\d+\.\d+(e-?\d+)*'
    t.value = float(t.value)
    return t

def t_DECNUMBER(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

def t_DSTRING(t):
    r'\"'
    t.lexer.code_start = t.lexer.lexpos
    t.lexer.begin('dstring')

def t_dstring_string(t):
    r'[^\"]'

def t_dstring_dquote(t):
    r'\"'
    t.type = 'DSTRING'
    t.value = t.lexer.lexdata[t.lexer.code_start:t.lexer.lexpos-1]
    t.lexer.lineno += t.value.count('\n')
    t.lexer.begin('INITIAL')
    return t
    
def t_SSTRING(t):
    r'\''
    t.lexer.code_start = t.lexer.lexpos
    t.lexer.begin('sstring')

def t_sstring_string(t):
    r'[^\']'

def t_sstring_squote(t):
    r'\''
    t.type = 'SSTRING'
    t.value = t.lexer.lexdata[t.lexer.code_start:t.lexer.lexpos-1]
    t.lexer.lineno += t.value.count('\n')
    t.lexer.begin('INITIAL')
    return t

def t_sstring_error(t):
    print("ERROR: ", t)

t_sstring_ignore = '\r'

def t_dstring_error(t):
    print("ERROR: ", t)

t_dstring_ignore = '\r'

def t_LBRACK(t):
    r'\['
    return t

def t_RBRACK(t):
    r'\]'
    return t
    
def t_RSHIFT(t):
    r'>>'
    return t
    
def t_PERIOD(t):
    r'\.'
    return t
    
def t_ASSIGN(t):
    r':='
    return t
    
def t_CARET(t):
    r'\^'
    return t
    
def t_MESSAGEARG(t):
    r'[a-zA-Z_][a-zA-Z_\d]*:'
    t.value = t.value.rstrip(':')
    return t
    
def t_OPERATOR(t):
    r'[\+\-\*\/\,<>=%~&\\][\+\-\*\/\,<>=%~&\\]?'
    return t
    
def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z_\d]*'
    return t
        
def t_error(t):
    print("ERROR: ", t.value[0])

t_ignore = ' \t\r\n'


# global variables
Lexer = lex.lex()