"""
Bytecode interpreter
"""

from st import *
import math
import gc


class Interp(object):
    """
    Interpreter definition
    """
    
    def __init__(self, system):
        """
        Create a new interpeter
        """
        # cache values from system
        self._sys   = system
        self._nil   = weakref.ref(system.o_nil)
        self._false = weakref.ref(system.o_false)
        self._true  = weakref.ref(system.o_true)
        
        # get refs to special selector symbols
        self._sel_initialize    = self._make_sel("initialize")
        self._sel_value         = self._make_sel("value")
        self._sel_size          = self._make_sel("size")
        self._sel_isnil         = self._make_sel("isNil")
        self._sel_notnil        = self._make_sel("notNil")
        self._sel_class         = self._make_sel("class")
        self._sel_at            = self._make_sel("at:")
        self._sel_at_put        = self._make_sel("at:put:")
        self._sel_value_colon   = self._make_sel("value:")
        self._sel_plus          = self._make_sel("+")
        self._sel_minus         = self._make_sel("-")
        self._sel_less_than     = self._make_sel("<")
        self._sel_greater_than  = self._make_sel(">")
        self._sel_less_equ      = self._make_sel("<=")
        self._sel_greater_equ   = self._make_sel(">=")
        self._sel_equal         = self._make_sel("=")
        self._sel_not_equal     = self._make_sel("~=")
        self._sel_times         = self._make_sel("*")
        self._sel_divide        = self._make_sel("/")
        self._sel_int_divide    = self._make_sel("//")
        self._sel_remainder     = self._make_sel("\\\\")
        self._sel_identity      = self._make_sel("==")
        self._sel_bit_and       = self._make_sel("bitAnd:")
        self._sel_bit_or        = self._make_sel("bitOr:")
        self._sel_bit_xor       = self._make_sel("bitXor:")
        self._sel_bit_shift     = self._make_sel("bitShift:")
        
        # the interpreter global state
        self.i_context = self._nil()
        
        # the primitive handler table
        # index 0 is reserved
        self.i_primitive = [None]
        
        # debugging support
        self.i_debug_pre    = self._debug_default
        self.i_debug_post   = self._debug_default
        
        # the bytecode handler table
        self.b_table = bTbl = [self._op_undef] * 256
        bTbl[B_PUSH_SELF]                   = self.b_push_self
        bTbl[B_PUSH_LIT_CONSTANT]           = self.b_push_lit_const
        bTbl[B_PUSH_LIT_VARIABLE]           = self.b_push_lit_var
        bTbl[B_PUSH_TEMPORARY_VARIABLE]     = self.b_push_temp_var
        bTbl[B_PUSH_OUTER_TEMP]             = self.b_push_outer_var
        bTbl[B_PUSH_RECEIVER_VARIABLE]      = self.b_push_recv_var
        bTbl[B_PUSH_INTEGER]                = self.b_push_int
        bTbl[B_PUSH_SPECIAL]                = self.b_push_special
        bTbl[B_DUP_STACK_TOP]               = self.b_dup_top
        bTbl[B_POP_STACK_TOP]               = self.b_pop_top
        bTbl[B_STORE_TEMPORARY_VARIABLE]    = self.b_store_temp_var
        bTbl[B_STORE_OUTER_TEMP]            = self.b_store_outer_var
        bTbl[B_STORE_LIT_VARIABLE]          = self.b_store_lit_var
        bTbl[B_STORE_RECEIVER_VARIABLE]     = self.b_store_recv_var
        bTbl[B_RETURN_METHOD_STACK_TOP]     = self.b_meth_ret
        bTbl[B_RETURN_CONTEXT_STACK_TOP]    = self.b_blk_ret
        bTbl[B_SEND]                        = self.b_send
        bTbl[B_SEND_SUPER]                  = self.b_send_super
        bTbl[B_VALUE_SPECIAL]               = self.b_send_spec_value
        bTbl[B_SIZE_SPECIAL]                = self.b_send_spec_size
        bTbl[B_IS_NIL_SPECIAL]              = self.b_send_spec_isnil
        bTbl[B_NOT_NIL_SPECIAL]             = self.b_send_spec_notnil
        bTbl[B_CLASS_SPECIAL]               = self.b_send_spec_class
        bTbl[B_AT_SPECIAL]                  = self.b_send_spec_at
        bTbl[B_AT_PUT_SPECIAL]              = self.b_send_spec_at_put
        bTbl[B_VALUE_COLON_SPECIAL]         = self.b_send_spec_value_colon
        bTbl[B_PLUS_SPECIAL]                = self.b_send_spec_plus
        bTbl[B_MINUS_SPECIAL]               = self.b_send_spec_minus
        bTbl[B_LESS_THAN_SPECIAL]           = self.b_send_spec_less_than
        bTbl[B_GREATER_THAN_SPECIAL]        = self.b_send_spec_greater_than
        bTbl[B_LESS_EQUAL_SPECIAL]          = self.b_send_spec_less_equ
        bTbl[B_GREATER_EQUAL_SPECIAL]       = self.b_send_spec_greater_equ
        bTbl[B_EQUAL_SPECIAL]               = self.b_send_spec_equal
        bTbl[B_NOT_EQUAL_SPECIAL]           = self.b_send_spec_not_equal
        bTbl[B_TIMES_SPECIAL]               = self.b_send_spec_times
        bTbl[B_DIVIDE_SPECIAL]              = self.b_send_spec_divide
        bTbl[B_INTEGER_DIVIDE_SPECIAL]      = self.b_send_spec_int_divide
        bTbl[B_REMAINDER_SPECIAL]           = self.b_send_spec_remainder
        bTbl[B_SAME_OBJECT_SPECIAL]         = self.b_send_spec_identity
        bTbl[B_BIT_AND_SPECIAL]             = self.b_send_spec_bit_and
        bTbl[B_BIT_OR_SPECIAL]              = self.b_send_spec_bit_or
        bTbl[B_BIT_XOR_SPECIAL]             = self.b_send_spec_bit_xor
        bTbl[B_BIT_SHIFT_SPECIAL]           = self.b_send_spec_bit_shift
        
    def _debug_default(self):
        """
        Default debug handler - does nothing
        """
        return
        
    def _op_undef(self, ctx, arg):
        """
        Called when an undefined bytecode is encountered
        """
        code = ctx.method.get_code()
        raise RuntimeError("unknown bytecode %d" % code[ctx.ip]) 
        
    def _make_sel(self, name):
        """
        Create a weak ref to a symbol
        """
        return weakref.ref(self._sys.symbol_find_or_add(name))
        
    def send_message_extern(self, recvObj, selObj, argValues):
        """
        Send a message from outside the interpreter.
        The selector object should be a valid Symbol and the
        value sequence must match the message arg order.
        """
        # create the root context
        # leave the parent nil
        self.i_context = MethodContext()
        psh = self.i_context.push
        
        # push receiver and args onto current stack
        psh(recvObj)
        for arg in argValues:
            psh(arg)
            
        # send message and run until control
        # returns to this root context
        self.send_message(len(argValues), False, selObj)
        self.exec()
        
        # pop return value from stack
        return self.i_context.pop()
        
    def send_message_intern(self, recvObj, selObj, argValues):
        """
        Send a message from inside the interpreter.
        The selector name is a python str and the arg
        value sequence must match the selector arg order.
        """
        # save the root context
        ctxSave = self.i_context
        
        # send the message smd get reply value
        ret = self.send_message_extern(recvObj, selObj, argValues)
        
        # restore context and return value
        self.i_context = ctxSave
        return ret
        
    def send_message(self, numArgs, isSuper, selObj):
        """
        Send a message.  This assumes that the receiver,
        message selector (possibly), and argument values have been
        pushed to the current stack.
        """
        # get old context
        oldCtx = self.i_context
        pop = oldCtx.pop
        
        # pop the message arguments from parent stack
        if numArgs:
            argList = [None] * numArgs
            n = numArgs
            while n:
                argList[n - 1] = pop()
                n -= 1
        else:
            argList = ()
        
        # pop the message selector and receiver
        if selObj is None:
            selObj = pop()
        recvObj = pop()
    
        # get class type for receiver
        # handle primitive types specially
        if is_int(recvObj):
            klassObj = self._sys.k_small_int()
        elif is_flt(recvObj):
            klassObj = self._sys.k_float_d()
        else:
            klassObj = recvObj.get_class()
            
        # lookup method object from selector symbol
        # search from receiver's class through its
        # superclasses until Object's nil superclass
        # if send super, start one class up in hierarchy
        methObj = self._nil()
        if isSuper:
            klassObj = klassObj.superClass
        while not klassObj.is_nil():
            #print("meth lookup", klassObj)
            methDict = klassObj.methodDictionary
            if not methDict.is_nil():
                methObj = self._sys.identdict_find(methDict, selObj)
                if not methObj.is_nil():
                    break
            klassObj = klassObj.superClass 
        if methObj.is_nil():
            raise NameError("unknown method %s" % selObj)

        # get method info
        numHdrArgs, numTemp, depth, primId = methObj.get_hdr()
        
        # check number of arguments
        if numArgs != numHdrArgs:
            raise RuntimeError("wrong number of args %d for %s" % (numArgs, selObj))
            
        # check for primitive operation
        # return control immediately to sender if
        # the primitive op is successful
        if primId:
            primFunc = self.i_primitive[primId]
            if primFunc(oldCtx, recvObj, argList):
                return
        
        # allocate a new context and link to old
        newCtx = MethodContext()
        newCtx.parent   = oldCtx
        newCtx.receiver = recvObj
        newCtx.method   = methObj
        
        # push args onto new stack
        for arg in argList:
            newCtx.push(arg)
            
        # make room for temp variables on new stack
        if numTemp:
            newCtx.expand(numTemp)
        
        # transfer control to new context
        self.i_context = newCtx
        
    def set_debug(self, preHook, postHook):
        """
        Set callbacks to be invoked before and after
        every bytecode instruction.
        """
        self.i_debug_pre    = preHook
        self.i_debug_post   = postHook
        
    def get_debug(self):
        """
        Get the curent debug callbacks (pre, post)
        """
        return (self.i_debug_pre, self.i_debug_post)
        
    def add_primitive(self, name):
        """
        Add a primitive handler at a given index.
        Return True if successful, False otherwise.
        """
        name = "p_" + name
        if not hasattr(self, name):
            return False
        handler = getattr(self, name)
        self.i_primitive.append(handler)
        return True
        
    def exec(self):
        """
        Start executing bytecodes from current location
        until the control returns to the root context.
        """
        while not self.i_context.parent.is_nil():
            self.i_debug_pre()
            self.step()
            self.i_debug_post()
        
    def step(self):
        """
        Fetch and execute the next bytecode
        """
        ctx = self.i_context
        ip = ctx.ip
        code = ctx.method.get_code()
        op = self.b_table[code[ip]]    
        ctx.ip = ip + op(ctx, code[ip + 1])
    
    def b_push_self(self, ctx, arg):
        """
        Execute push self bytecode
        """
        ctx.push(ctx.receiver)
        return 2
        
    def b_push_lit_const(self, ctx, arg):
        """
        Execute push literal constant bytecode
        """
        # look for compiled blocks
        # turn into BlockClosures
        lit = ctx.method.literals[arg]
        if is_obj(lit) and (lit.get_class() is self._sys.k_comp_block()):
            blk = BlockClosure()
            blk.block = lit
            blk.outerContext = ctx
            blk.receiver = ctx.receiver
            lit = blk
            
        # return on stack
        ctx.push(lit)
        return 2
        
    def b_push_lit_var(self, ctx, arg):
        """
        Execute the push literal var bytecode
        """
        # get symbol
        sym = ctx.method.literals[arg]
        
        # look in all class variables (including superclasses)
        recv = ctx.receiver
        if is_int(recv):
            klassObj = self._sys.k_small_int()
        elif is_flt(recv):
            klassObj = self._sys.k_float_d()
        else:
            klassObj = recv.get_class()
        if klassObj.get_class() is self._sys.k_metaclass():
            # handle special case of access from inside class method
            klassObj = recv
        while not klassObj.is_nil():
            #print("var lookup", klassObj)
            varDict = klassObj.classVariables
            if not varDict.is_nil():
                var = self._sys.dict_find(varDict, sym)
                if not var.is_nil():
                    # push variable to stack
                    ctx.push(var.value)
                    return 2
            klassObj = klassObj.superClass
            
        # look in globals
        var = self._sys.dict_find(self._sys.e_st_dict, sym)
        if var.is_nil():
            raise NameError("variable %s not found" % sym)
        
        # push variable to stack
        ctx.push(var.value.value)
        return 2
        
    def b_push_temp_var(self, ctx, arg):
        """
        Execute the push temp variable bytecode
        """
        ctx.push(ctx[7 + arg])
        return 2
        
    def b_push_outer_var(self, ctx, arg):
        """
        Execute the push outer temp variable bytecde
        """
        # get extended bytecode data
        level = ctx.method.get_code()[ctx.ip + 3]

        # look through context frames
        outer = ctx.outerContext
        while level:
            outer = outer.outerContext
            level -= 1

        # return temp variable
        ctx.push(outer[7 + arg])
        return 4
        
    def b_push_recv_var(self, ctx, arg):
        """
        Execute the push receiver variable bytecode
        """
        ctx.push(ctx.receiver[arg])
        return 2
        
    def b_push_int(self, ctx, arg):
        """
        Execute the push integer literal bytecode
        """
        ctx.push(arg)
        return 2
        
    def b_push_special(self, ctx, arg):
        """
        Execute the push special bytecode
        """
        ctx.push(ctx)
        return 2
        
    def b_dup_top(self, ctx, arg):
        """
        Execute the duplicate stack top bytecode.
        Push the last value on the stack.
        """
        ctx.push(ctx[-1])
        return 2
        
    def b_pop_top(self, ctx, arg):
        """
        Execute the pop stack top bytecode.
        Pop the last value from the stack and discard.
        """
        ctx.pop()
        return 2
        
    def b_store_temp_var(self, ctx, arg):
        """
        Execute the store temp variable bytecode
        """
        ctx[7 + arg] = ctx.pop()
        return 2
        
    def b_store_outer_var(self, ctx, arg):
        """
        Execute the store outer temp variable bytecde
        """
        # get extended bytecode data
        level = ctx.method.get_code()[ctx.ip + 3]

        # look through context frames
        outer = ctx.outerContext
        while level:
            outer = outer.outerContext
            level -= 1
        # store temp variable
        outer[7 + arg] = ctx.pop()
        return 4
        
    def b_store_lit_var(self, ctx, arg):
        """
        Execute the store literal var bytecode
        """
        # get symbol
        sym = ctx.method.literals[arg]
        
        # look in all class variables (including superclasses)
        recv = ctx.receiver
        if is_int(recv):
            klassObj = self._sys.k_small_int()
        elif is_flt(recv):
            klassObj = self._sys.k_float_d()
        else:
            klassObj = recv.get_class()
        if klassObj.get_class() is self._sys.k_metaclass():
            # handle special case of access from inside class method
            klassObj = recv
        while not klassObj.is_nil():
            #print("var lookup", klassObj)
            varDict = klassObj.classVariables
            if not varDict.is_nil():
                var = self._sys.dict_find(varDict, sym)
                if not var.is_nil():
                    # pop variable from stack
                    var.value = ctx.pop()
                    return 2
            klassObj = klassObj.superClass
            
        # look in globals
        var = self._sys.dict_find(self._sys.e_st_dict, sym)
        if var.is_nil():
            raise NameError("variable %s not found" % sym)
        
        # pop variable from stack
        var.value.value = ctx.pop()
        return 2
        
    def b_store_recv_var(self, ctx, arg):
        """
        Execute the store receiver variable bytecode
        """
        ctx.receiver[arg] = ctx.pop()
        return 2

    def b_send(self, ctx, arg):
        """
        Execute the generic send message bytecode
        """
        self.send_message(arg, False, None)
        return 2
        
    def b_send_super(self, ctx, arg):
        """
        Execute the send message to super bytecode
        """
        self.send_message(arg, True, None)
        return 2
        
    def b_send_spec_value(self, ctx, arg):
        """
        Execute the send message special value bytecode
        """
        self.send_message(arg, False, self._sel_value())
        return 2
        
    def b_send_spec_size(self, ctx, arg):
        """
        Execute the send message special size bytecode
        """
        self.send_message(arg, False, self._sel_size())
        return 2
        
    def b_send_spec_isnil(self, ctx, arg):
        """
        Execute the send message special isNil bytecode
        """
        self.send_message(arg, False, self._sel_isnil())
        return 2
        
    def b_send_spec_notnil(self, ctx, arg):
        """
        Execute the send message special notNil bytecode
        """
        self.send_message(arg, False, self._sel_notnil())
        return 2
        
    def b_send_spec_class(self, ctx, arg):
        """
        Execute the send message special class bytecode
        """
        self.send_message(arg, False, self._sel_class())
        return 2
        
    def b_send_spec_at(self, ctx, arg):
        """
        Execute the send message special at: bytecode
        """
        self.send_message(arg, False, self._sel_at())
        return 2
        
    def b_send_spec_at_put(self, ctx, arg):
        """
        Execute the send message special at:put: bytecode
        """
        self.send_message(arg, False, self._sel_at_put())
        return 2
        
    def b_send_spec_value_colon(self, ctx, arg):
        """
        Execute the send message special value: bytecode
        """
        self.send_message(arg, False, self._sel_value_colon())
        return 2
        
    def b_send_spec_plus(self, ctx, arg):
        """
        Execute the send message special + bytecode
        """
        self.send_message(arg, False, self._sel_plus())
        return 2
        
    def b_send_spec_minus(self, ctx, arg):
        """
        Execute the send message special - bytecode
        """
        self.send_message(arg, False, self._sel_minus())
        return 2
        
    def b_send_spec_less_than(self, ctx, arg):
        """
        Execute the send message special < bytecode
        """
        self.send_message(arg, False, self._sel_less_than())
        return 2
        
    def b_send_spec_greater_than(self, ctx, arg):
        """
        Execute the send message special > bytecode
        """
        self.send_message(arg, False, self._sel_greater_than())
        return 2
        
    def b_send_spec_less_equ(self, ctx, arg):
        """
        Execute the send message special <= bytecode
        """
        self.send_message(arg, False, self._sel_less_equ())
        return 2
        
    def b_send_spec_greater_equ(self, ctx, arg):
        """
        Execute the send message special >= bytecode
        """
        self.send_message(arg, False, self._sel_greater_equ())
        return 2
        
    def b_send_spec_equal(self, ctx, arg):
        """
        Execute the send message special = bytecode
        """
        self.send_message(arg, False, self._sel_equal())
        return 2
        
    def b_send_spec_not_equal(self, ctx, arg):
        """
        Execute the send message special ~= bytecode
        """
        self.send_message(arg, False, self._sel_not_equal())
        return 2
        
    def b_send_spec_times(self, ctx, arg):
        """
        Execute the send message special * bytecode
        """
        self.send_message(arg, False, self._sel_times())
        return 2
        
    def b_send_spec_divide(self, ctx, arg):
        """
        Execute the send message special / bytecode
        """
        self.send_message(arg, False, self._sel_divide())
        return 2
        
    def b_send_spec_int_divide(self, ctx, arg):
        """
        Execute the send message special // bytecode
        """
        self.send_message(arg, False, self._sel_int_divide())
        return 2
        
    def b_send_spec_remainder(self, ctx, arg):
        """
        Execute the send message special \\ bytecode
        """
        self.send_message(arg, False, self._sel_remainder())
        return 2
        
    def b_send_spec_identity(self, ctx, arg):
        """
        Execute the send message special == bytecode
        """
        self.send_message(arg, False, self._sel_identity())
        return 2
        
    def b_send_spec_bit_and(self, ctx, arg):
        """
        Execute the send message special bitAnd: bytecode
        """
        self.send_message(arg, False, self._sel_bit_and())
        return 2
        
    def b_send_spec_bit_or(self, ctx, arg):
        """
        Execute the send message special bitOr: bytecode
        """
        self.send_message(arg, False, self._sel_bit_or())
        return 2
        
    def b_send_spec_bit_xor(self, ctx, arg):
        """
        Execute the send message special bitXor: bytecode
        """
        self.send_message(arg, False, self._sel_bit_xor())
        return 2
        
    def b_send_spec_bit_shift(self, ctx, arg):
        """
        Execute the send message special bitShift: bytecode
        """
        self.send_message(arg, False, self._sel_bit_shift())
        return 2
        
    def b_meth_ret(self, ctx, arg):
        """
        Execute method return bytecode
        """
        # we may be nested in blocks
        # unwind until method context
        outCtx = ctx
        while not is_int(outCtx[6]):
            outCtx = outCtx.outerContext
        
        # get sender parent context
        newCtx = outCtx.parent
        
        # pop return value from current stack
        # and push onto sender's stack
        newCtx.push(ctx.pop())
        
        # return control to sender
        self.i_context = newCtx
        return 0
        
    def b_blk_ret(self, ctx, arg):
        """
        Execute context return bytecode
        """
        # get sender parent context
        newCtx = ctx.parent

        # pop return value from current stack
        # and push onto sender's stack
        newCtx.push(ctx.pop())

        # return control to sender
        self.i_context = newCtx
        return 0

    def p_Object_basicSize(self, ctx, recv, argList):
        """
        Primitive hander for Object basicSize
        This is the number of index references, not counting
        the class defined instance variables.
        """
        if is_obj(recv):
            sz = recv.size - (recv.get_class().instanceSpec >> 12)
        else:
            sz = 0
        ctx.push(sz)
        return True
        
    def p_Object_identity(self, ctx, recv, argList):
        """
        Primitive handler for Object identity (==)
        Check if two objects are identical, that is, have
        the same object ID.
        """
        send = argList[0]
        if is_obj(send) and recv.is_same(send):
            ret = self._true()
        else:
            ret = self._false()
        ctx.push(ret)
        return True
        
    def p_Object_class(self, ctx, recv, argList):
        """
        Primitive handler for Object class
        Get a reference to an object's class.
        """
        if is_int(recv):
            klass = self._sys.k_small_int()
        elif is_flt(recv):
            klass = self._sys.k_float_d()
        else:
            klass = recv.get_class()
        ctx.push(klass)
        return True
        
    def p_Object_basicAt(self, ctx, recv, argList):
        """
        Primitve handler for Object at:
        """
        idx = argList[0]
        if is_int(idx):
            spec = recv.get_class().instanceSpec
            if not (spec & 0x10):
                try:
                    ret = recv[(spec >> 12) + idx - 1]
                except IndexError:
                    return False
                ctx.push(ret)
                return True
        return False
        
    def p_Object_basicAtPut(self, ctx, recv, argList):
        """
        Primitve handler for Object at:put:
        """
        idx = argList[0]
        if is_int(idx):
            spec = recv.get_class().instanceSpec
            if not (spec & 0x10):
                val = argList[1]
                try:
                    recv[(spec >> 12) + idx - 1] = val
                except IndexError:
                    return False
                ctx.push(val)
                return True
        return False
        
    def p_Object_shallowCopy(self, ctx, recv, argList):
        """
        Primitive handler for Object shallowCopy
        """
        if is_obj(recv):
            ret = recv.clone()
        else:
            ret = recv
        ctx.push(ret)
        return True
        
    def p_Object_isReadOnly(self, ctx, recv, argList):
        """
        Primitive handler for Object isReadOnly
        """
        if is_obj(recv) and not recv.is_readonly():
            ret = self._false()
        else:
            ret = self._true()
        ctx.push(ret)
        return True
        
    def p_Object_hash(self, ctx, recv, argList):
        """
        Primitive handler for Object hash
        """
        if is_obj(recv):
            ret = recv.get_id()
        else:
            ret = int(recv)
        ctx.push(ret)
        return True
        
    def p_Object_become(self, ctx, recv, argList):
        """
        Primitive handler for Object become:
        """
        # check arguments
        send = argList[0]
        if is_obj(send):
            if not recv.is_readonly() and not send.is_readonly():
                # get references to original object stored in
                # other objects
                for obj in gc.get_referrers(recv):
                    if isinstance(obj, list):
                        # search through this object's references
                        n = obj.count(recv)
                        idx = 0
                        while n:
                            # replace references with new object
                            idx = obj.index(recv, idx)
                            obj[idx] = send
                            idx += 1
                            n -= 1
                    else:
                        raise RuntimeError("become not list")
                ctx.push(recv)
                return True
        return False
        
    def p_Object_allOwners(self, ctx, recv, argList):
        """
        Primtive handler for Object allOwners.
        Return Array of other Objects that reference this one.
        """
        refList = []
        if is_obj(recv):
            # get references to this object stored in
            # other objects
            for obj1 in gc.get_referrers(recv):
                for obj2 in gc.get_referrers(obj1):
                    if isinstance(obj2, dict):
                        obj3 = gc.get_referrers(obj2)
                        for obj4 in obj3:
                            if isinstance(obj4, Object):
                                refList.append(obj4)
        ctx.push(Array.from_seq(refList))
        return True
        
    def p_Object_perform(self, ctx, recv, argList):
        """
        Primitive handler for Object perform:
        """
        send = argList[0]
        if is_obj(send):
            argList = argList[1:]
            klass = send.get_class()
            if klass is self._sys.k_symbol():
                ret = self.send_message_intern(recv, send, argList)
            else:
                return False
            ctx.push(ret)
            return True
        return False
        
    def p_Object_performWithArguments(self, ctx, recv, argList):
        """
        Primitive handler for Object perform:withArguments:
        """
        send    = argList[0]
        argArr  = argList[1]
        if is_obj(send) and is_obj(argArr) and (argArr.get_class() is self._sys.k_array()):
            argList = [arg for arg in argArr]
            klass = send.get_class()
            if klass is self._sys.k_symbol():
                ret = self.send_message_intern(recv, send, argList)
            else:
                return False
            ctx.push(ret)
            return True
        return False
        
    def p_BlockClosure_value(self, ctx, recv, argList):
        """
        Primitive handler for BlockClosure value
        recv = BlockSlosure object
        """
        # get block info and verify number of args
        numArg = len(argList)
        blkObj = recv.block
        numHdrArgs, numTemp, depth = blkObj.get_hdr()
        if numHdrArgs != numArg:
            return False

        # allocate a new context and link to old
        newCtx = BlockContext()
        newCtx.parent = ctx
        newCtx.receiver = recv.receiver
        newCtx.method = blkObj
        newCtx.outerContext = recv.outerContext
        
        # copy arguments to new stack
        for arg in argList:
            newCtx.push(arg)
                
        # mske room for any temporary variables
        if numTemp:
            newCtx.expand(numTemp)

        # transfer control to new context
        self.i_context = newCtx
        return True
        
    def p_BlockClosure_cull(self, ctx, recv, argList):
        """
        Primitive handler for BlockClosure cull
        recv = BlockSlosure object
        """
        # get block info and verify number of args
        # trim excess arguments
        numArg = len(argList)
        blkObj = recv.block
        numHdrArgs, numTemp, depth = blkObj.get_hdr()
        if numHdrArgs > numArg:
            return False
        argList = argList[:numHdrArgs]

        # allocate a new context and link to old
        newCtx = BlockContext()
        newCtx.parent = ctx
        newCtx.receiver = recv.receiver
        newCtx.method = blkObj
        newCtx.outerContext = recv.outerContext
        
        # copy arguments to new stack
        for arg in argList:
            newCtx.push(arg)
                
        # mske room for any temporary variables
        if numTemp:
            newCtx.expand(numTemp)

        # transfer control to new context
        self.i_context = newCtx
        return True
        
    def p_BlockClosure_valueWithArguments(self, ctx, recv, argList):
        """
        Primitive handler for BlockClosure valueWithArguments:
        """
        # get argument array
        argList = argList[0]
        if not is_obj(argList) or (argList.get_class() is not self._sys.k_array()):
            return
        numArg = argList.size
            
        # get block info and verify number of args
        blkObj = recv.block
        numHdrArgs, numTemp, depth = blkObj.get_hdr()
        if numHdrArgs != numArg:
            return False

        # allocate a new context and link to old
        newCtx = BlockContext()
        newCtx.parent = ctx
        newCtx.receiver = recv.receiver
        newCtx.method = blkObj
        newCtx.outerContext = recv.outerContext
        
        # copy arguments to new stack
        for arg in argList:
            newCtx.push(arg)
                
        # mske room for any temporary variables
        if numTemp:
            newCtx.expand(numTemp)

        # transfer control to new context
        self.i_context = newCtx
        return True
        
    def p_Behavior_basicNew(self, ctx, recv, argList):
        """
        Primitiive handler for Behavior basicNew
        Create a new instance of a object based on class definition.
        For objects of fixed size.
        """
        if is_obj(recv) and (recv.get_class().get_class() is self._sys.k_metaclass()):
            spec = recv.instanceSpec
            if spec & 0x10:
                obj = Object(spec >> 12)
                obj._klass = recv
                ctx.push(obj)
                return True
        return False
        
    def p_Behavior_basicNewColon(self, ctx, recv, argList):
        """
        Primitiive handler for Behavior basicNew:
        Create a new instance of a object based on class definition.
        For objects of veriable size.
        """
        sz = argList[0]
        if is_obj(recv) and is_int(sz) and (recv.get_class().get_class() is self._sys.k_metaclass()):
            spec = recv.instanceSpec
            if not (spec & 0x10):
                obj = Object((spec >> 12) + sz)
                obj._klass = recv
                ctx.push(obj)
                return True
        return False
        
    def p_Behavior_newInitialize(self, ctx, recv, argList):
        """
        Primitive handler for Bahavior new.
        Create a new instance of a object based on class definition.
        Send initialize message to the new object after creation.
        For objects of fixed size.
        """
        # create the object
        status = self.p_Behavior_basicNew(ctx, recv, argList)
        
        if status:
            # send the new object initialize message
            self.send_message_intern(ctx[-1], self._sel_initialize(), ())
        return status
        
    def p_Behavior_newColonInitialize(self, ctx, recv, argList):
        """
        Primitive handler for Bahavior mew:
        Create a new instance of a object based on class definition.
        Send initialize message to the new object after creation.
        For objects of variable size.
        """
        # create the object
        status = self.p_Behavior_basicNewColon(ctx, recv, argList)
        
        if status:
            # send the new object initialize message
            self.send_message_intern(ctx[-1], self._sel_initialize(), ())
        return status
        
    def p_Character_create(self, ctx, recv, argList):
        """
        Primitve handler for Character value:
        """
        idx = argList[0]
        if is_int(idx):
            try:
                ret = self._sys.o_char[idx]
            except IndexError:
                return False
            ctx.push(ret)
            return True
        return False
        
    def p_Character_equal(self, ctx, recv, argList):
        """
        Primitive handler for Character =
        """
        send = argList[0]
        ret = self._false()
        if is_obj(send) and (send.get_class() is self._sys.k_character()):
            if recv.codePoint == send.codePoint:
                ret = self._true()
        ctx.push(ret)
        return True
        
    def p_SmallInteger_plus(self, ctx, recv, argList):
        """
        Primitive handler for SmallInteger +
        """
        global Int_Max
        send = argList[0]
        if is_int(send):
            x = recv + send
            if abs(x) > Int_Max:
                return False
            ctx.push(x)
            return True
        return False
        
    def p_SmallInteger_minus(self, ctx, recv, argList):
        """
        Primirive handler for SmallInteger -
        """
        global Int_Max
        send = argList[0]
        if is_int(send):
            x = recv - send
            if abs(x) > Int_Max:
                return False
            ctx.push(x)
            return True
        return False
        
    def p_SmallInteger_times(self, ctx, recv, argList):
        """
        Primirive handler for SmallInteger *
        """
        global Int_Max
        send = argList[0]
        if is_int(send):
            x = recv * send
            if abs(x) > Int_Max:
                return False
            ctx.push(x)
            return True
        return False
        
    def p_SmallInteger_intDiv(self, ctx, recv, argList):
        """
        Primirive handler for SmallInteger //
        """
        send = argList[0]
        if is_int(send):
            if send == 0:
                return False
            ctx.push(recv // send)
            return True
        return False
        
    def p_SmallInteger_modulo(self, ctx, recv, argList):
        """
        Primirive handler for SmallInteger \\
        """
        send = argList[0]
        if is_int(send):
            if send == 0:
                return False
            ctx.push(recv % send)
            return True
        return False
        
    def p_SmallInteger_quo(self, ctx, recv, argList):
        """
        Primirive handler for SmallInteger quo:
        Return an integer result rounded to zero.
        """
        send = argList[0]
        if is_int(send):
            if send == 0:
                return False
            ctx.push(int(recv / send))
            return True
        return False
        
    def p_SmallInteger_divide(self, ctx, recv, argList):
        """
        Primirive handler for SmallInteger /
        Return an integer or Fraction.
        """
        send = argList[0]
        if is_int(send):
            if send == 0:
                return False
            if math.isclose((recv / send) % 1, 0):
                ret = int(recv / send)
            else:
                ret = Fraction(recv, send)
            ctx.push(ret)
            return True
        return False
        
    def p_SmallInteger_lt(self, ctx, recv, argList):
        """
        Primitive handler for SmallInteger <
        """
        send = argList[0]
        if is_int(send):
            if recv < send:
                ctx.push(self._true())
            else:
                ctx.push(self._false())
            return True
        return False
        
    def p_SmallInteger_gt(self, ctx, recv, argList):
        """
        Primitive handler for SmallInteger >
        """
        send = argList[0]
        if is_int(send):
            if recv > send:
                ctx.push(self._true())
            else:
                ctx.push(self._false())
            return True
        return False
        
    def p_SmallInteger_le(self, ctx, recv, argList):
        """
        Primitive handler for SmallInteger <=
        """
        send = argList[0]
        if is_int(send):
            if recv <= send:
                ctx.push(self._true())
            else:
                ctx.push(self._false())
            return True
        return False
        
    def p_SmallInteger_ge(self, ctx, recv, argList):
        """
        Primitive handler for SmallInteger >=
        """
        send = argList[0]
        if is_int(send):
            if recv >= send:
                ctx.push(self._true())
            else:
                ctx.push(self._false())
            return True
        return False
        
    def p_SmallInteger_eq(self, ctx, recv, argList):
        """
        Primitive handler for SmallInteger =
        """
        send = argList[0]
        if is_int(send):
            if recv == send:
                ctx.push(self._true())
            else:
                ctx.push(self._false())
            return True
        return False
        
    def p_SmallInteger_ne(self, ctx, recv, argList):
        """
        Primitive handler for SmallInteger ~=
        """
        send = argList[0]
        if is_int(send):
            if recv != send:
                ctx.push(self._true())
            else:
                ctx.push(self._false())
            return True
        return False
        
    def p_SmallInteger_bitAnd(self, ctx, recv, argList):
        """
        Primitive handler for SmallInteger bitAnd:
        """
        send = argList[0]
        if is_int(send):
            ctx.push(recv & send)
            return True
        return False
        
    def p_SmallInteger_bitOr(self, ctx, recv, argList):
        """
        Primitive handler for SmallInteger bitOr:
        """
        send = argList[0]
        if is_int(send):
            ctx.push(recv | send)
            return True
        return False
        
    def p_SmallInteger_bitXor(self, ctx, recv, argList):
        """
        Primitive handler for SmallInteger bitXor:
        """
        send = argList[0]
        if is_int(send):
            ctx.push(recv ^ send)
            return True
        return False
        
    def p_SmallInteger_bitShift(self, ctx, recv, argList):
        """
        Primitive handler for SmallInteger bitShift:
        """
        global Int_Max
        send = argList[0]
        if is_int(send):
            if send <= 0:
                x = recv >> abs(send)
            else:
                x = recv << send
                if abs(x) > Int_Max:
                    return False
            ctx.push(x)
            return True
        return False
        
    def p_FloatD_infinity(self, ctx, recv, argList):
        """
        Primitive handler for FloatD infinity
        """
        ctx.push(float("inf"))
        return True
        
    def p_FloatD_negativeInfinity(self, ctx, recv, argList):
        """
        Primitive handler for FloatD negativeInfinity
        """
        ctx.push(float("-inf"))
        return True
        
    def p_FloatD_nan(self, ctx, recv, argList):
        """
        Primitive handler for FloatD nan
        """
        ctx.push(float("nan"))
        return True
        
    def p_FloatD_fmax(self, ctx, recv, argList):
        """
        Primitive handler for FloatD fmax
        """
        ctx.push(sys.float_info.max)
        return True
        
    def p_FloatD_fminNormalized(self, ctx, recv, argList):
        """
        Primitive handler for FloatD fminNormalized
        """
        ctx.push(sys.float_info.epsilon)
        return True
        
    def p_FloatD_emax(self, ctx, recv, argList):
        """
        Primitive handler for FloatD emax
        """
        ctx.push(sys.float_info.max_exp)
        return True
        
    def p_FloatD_emin(self, ctx, recv, argList):
        """
        Primitive handler for FloatD emin
        """
        ctx.push(sys.float_info.min_exp)
        return True
            
    def p_FloatD_precision(self, ctx, recv, argList):
        """
        Primitive handler for FloatD precision
        """
        ctx.push(sys.float_info.mant_dig)
        return True
        
    def p_FloatD_decimalDigits(self, ctx, recv, argList):
        """
        Primitive handler for FloatD decimalDigits
        """
        ctx.push(sys.float_info.dig)
        return True
        
    def p_FloatD_plus(self, ctx, recv, argList):
        """
        Primitive handler for FloatD +
        """
        send = argList[0]
        if is_flt(send):
            ctx.push(recv + send)
            return True
        return False
        
    def p_FloatD_minus(self, ctx, recv, argList):
        """
        Primitive handler for FloatD -
        """
        send = argList[0]
        if is_flt(send):
            ctx.push(recv - send)
            return True
        return False
        
    def p_FloatD_times(self, ctx, recv, argList):
        """
        Primitive handler for FloatD *
        """
        send = argList[0]
        if is_flt(send):
            ctx.push(recv * send)
            return True
        return False
        
    def p_FloatD_divide(self, ctx, recv, argList):
        """
        Primitive handler for FloatD /
        """
        send = argList[0]
        if is_flt(send):
            if send == 0.0:
                return False
            ctx.push(recv / send)
            return True
        return False
        
    def p_FloatD_lt(self, ctx, recv, argList):
        """
        Primitive handler for FloatD <
        """
        send = argList[0]
        if is_flt(send):
            if recv < send:
                ctx.push(self._true())
            else:
                ctx.push(self._false())
            return True
        return False
        
    def p_FloatD_gt(self, ctx, recv, argList):
        """
        Primitive handler for FloatD >
        """
        send = argList[0]
        if is_flt(send):
            if recv > send:
                ctx.push(self._true())
            else:
                ctx.push(self._false())
            return True
        return False
        
    def p_FloatD_le(self, ctx, recv, argList):
        """
        Primitive handler for FloatD <=
        """
        send = argList[0]
        if is_flt(send):
            if recv <= send:
                ctx.push(self._true())
            else:
                ctx.push(self._false())
            return True
        return False
        
    def p_FloatD_ge(self, ctx, recv, argList):
        """
        Primitive handler for FloatD >=
        """
        send = argList[0]
        if is_flt(send):
            if recv >= send:
                ctx.push(self._true())
            else:
                ctx.push(self._false())
            return True
        return False
        
    def p_FloatD_eq(self, ctx, recv, argList):
        """
        Primitive handler for FloatD =
        """
        send = argList[0]
        if is_flt(send):
            if recv == send:
                ctx.push(self._true())
            else:
                ctx.push(self._false())
            return True
        return False
        
    def p_FloatD_ne(self, ctx, recv, argList):
        """
        Primitive handler for FloatD ~=
        """
        send = argList[0]
        if is_flt(send):
            if recv != send:
                ctx.push(self._true())
            else:
                ctx.push(self._false())
            return True
        return False
        
    def p_ArrayedCollection_replaceFromToWithStartingAt(self, ctx, recv, argList):
        """
        Primitve handler for Array replaceFrom:To:With:StartingAt:
        """
        start           = argList[0]
        stop            = argList[1]
        replaceArr      = argList[2]
        replaceStart    = argList[3]
        if is_int(start) and is_int(stop) and is_int(replaceStart):
            if stop >= start:
                n = stop - start + 1
                try:
                    while n:
                        recv[start + n - 2] = replaceArr[replaceStart + n - 2]
                        n -= 1
                except IndexError:
                    return False
                ctx.push(recv)
                return True
        return False
        
    def p_ArrayedCollection_indexOfStartingAt(self, ctx, recv, argList):
        """
        Primitve handler for Array indexOf:StartingAt:
        """
        item    = argList[0]
        start   = argList[1]
        if is_int(start):
            try:
                idx = recv._refs.index(item, start - 1) + 1
            except ValueError:
                idx = 0
            ctx.push(idx)
            return True
        return False
        
    def p_ByteArray_basicNewColon(self, ctx, recv, argList):
        """
        Primitiive handler for ByteArray basicNew:
        Optimization to get proper storage type.
        """
        sz = argList[0]
        if is_int(sz):
            ctx.push(ByteArray(sz))
            return True
        return False        
    
    def p_ByteArray_newColonInitialize(self, ctx, recv, argList):
        """
        Primitive handler for ByteArray mew:
        Send initialize message to the new object after creation.
        """
        # create the object
        status = self.p_ByteArray_basicNewColon(ctx, recv, argList)
        
        if status:
            # send the new object initialize message
            self.send_message_intern(ctx[-1], self._sel_initialize(), ())
        return status
        
        
        
        
        
        



        
        
        
        
        