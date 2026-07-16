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
    
    # reserved keywords
    _Keyword_Names = set(("self", "nil", "true", "false", "super", "thisContext"))
    
    # mapping for unary special messages
    _Special_Unary = {
        "value"     : B_VALUE_SPECIAL,
        "size"      : B_SIZE_SPECIAL,
        "isNil"     : B_IS_NIL_SPECIAL,
        "notNil"    : B_NOT_NIL_SPECIAL,
    }
    
    def __init__(self, system, verbose):
        """
        Create a blank compiler instance
        """
        global Lexer, Parser
        
        # cache system information
        self._sys = system
        self._verbose = verbose
        self._nil = system.o_nil
        self._true = system.o_true
        self._false = system.o_false
        bind = system.find_global("VMPrimitives")
        if bind.is_nil():
            raise NameError("missing global VMPrimitives")
        self._prim_dict = bind.value
        
        # the lexer and parser
        self._lex = Lexer
        self._parse = Parser(self._lex)
        
        # helpers
        self._cur_klass = None
        self._cur_inst_var = []
        self._cur_meth = None
        self._cur_local = None
        self._cur_literal = None
        self._cur_bytes = None
        self._cur_depth = None
        self._max_depth = None
        self._ctx_stack = []
        
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
        if binding.is_nil():
            raise CompileError("unknown class " + klassName)
        self._cur_klass = binding.value
        self._cur_inst_var.clear()
        if self._verbose:
            print("Compiling class", self._cur_klass.name)
        
        # get definition body
        tok = self._lex.token()         # [
        if tok.type != "LBRACK":
            raise CompileError("missing [ " + str(self._cur_meth))
        tok = self._lex.token()
            
        # check for instance variables
        if (tok.type == "OPERATOR") and (tok.value == '|'):
            self.parse_inst_vars()
            tok = self._lex.token()
        if not self._cur_klass.instanceVariables.is_nil():
            for var in self._cur_klass.instanceVariables:
                self._cur_inst_var.append(var.to_str())
        if self._verbose:
            print("Instance Variables: ", self._cur_inst_var)
            
        # check for attributes
        while (tok.type == "OPERATOR") and (tok.value == '<'):
            self.parse_class_attr()
            tok = self._lex.token()
            
        parse1 = None
        parse2 = None
        parse3 = None
            
        # check for class variables
        if (tok.type != "IDENT") and (tok.type != "OPERATOR") and (tok.type != "MESSAGEARG"):
            raise CompileError("expected ident or operator " + str(self._cur_meth))
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
        if self._verbose:
            print()
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
                self.parse_method([], [], True, False, True)
                parse1 = None
                parse2 = None
                continue
            elif (parse1.type == "OPERATOR") and (parse2.type == "IDENT"):
                self.parse_method([parse1.value], [parse2.value], True, True, False)
                parse1 = None
                parse2 = None
                continue
            elif (parse1.type == "MESSAGEARG") and (parse2.type == "IDENT"):
                self.parse_method([parse1.value], [parse2.value], True, False, False)
                parse1 = None
                parse2 = None
                continue
            elif (parse1.type == "IDENT") and (parse2.type == "LBRACK"):
                self.parse_method([parse1.value], [], False, False, False)
                parse1 = None
                parse2 = None
            else:
                raise CompileError("bad method syntax")
        
        if not self._cur_klass.classVariables.is_nil():
            if self._verbose:
                print("Class Var Dict:")
                self._sys.dict_print(self._cur_klass.classVariables)
                print()
        
        if (not self._cur_klass.get_class().is_nil()) and (not self._cur_klass.get_class().methodDictionary.is_nil()):
            if self._verbose:
                print("Class Meth Dict:")
                self._sys.identdict_print(self._cur_klass.get_class().methodDictionary)
                print()
        
        if not self._cur_klass.methodDictionary.is_nil():
            if self._verbose:
                print("Inst Meth Dict:")
                self._sys.identdict_print(self._cur_klass.methodDictionary)
                print()
                
    def parse_class_attr(self):
        """
        Parse a class attribute definition
        """
        attrName = self._lex.token()    # name
        attrValue = self._lex.token()   # value
        tok = self._lex.token()         # >
        if (tok.type != "OPERATOR") or (tok.value != '>'):
            raise CompileError("attr missing >")
        if attrName.value == "comment":
            self._cur_klass.comment = String.from_str(attrValue.value)
        elif attrName.value == "category":
            self._cur_klass.category = String.from_str(attrValue.value)
            
    def parse_inst_vars(self):
        """
        Parse the class definition instance variables name list
        """
        tok = self._lex.token()
        while tok.type == "IDENT":
            tok = self._lex.token()
        if (not tok.type == "OPERATOR") or (not tok.value == '|'):
            raise CompileError("inst vars missing |")
        
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
        if symObj.is_nil():
            raise CompileError("class var %s not defined" % varName)
        varDict = self._cur_klass.classVariables
        assoc = self._sys.dict_find(varDict, symObj)
        if assoc.is_nil():
            raise CompileError("class var %s not defined" % varName)
        
    def parse_method(self, methName, argNames, parseBrack, opName, klassMeth):
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
                        raise CompileError("expected ident " + str(self._cur_meth))
                    argNames.append(tok.value)
                    tok = self._lex.token()
                else:
                    raise CompileError("bad message syntax " + str(self._cur_meth))
                    
        # parse method name into a selector and argument names
        # create symbol for selector
        numArgs = len(argNames)
        methName = ":".join(methName)
        if (numArgs > 0) and not opName:
            methName += ":"
        methSym = self._sys.symbol_find_or_add(methName)
        if self._verbose:
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
        primId = 0
        while (tok.type == "OPERATOR") and (tok.value == '<'):
            value = self.parse_method_attr()
            if value is not None:
                primId = value
            tok = self._lex.token()
        if self._verbose:
            print("Primitive:", primId)
            
        # skip more comment
        while tok.type == "DSTRING":
            tok = self._lex.token()
            
        # parse method temporary variables
        if (tok.type == "OPERATOR") and (tok.value == '|'):
            tempNames = self.parse_method_temps()
            tok = self._lex.token()
        else:
            tempNames = []
        if self._verbose:
            print("Temps:", tempNames)
        
        # setup environment
        self._cur_local = argNames + tempNames
        self._cur_literal = []
        self._cur_bytes = bytearray()
        self._cur_depth = self._max_depth = 0
            
        # scan method statements
        # look for trailing ']'
        # strip out double quote comments
        pos = 0
        remainder = self._lex.lexdata[self._lex.lexpos:]
        if tok.type != "RBRACK":
            if tok.type == "CHARACTER":
                stmtText = "$" + tok.value
            elif tok.type == "SSTRING":
                stmtText = "\'" + tok.value + "\'"
            elif tok.type == "DSTRING":
                stmtText = ""
            elif tok.type == "SYMBOL":
                stmtText = "#" + tok.value
            else:
                stmtText = str(tok.value)
            if tok.type == "LBRACK":
                brackCount = 2
            else:
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
            result = self.compile_str(stmtText)
            methObj.set_code(result)
            
        else:
            # empty method definition
            methObj.set_code(self._Ret_Self_Bytes)
            self._max_depth = 1
            
        # set method header values
        methObj.set_hdr(len(argNames), 
                        len(tempNames), 
                        self._max_depth,
                        primId)
        
        # create literals Array for method
        if len(self._cur_literal) > 0:
            methObj.literals = Array.from_seq(self._cur_literal)
            methObj.literals.make_readonly()
            if self._verbose:
                print()
                print("Method Literals:", len(self._cur_literal))
                self._sys.arr_print(methObj.literals)
            
        # add method to class dictionary
        # or metaclass dictionary if class method
        if klassMeth:
            methDict = self._cur_klass.get_class().methodDictionary
            if methDict.is_nil():
                self._cur_klass.get_class().methodDictionary = methDict = MethodDictionary.new_n(32)
        else:
            methDict = self._cur_klass.methodDictionary
            if methDict.is_nil():
                self._cur_klass.methodDictionary = methDict = MethodDictionary.new_n(32)
        self._sys.identdict_add(methDict, methSym, methObj)
            
        byteCode = methObj.get_code()
        if self._verbose:
            print("Method Bytecodes:", len(byteCode))
            self._sys.dis_bytecode(byteCode)
            print("Depth:", self._max_depth)
            print()
            
        # setup lexer to continue parsing module text
        self._lex.input(remainder[pos:])
          
    def parse_method_attr(self):
        """
        Parse a method attribute definition.  Return int ID
        of primitive if present, None otherwise.
        """
        primId = None
        attrName = self._lex.token()    # name
        attrValue = self._lex.token()   # value
        tok = self._lex.token()         # >
        if (tok.type != "OPERATOR") or (tok.value != '>'):
            raise CompileError("missing > " + str(self._cur_meth))
        if attrName.value == "category":
            self._cur_meth.descriptor.category = String.from_str(attrValue.value)
        elif attrName.value == "primitive":
            sym = self._sys.symbol_find(attrValue.value)
            if not sym.is_nil():
                assoc = self._sys.dict_find(self._prim_dict, sym)
                if not assoc.is_nil():
                    primId = assoc.value
        return primId
            
    def parse_method_temps(self):
        """
        Parse a list of method temporary names
        """
        tempNames = []
        tok = self._lex.token()
        while (tok.type != "OPERATOR") and (tok.value != '|'):
            if tok.type != "IDENT":
                raise CompileError("expected ident "  + str(self._cur_meth))
            tempNames.append(tok.value)
            tok = self._lex.token()
        return tempNames
        
    def compile_str(self, text):
        """
        Compile a python string of Smalltalk statements
        """
        # setup parser
        if self._verbose:
            print(text)
        self._lex.input(text)
        self._parse.reset()
        
        # get list of statements
        result = self._parse.parse_statements()
        if not isinstance(result, ParseStatementList):
            raise CompileError("bad statements "  + str(self._cur_meth))
            
        # compile
        self.compile_statement_list(result.data, False)
        return self._cur_bytes
        
    def compile_statement_list(self, slist, isBlk):
        """
        Compile a list of statments
        """
        # compile each statement
        for s in slist:
            notLast = slist.index(s) != (len(slist) - 1)
            self.compile_statement(s, isBlk and not notLast)
            
            # discard stack top if result not used
            # unless it is not the last statement of a block
            if not isBlk:
                if not isinstance(s, (ParseReturnStatement, ParseAssignStatement)):
                    self.emit_bytes(-1, B_POP_STACK_TOP, 0)
            else:
                if notLast:
                    if not isinstance(s, (ParseReturnStatement, ParseAssignStatement)):
                        self.emit_bytes(-1, B_POP_STACK_TOP, 0)
            
        # add ^self if no explicit return provided
        # and this is not a block context
        if not isBlk:
            if not isinstance(slist[-1], ParseReturnStatement):
                self.emit_bytes(0, *self._Ret_Self_Bytes)
                
        # if it is a block context, add return if lasst
        # statement is not a method return
        else:
            if not isinstance(slist[-1], ParseReturnStatement):
                self.emit_bytes(-1, B_RETURN_CONTEXT_STACK_TOP, 0)
        
    def compile_statement(self, s, nested):
        """
        Compile a single statement
        """
        if isinstance(s, ParseReturnStatement):
            self.compile_ret_statement(s.data)
        elif isinstance(s, ParseExecStatement):
            self.compile_exec_statement(s.data)
        elif isinstance(s, ParseAssignStatement):
            self.compile_assign_statement(s.vlist, s.data, nested)
        else:
            raise CompileError("unknown statement type %s" % s)
        
    def compile_ret_statement(self, s):
        """
        Compile a ^ return statement
        """
        # generate statement
        self.compile_exec_statement(s.data)
        
        # add return instruction
        self.emit_bytes(-1, B_RETURN_METHOD_STACK_TOP, 0)
        
    def compile_assign_statement(self, vlist, s, nested):
        """
        Compile a := assignment statement
        """
        # process the assign list
        for var in vlist:
        
            # check variable name
            varName = var.value
            if varName in self._Keyword_Names:
                raise CompileError("assign to %s not allowed" % var)
        
            # generate value
            if var is vlist[0]:
                self.compile_exec_statement(s.data)
                
            # duplicate value for chained assign
            if var is not vlist[-1]:
                self.emit_bytes(1, B_DUP_STACK_TOP, 0)
        
            # if this is a nested assign, duplicate the value
            # since the store will consume a single copy
            if nested and (var is vlist[-1]):
                self.emit_bytes(1, B_DUP_STACK_TOP, 0)
        
            # assign value
            # look in locals first
            idx, scope = self.find_local(varName)
            if idx is not None:
                if scope == 0:
                    # current context
                    self.emit_bytes(-1, B_STORE_TEMPORARY_VARIABLE, idx)
                else:
                    # parent context
                    self.emit_bytes(-1, B_STORE_OUTER_TEMP, idx, B_EXT_BYTE, scope - 1)
            else:
                # look in instance variables
                try:
                    idx = self._cur_inst_var.index(varName)
                    self.emit_bytes(-1, B_STORE_RECEIVER_VARIABLE, idx)
                except ValueError:
                    # variable is global
                    sym = self._sys.symbol_find_or_add(varName)
                    idx = self.add_literal(sym)
                    self.emit_bytes(-1, B_STORE_LIT_VARIABLE, idx)
        
    def compile_exec_statement(self, s):
        """
        Compile a plain statement
        """
        if isinstance(s, ParseUnaryMessage):
            self.compile_unary_message(s.recv, s.name, s.sup)
        elif isinstance(s, ParseExprMessage):
            self.compile_expr_message(s.recv, s.name, s.send, s.sup)
        elif isinstance(s, ParseArgumentMessage):
            self.compile_arg_message(s.recv, s.args, s.sup)
        elif isinstance(s, ParseCascadeMessage):
            self.compile_cas_message(s.recv, s.mlist, s.sup)
        elif isinstance(s, ParseLiteral):
            self.compile_load_literal(s.value)
        elif isinstance(s, ParseExecStatement):
            self.compile_exec_statement(s.data)
        elif isinstance(s, ParseAssignStatement):
            self.compile_assign_statement(s.vlist, s.data, True)
        else:
            pass
            #raise CompileError("bad statement syntax %s" % s)
            
    def compile_unary_message(self, recv, name, isSuper):
        """
        Compile sending a unary message
        """
        if isinstance(recv, ParseUnaryMessage):
            self.compile_unary_message(recv.recv, recv.name)
        elif isinstance(recv, ParseExecStatement):
            self.compile_exec_statement(recv)
        else:
            raise CompileError("unary recv:", recv)
            
        sym = self._sys.symbol_find_or_add(name)
        if (name in self._Special_Unary) and not isSuper:
            self.emit_bytes(-1, self._Special_Unary[name], 0)
        else:
            idx = self.add_literal(sym)
            self.emit_bytes(1, B_PUSH_LIT_CONSTANT, idx)
            if isSuper:
                self.emit_bytes(-1, B_SEND_SUPER, 0)
            else:
                self.emit_bytes(-1, B_SEND, 0)
        
    def compile_expr_message(self, recv, name, send, isSuper):
        """
        Compile sending a binary expression message
        """
        self.compile_exec_statement(recv.data)
        sym = self._sys.symbol_find_or_add(name)
        idx = self.add_literal(sym)
        self.emit_bytes(1, B_PUSH_LIT_CONSTANT, idx)
        self.compile_exec_statement(send.data)
        if isSuper:
            self.emit_bytes(-2, B_SEND_SUPER, 1)
        else:
            self.emit_bytes(-2, B_SEND, 1)
        
    def compile_arg_message(self, recv, args, isSuper):
        """
        Comple sending a message with named arguments
        """
        # get receiver
        self.compile_exec_statement(recv.data)

        # build up argument names and value
        argNames = []
        argValues = []
        numArgs = len(args)
        for a in args:
            argNames.append(a.name)
            argValues.append(a.value)
            
        # push selector
        selName = ":".join(argNames) + ":"
        sym = self._sys.symbol_find_or_add(selName)
        idx = self.add_literal(sym)
        self.emit_bytes(1, B_PUSH_LIT_CONSTANT, idx)
        
        # get and push argument values
        for a in argValues:
            if isinstance(a, ParseLiteral):
                self.compile_load_literal(a.value)
            elif isinstance(a, ParseUnaryMessage):
                self.compile_unary_message(a.recv, a.name, a.sup)
            elif isinstance(a, ParseExecStatement):
                self.compile_exec_statement(a.data)
            else:
                raise CompileError("bad message argument syntax "  + str(self._cur_meth))
            
        # send message
        if isSuper:
            self.emit_bytes(-1 - numArgs, B_SEND_SUPER, numArgs)
        else:
            self.emit_bytes(-1 - numArgs, B_SEND, numArgs)
        
    def compile_cas_message(self, recv, mlist, isSuper):
        """
        Compile a cascade list of messages
        """
        # load the receiver
        self.compile_exec_statement(recv.data)
        
        # compile each message
        # reload receiver each time except last
        # remove reply each time except last
        for msg in mlist:
            if msg is not mlist[-1]:
                self.emit_bytes(1, B_DUP_STACK_TOP, 0)
            self.compile_exec_statement(msg.data)
            if msg is not mlist[-1]:
                self.emit_bytes(-1, B_POP_STACK_TOP, 0)
        
    def compile_load_literal(self, x):
        """
        Compile the code to load a literal value
        onto the stack.
        """
        global Int_Max
        
        # empty
        if x is None:
            return 
            
        # keyeord or variable name
        if isinstance(x, str):
            # keywords
            if x == "self":
                self.emit_bytes(1, B_PUSH_SELF, 0)
            elif x == "nil":
                idx = self.add_literal(self._nil)
                self.emit_bytes(1, B_PUSH_LIT_CONSTANT, idx)
            elif x == "true":
                idx = self.add_literal(self._true)
                self.emit_bytes(1, B_PUSH_LIT_CONSTANT, idx)
            elif x == "false":
                idx = self.add_literal(self._false)
                self.emit_bytes(1, B_PUSH_LIT_CONSTANT, idx)
            elif x == "super":
                self.emit_bytes(1, B_PUSH_SELF, 0)
            elif x == "thisContext":
                self.emit_bytes(1, B_PUSH_SPECIAL, 0)
            # variable name
            else:
                self.compile_push_var(x)
                    
        # small integer
        elif isinstance(x, int):
            if abs(x) > Int_Max:
                raise CompileError("integer value %d too large" % x)
            # optimize with push direct if value is small enough
            if (x >= 0) and (x < 256):
                self.emit_bytes(1, B_PUSH_INTEGER, x)
            else:
                idx = self.add_literal(x)
                self.emit_bytes(1, B_PUSH_LIT_CONSTANT, idx)
            
        # float constant
        elif isinstance(x, float):
            idx = self.add_literal(x)
            self.emit_bytes(1, B_PUSH_LIT_CONSTANT, idx)
            
        # symbol constant
        elif isinstance(x, ParseLiteralSymbol):
            sym = self._sys.symbol_find_or_add(x.value)
            idx = self.add_literal(sym)
            self.emit_bytes(1, B_PUSH_LIT_CONSTANT, idx)
            
        # string constant
        elif isinstance(x, ParseLiteralString):
            idx = self.add_literal(String.from_str(x.value))
            self.emit_bytes(1, B_PUSH_LIT_CONSTANT, idx)
            
        # block closure
        elif isinstance(x, ParseLiteralBlock):
            self.compile_blk_closure(x.value, x.args, x.temps)
            
        # literal character
        elif isinstance(x, ParseLiteralChar):
            idx = self.add_literal(self._sys.o_char[ord(x.value)])
            self.emit_bytes(1, B_PUSH_LIT_CONSTANT, idx)
            
        # literal array
        elif isinstance(x, ParseLiteralArray):
            idx = self.add_literal(self.build_array(x.value))
            self.emit_bytes(1, B_PUSH_LIT_CONSTANT, idx)
            
        # literal bytearray
        elif isinstance(x, ParseLiteralBytearray):
            idx = self.add_literal(self.build_bytearray(x.value))
            self.emit_bytes(1, B_PUSH_LIT_CONSTANT, idx)
            
        # unknown type
        else:
            raise CompileError("unknown literal type %s" % x)
   
    def compile_push_var(self, x):
        """
        Compile a variable push
        """
        # look in locals
        idx, scope = self.find_local(x)
        if idx is not None:
            if scope == 0:
                # this context
                self.emit_bytes(1, B_PUSH_TEMPORARY_VARIABLE, idx)
            else:
                # parent context
                self.emit_bytes(1, B_PUSH_OUTER_TEMP, idx, B_EXT_BYTE, scope - 1)
       
        # look in instance variables
        else:
            try:
                idx = self._cur_inst_var.index(x)
                self.emit_bytes(1, B_PUSH_RECEIVER_VARIABLE, idx)
            except ValueError:
                # variable is global
                sym = self._sys.symbol_find_or_add(x)
                idx = self.add_literal(sym)
                self.emit_bytes(1, B_PUSH_LIT_VARIABLE, idx)
            
    def compile_blk_closure(self, s, args, temps):
        """
        Compile a block closure expresion
        """
        # save current context state and prepare new
        self.context_push()
        self._cur_local.extend(args)
        self._cur_local.extend(temps)
        
        # compile the block statements
        # check for empty closure
        if s.data[0].data is None:
            idx = self.add_literal(self._nil)
            self.emit_bytes(0, B_PUSH_LIT_CONSTANT, idx, B_RETURN_CONTEXT_STACK_TOP, 0)
        else:
            self.compile_statement_list(s.data, True)
        
        # create new block object and its literals array
        blkObj = CompiledBlock()
        blkObj.set_hdr(len(args), len(temps), self._max_depth)
        blkObj.set_code(self._cur_bytes)
        blkObj.literals = Array.from_seq(self._cur_literal)
        blkObj.literals.make_readonly()
        blkObj.method = self._cur_meth
        
        if self._verbose:
            print("Block------")
            print("Args:", args)
            print("Temps:", temps)
            print("Depth: ", self._max_depth)
            print("Block Literals", blkObj.literals.size)
            self._sys.arr_print(blkObj.literals)
            print("Block Bytecodes:", len(blkObj.get_code()))
            self._sys.dis_bytecode(blkObj.get_code())
        
        # restore context state
        self.context_pop()
        
        # add new block to context literals
        idx = self.add_literal(blkObj)
        self.emit_bytes(1, B_PUSH_LIT_CONSTANT, idx)
        
    def build_array(self, alist):
        """
        Construct a literal array
        """
        # create empty array
        arrObj = Array(len(alist))
        arrObj.make_readonly()
        
        # create array items and store references in array
        for n,item in enumerate(alist):
            x = item.value
            if isinstance(x, str):
                if x == "nil":
                    itemObj = self._nil
                elif x == "true":
                    itemObj = self._true
                elif x == "false":
                    itemObj = self._false
                else:
                    raise CompileError("variable not allowed in array: %s", x)
            elif isinstance(x, int):
                itemObj = x
            elif isinstance(x, ParseLiteralSymbol):
                itemObj = Symbol.from_str(x.value)
            elif isinstance(x, ParseLiteralString):
                itemObj = String.from_str(x.value)
            elif isinstance(x, ParseLiteralBytearray):
                itemObj = self.build_bytearray(x.value)
            elif isinstance(x, ParseLiteralArray):
                itemObj = self.build_array(x.value)
            else:
                raise CompileError("illegal array member: %s" % x)
            arrObj[n] = itemObj
        
        return arrObj
        
    def build_bytearray(self, alist):
        """
        Construct a literal bytearray
        """
        # create empty array
        arrObj = ByteArray(len(alist))
        arrObj.make_readonly()
        
        # store values in array
        for n,item in enumerate(alist):
            x = item.value
            if isinstance(x, int) and (x >= 0) and (x < 256):
                arrObj[n] = x
            else:
                raise CompileError("bytearray must be int 0 - 255: %s" % x)
            
        return arrObj
        
    def context_push(self):
        """
        Enter a new context
        """
        self._ctx_stack.append((self._cur_bytes, 
                                self._cur_literal,
                                self._cur_depth,
                                self._max_depth,
                                self._cur_local))
        self._cur_bytes = bytearray()
        self._cur_literal = []
        self._cur_local = []
        self._cur_depth = self._max_depth = 0
        
    def context_pop(self):
        """
        Leave a context
        """
        self._cur_bytes, \
        self._cur_literal, \
        self._cur_depth, \
        self._max_depth, \
        self._cur_local  = self._ctx_stack.pop()
        
    def add_literal(self, x):
        """
        Add a new literal reference to the current context
        and return its index into the literals array.
        """
        try:
            idx = self._cur_literal.index(x)
        except ValueError:
            self._cur_literal.append(x)
            idx = len(self._cur_literal) - 1
        return idx
            
    def emit_bytes(self, stackInc, *bc):
        """
        Append the bytecodes to the current code block
        """
        self._cur_depth += stackInc
        self._max_depth = max(self._max_depth, self._cur_depth)
        self._cur_bytes.extend((bc))
        
    def find_local(self, name):
        """
        Find the index of a argument or temporary
        variable name, or None if not local.  Returns a 
        tuple (idx, scope), where scope indicates:
        0  = current context
        >0 = parent context
        <0 = instance var index
        """   
        scope = 0
        
        # look in this context
        try:
            return (self._cur_local.index(name), scope)
        except ValueError:
            pass
            
        # look in parent contexts
        varStack = []
        for f in self._ctx_stack:
            varStack.append(f[-1])
        for varList in reversed(varStack):
            scope += 1
            try:
                return (varList.index(name), scope)
            except ValueError:
                pass
            
        # name is not local
        return (None, scope)

            

        