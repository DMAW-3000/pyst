"""
Smalltalk bootstrap compiler
"""

from st import *
from lexer import Lexer


class CompileError(Exception): 
    """
    Signal a compilation error
    """
    pass
    

class Compile(object):
    """
    The bootstrap compiler
    """
    def __init__(self, system):
        """
        Create a blank compiler instance
        """
        # cache system information
        self._sys = system
        self._nil = system.o_nil
        
        # helpers
        self._cur_klass = None
        self._cur_meth = None

    def parse_file(self, fileName):
        """
        Compile a file containing class definitions
        """
        f = open(fileName, "rt")
        text = f.read()
        f.close()
        self.parse_module(text)
        
    def parse_module(self, text):
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
        """
        Parse the definition of a class
        """
        # lookup class
        binding = self._sys.find_global(klassName)
        if is_nil(binding):
            raise CompileError("unknown class " + klassName)
        self._cur_klass = binding.value
        print("Compiling class", self._cur_klass.name)
        
        # get definition body
        tok = Lexer.token()         # [
        if tok.type != "LBRACK":
            raise CompileError("missing [")
            
        # check for attributes
        tok = Lexer.token()         # <
        while (tok.type == "OPERATOR") and (tok.value == '<'):
            self.parse_class_attr()
            tok = Lexer.token()
            
        parse1 = None
        parse2 = None
        parse3 = None
            
        # check for class variables
        if (tok.type != "IDENT") and (tok.type != "OPERATOR"):
            raise CompileError("expected ident or operator")
        while True:
            parse1 = tok         # name
            tok = Lexer.token()         # := or name
            if tok.type == "ASSIGN":
                self.parse_class_var(parse1.value)
                tok = Lexer.token()
            else:
                parse2 = tok
                break
        
        # parse class methods
        while True:
            if parse1 is None:
                parse1 = Lexer.token()
            if parse2 is None:
                parse2 = Lexer.token()
            if (parse1 is None) or (parse2 is None):
                break
            if (parse2.type == "IDENT") and (parse2.value == "class"):
                tok = Lexer.token()     # >>
                if tok != "RSHIFT":
                    CompileError("expected >>")
                self.parse_method([], [], True)
                parse1 = None
                parse2 = None
                continue
            elif (parse1.type == "OPERATOR") and (parse2.type == "IDENT"):
                self.parse_method([parse1.value], [parse2.value], True)
                parse1 = None
                parse2 = None
                continue
            elif (parse1.type == "MESSAGEARG") and (parse2.type == "IDENT"):
                self.parse_method([parse1.value], [parse2.value], True)
                parse1 = None
                parse2 = None
                continue
            elif (parse1.type == "IDENT") and (parse2.type == "LBRACK"):
                self.parse_method([parse1.value], [], False)
                parse1 = None
                parse2 = None
            else:
                print(parse1, parse2)
                break
        
    def parse_class_attr(self):
        """
        Parse a class attribute definition
        """
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
        """
        Parse the initialization statement for a class variable
        """
        varValue = Lexer.token()       # value
        if varValue.value != 'nil':
            raise CompileError("expected nil")
        tok = Lexer.token()            # .
        if tok.type != "PERIOD":
            raise CompileError("missing .")
        symObj = self._sys.symbol_find(varName)
        if is_nil(symObj):
            raise CompileError("class var %s not defined" % varName)
        varDict = self._cur_klass.classVariables
        assoc = self._sys.dict_find(varDict, symObj)
        if is_nil(assoc):
            raise CompileError("class var %s not defined" % varName)
        varObj = self._nil      # just set to NIL for now, need to parse statement
        self._sys.dict_add(varDict, symObj, varObj)
        print("Class Variable:", symObj, varObj)
        
    def parse_method(self, methName, argName, parseBrack):
        """
        Parse the definition of a method
        """
        if parseBrack:
            # parse method arguments
            tok = Lexer.token()             # ident or ident:
            while tok.type != "LBRACK":
                if tok.type == "IDENT":
                    methName.append(tok.value)
                    tok = Lexer.token()
                elif tok.type == "MESSAGEARG":
                    methName.append(tok.value)
                    tok = Lexer.token()     # ident
                    if tok.type != "IDENT":
                        raise CompileError("expected ident")
                    argName.append(tok.value)
                    tok = Lexer.token()
        numArgs = len(argName)
        methName = ":".join(methName)
        if numArgs > 0:
            methName += ":"
        print("Method:", methName)
        print("Args:", argName)
        
        
        # create Method and MethodInfo objects
        self._cur_meth = methObj = CompiledMethod()
        methObj.descriptor = MethodInfo(self._cur_klass)
        
        # skip any comment
        tok = Lexer.token()
        while tok.type == "DSTRING":
            tok = Lexer.token()
            
        # parse method attributes
        while (tok.type == "OPERATOR") and (tok.value == '<'):
            self.parse_method_attr()
            tok = Lexer.token()
            
        # parse method temporary variables
        if tok.type == "PIPE":
            tempNames = self.parse_method_temps()
            tok = Lexer.token()
        else:
            tempNames = []
        print("Temps:", tempNames)
            
        # scan method statements
        # look for trailing ']'
        if tok.type != "RBRACK":
            stmtText = tok.value
            brackCount = 1
            c = Lexer.lexdata[Lexer.lexpos]
            while brackCount > 0:
                if c == ']':
                    brackCount -= 1
                    if brackCount > 0:
                        stmtText += c
                elif c == '[':
                    brackCount += 1
                    stmtText += c
                else:
                    stmtText += c
                Lexer.lexpos += 1
                c = Lexer.lexdata[Lexer.lexpos]
            #methObj.descriptor.sourceCode = String.from_str(stmtText)
            print(stmtText)
        Lexer.input(Lexer.lexdata[Lexer.lexpos:])
          
    def parse_method_attr(self):
        """
        Parse a method attribute definition
        """
        attrName = Lexer.token()    # name
        attrValue = Lexer.token()   # value
        tok = Lexer.token()         # >
        if (tok.type != "OPERATOR") or (tok.value != '>'):
            raise CompileError("missing >")
        if attrName.value == "category":
            self._cur_meth.descriptor.category = String.from_str(attrValue.value)
            
    def parse_method_temps(self):
        """
        Parse a list of method temporary names
        """
        tempNames = []
        tok = Lexer.token()
        while tok.type != "PIPE":
            if tok.type != "IDENT":
                raise CompileError("expected ident")
            tempNames.append(tok.value)
            tok = Lexer.token()
        return tempNames
                
        
            
        
        