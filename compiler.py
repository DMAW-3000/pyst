"""
Smalltalk bootstrap compiler
"""

from st import *
from lexer import Lexer

class CompileError(Exception): pass

class Compile(object):

    def __init__(self, system):
        """
        Create a blank compiler instance
        """
        # cache system information
        self._sys = system

    def compile_file(self, fileName):
        """
        Compile a file containing class definitions
        """
        f = open(fileName, "rt")
        text = f.read()
        f.close()
        self.compile_module(text)
        
    def compile_module(self, text):
        """
        Compile a module of class definitions
        """
        Lexer.input(text)
        
        # skip leading comments
        tok = Lexer.token()
        while tok.type == "DSTRING":
            tok = Lexer.token()
            
        # check for class definition
        superName = tok
        message = Lexer.token()
        klassName = Lexer.token()
        if (superName.type == "IDENT") and \
           (message.type == "MESSAGEARG") and (message.value == "subclass") and \
           (klassName.type == "IDENT"):
            print("%s -> %s" % (superName.value, klassName.value))
        
        # get definition body
        tok = Lexer.token()         # [
        if tok.type != "LBRACK":
            raise CompileError("missing [")
            
        # check for attributes
        tok = Lexer.token()         # <
        while (tok.type == "OPERATOR") and (tok.value == '<'):
            self.parse_attr()
            tok = Lexer.token()
        if tok.type != "IDENT":
            raise CompileError("expected ident")
            
        # check for class variables
        objName = tok.value         # name
        tok = Lexer.token()         # := or name
        if tok.type == "ASSIGN":
            self.compile_class_var(objName)
            
    def parse_attr(self):
        attrName = Lexer.token()    # name
        attrValue = Lexer.token()   # value
        tok = Lexer.token()         # >
        if (tok.type != "OPERATOR") or (tok.value != '>'):
            raise CompileError("missing >")
        print(attrName.value, ":", attrValue.value)
        
    def compile_class_var(self, name):
        value = Lexer.token()       # value
        print(name, ":=", value.value)
        