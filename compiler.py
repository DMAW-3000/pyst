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
        self._nil = system.o_nil
        
        # helpers
        self._cur_klass = None

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
            self.parse_class(superName.value, klassName.value)
            
    def parse_class(self, superName, klassName):
        # lookup class
        binding = self._sys.find_global(klassName)
        if is_nil(binding):
            raise CompileError("unknown class " + klassName)
        self._cur_klass = binding.value
        print("Compiling ", self._cur_klass.name)
        
        # get definition body
        tok = Lexer.token()         # [
        if tok.type != "LBRACK":
            raise CompileError("missing [")
            
        # check for attributes
        tok = Lexer.token()         # <
        while (tok.type == "OPERATOR") and (tok.value == '<'):
            self.parse_class_attr()
            tok = Lexer.token()
            
        # check for class variables
        if tok.type != "IDENT":
            raise CompileError("expected ident")
        while True:
            parse1 = tok.value         # name
            tok = Lexer.token()         # := or name
            if tok.type == "ASSIGN":
                self.parse_class_var(parse1)
                tok = Lexer.token()
            else:
                break
        
        # parse class methods
        if tok.type != "IDENT":
            raise CompileError("expected ident")
        while True:
            parse2 = tok.value
            if parse2 == "class":
                tok = Lexer.token()     # >>
                if tok != "RSHIFT":
                    CompileError("expected >>")
            break
        
    def parse_class_attr(self):
        attrName = Lexer.token()    # name
        attrValue = Lexer.token()   # value
        tok = Lexer.token()         # >
        if (tok.type != "OPERATOR") or (tok.value != '>'):
            raise CompileError("missing >")
        if attrName.value == "comment":
            self._cur_klass.comment = String.from_str(attrValue.value)
        elif attrName.value == "category":
            self._cur_klass.category = String.from_str(attrValue.value)
        
    def parse_class_var(self, varName):
        varValue = Lexer.token()       # value
        if varValue.value != 'nil':
            raise CompileError("expected nil")
        tok = Lexer.token()            # .
        if tok.type != "PERIOD":
            raise CompileError("missing .")
        self._sys.dict_print(self._cur_klass.classVariables, True)
        symObj = self._sys.symbol_find(varName)
        if is_nil(symObj):
            raise CompileError("class var %s not defined" % varName)
        binding = self._sys.dict_find(self._cur_klass.classVariables, symObj)
        if is_nil(binding):
            raise CompileError("class var %s not defined" % varName)
        
        