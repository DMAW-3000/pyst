"""
Smalltalk bootstrap compiler
"""

from st import *
from lexer import Lexer
from sparser import *

METH_NAMES = set(("isMetaclass", "postCopy", "isString", "isCharacterArray",
              "isSymbol", "isString", "isCharacter", "isNumber", "isFloat",
              "isInteger", "isSmallInteger", "isNamespace", "isClass", "dependencies",
              "isArray", "isBehavior", "yourself", "identityHash", "hash",
              "nextInstance", "isNil", "notNil", "ifNil:", "isCObject", "~=", "~~",
              "class", "primitiveFailed", "shouldNotImplement", "isMemberOf:",
              "subclassResponsibility", "notYetImplemented", "badReturnError",
              "noRunnableProcess", "userInterrupt", "isMetaClass", "validSize",
              "isMeta", "halt:", "inspect", "examine", "changed", "displayOn:",
              "respondsTo:", "become:", "becomeForward:", "postStore", "at:", "basicAt:",
              "reconstructOriginalObject", "dependencies:"))


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
    
    # reserved keywords
    _Keyword_Names = set(("self", "nil", "true", "false"))
    
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
        self._cur_local = None
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
        
    def parse_method(self, methName, argNames, parseBrack, opName):
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
                    argNames.append(tok.value)
                    tok = self._lex.token()
                else:
                    raise CompileError("bad message syntax")
                    
        # parse method name into a selector and argument names
        # create symbol for selector
        numArgs = len(argNames)
        methName = ":".join(methName)
        if (numArgs > 0) and not opName:
            methName += ":"
        methSym = self._sys.symbol_find_or_add(methName)
        print("Method:", methSym)
        print("Args:", argNames)
        
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
        
        # setup environment
        self._cur_local = argNames + tempNames
        self._cur_literal = []
        self._cur_bytes = bytearray()
            
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
            if methName in METH_NAMES:
                result = self.compile_str(stmtText)
                methObj.set_code(result)
                print(stmtText)
            else:
                print(">> Defer")
        else:
            # empty method definition
            methObj.set_code(self._Ret_Self_Bytes)
            
        # set method header values
        # TODO: set depth
        methObj.set_hdr(len(argNames), len(tempNames), 0)
        
        # create literals Array for method
        if len(self._cur_literal) > 0:
            methObj.literals = Array.from_seq(self._cur_literal)
            print("Literals:", len(self._cur_literal))
            self._sys.arr_print(methObj.literals)
            
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
        
    def compile_str(self, text):
        """
        Compile a python string of Smalltalk statements
        """
        # setup parser
        self._lex.input(text)
        
        # get list of statements
        result = self._parse(text, lexer = self._lex, debug = False)
        if not isinstance(result, ParseStatementList):
            raise CompileError("bad statements")
            
        # compile
        self.compile_statement_list(result.data)
        return self._cur_bytes
        
    def compile_statement_list(self, slist):
        """
        Compile a list of statments
        """
        # compile each statement
        for s in slist:
            self.compile_statement(s)
            
            # discard stack top if result not used
            if not isinstance(s, (ParseReturnStatement, ParseAssignStatement)):
                self.emit_bytes(B_POP_STACK_TOP, 0)
            
        # add ^self if no explicit return provided
        if not isinstance(slist[-1], ParseReturnStatement):
            self.emit_bytes(*self._Ret_Self_Bytes)
        
    def compile_statement(self, s):
        """
        Compile a single statement
        """
        if isinstance(s, ParseReturnStatement):
            self.compile_ret_statement(s.data)
        elif isinstance(s, ParseExecStatement):
            self.compile_exec_statement(s.data)
        elif isinstance(s, ParseAssignStatement):
            self.compile_assign_statement(s.var, s.data)
        else:
            raise CompileError("unknown statement type %s" % s)
        
    def compile_ret_statement(self, s):
        """
        Compile a ^ return statement
        """
        # generate statement
        self.compile_exec_statement(s.data)
        
        # add return instruction
        self.emit_bytes(B_RETURN_METHOD_STACK_TOP, 0)
        
    def compile_assign_statement(self, var, s):
        """
        Compile a := assignment statement
        """
        # check variable name
        if var in self._Keyword_Names:
            raise CompileError("assign to %s not allowed" % var)
        
        # generate value
        self.compile_exec_statement(s.data)
        
        # assign value
        idx = self.find_local(var)
        if idx is not None:
            self.emit_bytes(B_STORE_TEMPORARY_VARIABLE, idx)
        else:
            sym = self._sys.symbol_find_or_add(var)
            idx = self.add_literal(sym)
            self.emit_bytes(B_STORE_LIT_VARIABLE, idx)
        
    def compile_exec_statement(self, s):
        if isinstance(s, ParseUnaryMessage):
            self.compile_unary_message(s.recv, s.name)
        elif isinstance(s, ParseExprMessage):
            self.compile_expr_message(s.recv, s.name, s.send)
        elif isinstance(s, ParseArgumentMessage):
            self.compile_arg_message(s.recv, s.args)
        elif isinstance(s, ParseLiteral):
            self.compile_load_literal(s.value)
        else:
            raise CompileError("bad statement syntax %s" % s)
            
    def compile_unary_message(self, recv, name):
        if isinstance(recv, ParseUnaryMessage):
            self.compile_unary_message(recv.recv, recv.name)
        else:
            self.compile_load_literal(recv.value)
        sym = self._sys.symbol_find_or_add(name)
        idx = self.add_literal(sym)
        self.emit_bytes(B_PUSH_LIT_CONSTANT, idx, B_SEND, 0)
        
    def compile_expr_message(self, recv, name, send):
        self.compile_exec_statement(recv.data)
        sym = self._sys.symbol_find_or_add(name)
        idx = self.add_literal(sym)
        self.emit_bytes(B_PUSH_LIT_CONSTANT, idx)
        self.compile_exec_statement(send.data)
        self.emit_bytes(B_SEND, 1)
        
    def compile_arg_message(self, recv, args):
        if isinstance(recv, ParseUnaryMessage):
            self.compile_unary_message(recv.recv, recv.name)
        else:
            self.compile_load_literal(recv.value) 
        for a in args:
            sym = self._sys.symbol_find_or_add(a.name + ':')
            idx = self.add_literal(sym)
            self.emit_bytes(B_PUSH_LIT_CONSTANT, idx)
            self.compile_load_literal(a.value.value)
            self.emit_bytes(B_SEND, 1)
        
    def compile_load_literal(self, x):
        """
        Compile the code to load a literal value
        onto the stack.
        """
        # keyeord or variable name
        if isinstance(x, str):
            # keywords
            if x == "self":
                self.emit_bytes(B_PUSH_SELF, 0)
            elif x == "nil":
                idx = self.add_literal(self._nil)
                self.emit_bytes(B_PUSH_LIT_CONSTANT, idx)
            elif x == "true":
                idx = self.add_literal(self._true)
                self.emit_bytes(B_PUSH_LIT_CONSTANT, idx)
            elif x == "false":
                idx = self.add_literal(self._false)
                self.emit_bytes(B_PUSH_LIT_CONSTANT, idx)
            # variable name
            else:
                idx = self.find_local(x)
                if idx is not None:
                    self.emit_bytes(B_PUSH_TEMPORARY_VARIABLE, idx)
                else:
                    sym = self._sys.symbol_find_or_add(x)
                    idx = self.add_literal(sym)
                    self.emit_bytes(B_PUSH_LIT_VARIABLE, idx)
        # small integer
        # TODO: check for overflow of int type
        elif isinstance(x, int):
            idx = self.add_literal(x)
            self.emit_bytes(B_PUSH_LIT_CONSTANT, idx)
        # unknown type
        else:
            raise CompileError("unknown literal type %s" % x)
                
    def add_literal(self, x):
        """
        Add a new literal reference to the current context
        """
        try:
            return self._cur_literal.index(x)
        except ValueError:
            self._cur_literal.append(x)
            return len(self._cur_literal) - 1
            
    def emit_bytes(self, *bc):
        """
        Append the bytecodes to the current code block
        """
        self._cur_bytes.extend((bc))
        
    def find_local(self, name):
        """
        Find the index of a argument or temporary
        variable name, or None if not local.
        """
        try:
            idx = self._cur_local.index(name)
        except:
            idx = None
        return idx

            

        