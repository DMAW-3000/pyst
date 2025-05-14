"""
Smalltalk bootstrap compiler
"""

from st import *
from lexer import Lexer
from sparser import *


class CompileError(Exception): 
    """
    Signal a compilation error
    """
    pass
    

class Compile(object):
    """
    The bootstrap compiler
    """
    
    # the default code for pushing self and returning from method
    _Ret_Self_Bytes = bytearray((B_PUSH_SELF, 0, B_RETURN_METHOD_STACK_TOP, 0))
    
    def __init__(self, system):
        """
        Create a blank compiler instance
        """
        global Lexer, Parser
        
        # cache system information
        self._sys = system
        self._nil = system.o_nil
        self._true = system.o_true
        self._false = system.o_false
        
        # the lexer and parser
        self._lex = Lexer
        self._parse = Parser.parse
        
        # helpers
        self._cur_klass = None
        self._cur_meth = None
        self._cur_arg = None
        self._cur_temp = None
        self._cur_literal = None
        self._cur_bytes = None
        
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
        self._lex.input(text)
        
        # skip leading comments
        tok = self._lex.token()
        while tok.type == "DSTRING":
            tok = self._lex.token()
            
        # check for class definition
        superName = tok
        message = self._lex.token()
        klassName = self._lex.token()
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
        tok = self._lex.token()         # [
        if tok.type != "LBRACK":
            raise CompileError("missing [")
            
        # check for attributes
        tok = self._lex.token()         # <
        while (tok.type == "OPERATOR") and (tok.value == '<'):
            self.parse_class_attr()
            tok = self._lex.token()
            
        parse1 = None
        parse2 = None
        parse3 = None
            
        # check for class variables
        if (tok.type != "IDENT") and (tok.type != "OPERATOR"):
            raise CompileError("expected ident or operator")
        while True:
            parse1 = tok         # name
            tok = self._lex.token()         # := or name
            if tok.type == "ASSIGN":
                self.parse_class_var(parse1.value)
                tok = self._lex.token()
            else:
                parse2 = tok
                break
        
        # parse class methods
        while True:
            if parse1 is None:
                parse1 = self._lex.token()
            if parse2 is None:
                parse2 = self._lex.token()
            if (parse1 is None) or (parse2 is None):
                break
            if (parse2.type == "IDENT") and (parse2.value == "class"):
                tok = self._lex.token()     # >>
                if (tok.type != "OPERATOR") or (tok.value != ">>"):
                    CompileError("expected >>")
                self.parse_method([], [], True, False)
                parse1 = None
                parse2 = None
                continue
            elif (parse1.type == "OPERATOR") and (parse2.type == "IDENT"):
                self.parse_method([parse1.value], [parse2.value], True, True)
                parse1 = None
                parse2 = None
                continue
            elif (parse1.type == "MESSAGEARG") and (parse2.type == "IDENT"):
                self.parse_method([parse1.value], [parse2.value], True, False)
                parse1 = None
                parse2 = None
                continue
            elif (parse1.type == "IDENT") and (parse2.type == "LBRACK"):
                self.parse_method([parse1.value], [], False, False)
                parse1 = None
                parse2 = None
            else:
                raise CompileError("bad method syntax")
        
    def parse_class_attr(self):
        """
        Parse a class attribute definition
        """
        attrName = self._lex.token()    # name
        attrValue = self._lex.token()   # value
        tok = self._lex.token()         # >
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
        varValue = self._lex.token()       # value
        if varValue.value != 'nil':
            raise CompileError("expected nil")
        tok = self._lex.token()            # .
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
        
    def parse_method(self, methName, argName, parseBrack, opName):
        """
        Parse the definition of a method
        """
        #get remainder of method name
        if parseBrack:
            # parse method arguments
            tok = self._lex.token()             # ident or ident:
            while tok.type != "LBRACK":
                if tok.type == "IDENT":
                    methName.append(tok.value)
                    tok = self._lex.token()
                elif tok.type == "MESSAGEARG":
                    methName.append(tok.value)
                    tok = self._lex.token()     # ident
                    if tok.type != "IDENT":
                        raise CompileError("expected ident")
                    argName.append(tok.value)
                    tok = self._lex.token()
                else:
                    raise CompileError("bad message syntax")
                    
        # parse method name into a selector and argument names
        # create symbol for selector
        numArgs = len(argName)
        methName = ":".join(methName)
        if (numArgs > 0) and not opName:
            methName += ":"
        methSym = self._sys.symbol_find_or_add(methName)
        print("Method:", methSym)
        print("Args:", argName)
        
        # create Method and MethodInfo objects
        self._cur_meth = methObj = CompiledMethod()
        methObj.descriptor = MethodInfo(self._cur_klass)
        methObj.descriptor.selector = methSym
        
        # skip any comment
        tok = self._lex.token()
        while tok.type == "DSTRING":
            tok = self._lex.token()
            
        # parse method attributes
        while (tok.type == "OPERATOR") and (tok.value == '<'):
            self.parse_method_attr()
            tok = self._lex.token()
            
        # skip more comment
        while tok.type == "DSTRING":
            tok = self._lex.token()
            
        # parse method temporary variables
        if tok.type == "PIPE":
            tempNames = self.parse_method_temps()
            tok = self._lex.token()
        else:
            tempNames = []
        print("Temps:", tempNames)
            
        # scan method statements
        # look for trailing ']'
        # strip out double quote comments
        pos = 0
        remainder = self._lex.lexdata[self._lex.lexpos:]
        if tok.type != "RBRACK":
            stmtText = tok.value
            brackCount = 1
            comment = False
            c = remainder[pos]
            while brackCount > 0:
                if c == '\"':
                    comment = not comment
                elif c == ']':
                    brackCount -= 1
                    if (brackCount > 0) and (not comment):
                        stmtText += c
                elif c == '[':
                    brackCount += 1
                    if not comment:
                        stmtText += c
                else:
                    if not comment:
                        stmtText += c
                pos += 1
                c = remainder[pos]
            #methObj.descriptor.sourceCode = String.from_str(stmtText)
            result = self.compile_statements(stmtText, argName, tempNames, [])
            methObj.set_code(result)
        else:
            # empty method definition
            methObj.set_code(self._Ret_Self_Bytes)
            
        byteCode = methObj.get_code()
        print("Bytecodes:", len(byteCode))
        self._sys.dis_bytecode(byteCode)
        print()
            
        # setup lexer to continue parsing module text
        self._lex.input(remainder[pos:])
          
    def parse_method_attr(self):
        """
        Parse a method attribute definition
        """
        attrName = self._lex.token()    # name
        attrValue = self._lex.token()   # value
        tok = self._lex.token()         # >
        if (tok.type != "OPERATOR") or (tok.value != '>'):
            raise CompileError("missing >")
        if attrName.value == "category":
            self._cur_meth.descriptor.category = String.from_str(attrValue.value)
        elif attrName.value == "primitive":
            print("Primitive:", attrValue.value)
            
    def parse_method_temps(self):
        """
        Parse a list of method temporary names
        """
        tempNames = []
        tok = self._lex.token()
        while tok.type != "PIPE":
            if tok.type != "IDENT":
                raise CompileError("expected ident")
            tempNames.append(tok.value)
            tok = self._lex.token()
        return tempNames
        
    def compile_statements(self, text, argNames, tempNames, literals):
        """
        Compile a list of Smalltalk statements
        """
        # setup environment
        self._cur_arg = argNames
        self._cur_temp = tempNames
        self._cur_literal = literals
        self._cur_bytes = bytearray()
        
        # setup parser
        text = "^nil"
        self._lex.input(text)
        result = self._parse(text, lexer = self._lex, debug = False)
        self.compile_load_primitive(result.data.data.data)
        if isinstance(result, ParseReturnStatement):
            self._cur_bytes.extend((B_RETURN_METHOD_STACK_TOP, 0))
        print(literals)
        print(text)
        return self._cur_bytes
        
    def compile_load_primitive(self, x):
        if isinstance(x, str):
            if x == "nil":
                idx = self.add_literal(self._nil)
                self._cur_bytes.extend((B_PUSH_LIT_CONSTANT, idx))
            elif x == "true":
                idx = self.add_literal(self._true)
                self._cur_bytes.extend((B_PUSH_LIT_CONSTANT, idx))
            elif x == "false":
                idx = self.add_literal(self._false)
                self._cur_bytes.extend((B_PUSH_LIT_CONSTANT, idx))
            elif x == "self":
                self._cur_bytes.extend((B_PUSH_SELF, 0))
                
    def add_literal(self, x):
        if x in self._cur_literal:
            return self._cur_literal.index(x)
        self._cur_literal.append(x)
        return len(self._cur_literal) - 1
            

        