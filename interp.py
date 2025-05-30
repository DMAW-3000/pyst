"""
Bytecode interpreter
"""

from st import *


class Interp(object):
    """
    Interpreter definition
    """
    
    def __init__(self, system):
        """
        Create a new interpeter
        """
        # cache values from system
        self._sys = system
        self._nil = system.o_nil
        self._false = system.o_false
        self._true = system.o_true
        
        # the interpreter global state
        self.i_context = self._nil
        
        # the primitive handler table
        # index 0 is reserved
        self.i_primitive = [None]
        
        # debugging support
        self.i_debug_pre = None
        self.i_debug_post = None
        
        # the bytecode handler table
        self.b_table = bTbl = [None] * 256
        bTbl[B_PUSH_SELF] = self.b_push_self
        bTbl[B_PUSH_LIT_CONSTANT] = self.b_push_lit_const
        bTbl[B_PUSH_LIT_VARIABLE] = self.b_push_lit_var
        bTbl[B_PUSH_TEMPORARY_VARIABLE] = self.b_push_temp_var
        bTbl[B_RETURN_METHOD_STACK_TOP]= self.b_meth_ret
        bTbl[B_SEND] = self.b_send
        
    def reset(self):
        """
        Prepare for execution
        """
        # create the root context
        # leave the parent nil
        self.i_context = MethodContext()
        
    def send_message_extern(self, recvObj, selName, argValues):
        """
        Send a message from outside the interpreter.
        The selector name is a python str and the arg
        value sequence must match the selector arg order.
        """
        self.reset()
        psh = self.i_context.push
        
        # find selector symbol
        selObj = self._sys.symbol_find(selName)
        if selObj.is_nil():
            raise NameError("unknown selector %s" % selName)
        
        # push receiver, selector, and args onto current stack
        psh(recvObj)
        psh(selObj)
        for a in argValues:
            psh(a)
            
        # send message and run until control
        # returns to this root context
        self.send_message(len(argValues))
        self.exec()
        
        # pop return value from stack
        return self.i_context.pop()
        
    def send_message(self, numArgs):
        """
        Send a message.  This assumes that the receiver,
        message selector, and argument values have been
        pushed to the current stack.
        """
        # get old context
        # adjust ip so the next bytecode is ready
        # after return
        oldCtx = self.i_context
        pop = oldCtx.pop
        
        # pop the message arguments
        argList = []
        if numArgs > 0:
            n = numArgs
            while n > 0:
                argList.append(pop())
                n -= 1
            argList.reverse()
        
        # pop the message selector and receiver
        selObj = pop()
        recvObj = pop()
    
        # lookup method object from selector symbol
        # search from receiver's class through its
        # superclasses until Object's nil superclass
        if is_int(recvObj):
            klassObj = self._sys.k_small_int
        else:
            klassObj = recvObj.get_class()
        while True:
            #print("meth lookup", klassObj)
            methDict = klassObj.methodDictionary
            if not methDict.is_nil():
                methObj = self._sys.identdict_find(methDict, selObj)
                if not methObj.is_nil():
                    break
            superObj = klassObj.superClass
            if superObj.is_nil():
                raise NameError("unknown method %s" % selObj)
            klassObj = superObj 

        # get method info
        numHdrArgs, numTemp, depth, primId = methObj.get_hdr()
        
        # check number of arguments
        if numArgs != numHdrArgs:
            raise RuntimeError("wrong number of args %d for %s" % (numArgs, selObj))
        
        # allocate a new context and link to old
        newCtx = MethodContext()
        newCtx.parent = oldCtx
        newCtx.receiver = recvObj
        newCtx.method = methObj
        
        # push args onto new stack
        for a in argList:
            newCtx.push(a)
            
        # check for primitive operation
        # return control immediately to sender if
        # the primitive op is successful
        if primId > 0:
            try:
                primFunc = self.i_primitive[primId]
            except IndexError:
                primFunc = None
            if (primFunc is not None) and primFunc(newCtx, recvObj, numArgs):
                oldCtx.push(newCtx.pop())
                return
            
        # make room for temp variables on new stack
        if numTemp > 0:
            newCtx.expand(numTemp)
        
        # transfer control to new context
        self.i_context = newCtx
        
    def set_debug(self, preHook, postHook):
        """
        Set callbacks to be invoked before and after
        every bytecode instruction.
        """
        self.i_debug_pre = preHook
        self.i_debug_post = postHook
        
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
            if self.i_debug_pre is not None:
                self.i_debug_pre()
            self.step()
            if self.i_debug_post is not None:
                self.i_debug_post()
        
    def step(self):
        """
        Fetch and execute the next bytecode
        """
        ctx = self.i_context
        ip = ctx.ip
        code = ctx.method.get_code()
        op = self.b_table[code[ip]]
        if op is None:
            raise RuntimeError("unknown bytecode %d" % code[ip]) 
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
        ctx.push(ctx.method.literals[arg])
        return 2
        
    def b_push_lit_var(self, ctx, arg):
        """
        Execute the push literal var bytecode
        """
        # get symbol
        sym = ctx.method.literals[arg]
        
        # TODO - do full namespace resolution
        # look in all places for variable
        
        # look in globals
        var = self._sys.dict_find(self._sys.g_st_dict, sym)
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
        
    def b_send(self, ctx, arg):
        """
        Execute the generic send message bytecode
        """
        self.send_message(arg)
        return 2
        
    def b_meth_ret(self, ctx, arg):
        """
        Execute method return bytecode
        """
        # get sender parent context
        newCtx = ctx.parent
        
        # pop return value from current stack
        # and push onto sender's stack
        newCtx.push(ctx.pop())
        
        # return control to sender
        self.i_context = newCtx
        return 0
        
    def p_Object_basicSize(self, ctx, recv, numArg):
        """
        Primitive hander for Object basicSize
        """
        ctx.push(recv.size)
        return True
        
    def p_Object_identity(self, ctx, recv, numArg):
        """
        Primitive handler for Object identity (==)
        """
        send = ctx[7]
        if is_int(recv):
            if is_int(send):
                if recv == send:
                    ret = self._true
                else:
                    ret = self._false
            else:
                ret = self._false
        else:
            if is_int(send):
                ret = self._false
            else:
                if recv.is_same(send):
                    ret = self._true
                else:
                    ret = self._false
        ctx.push(ret)
        return True
        
    def p_Object_class(self, ctx, recv, numArg):
        """
        Primitive handler for Object class
        """
        if is_int(recv):
            klass = self._sys.k_small_int
        else:
            klass = recv.get_class()
        ctx.push(klass)
        return True
        
        
        



        
        
        
        
        