"""
Interpreter
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
        
        # the interpreter global state
        self.i_context = self._nil
        
        # the bytecode table
        self.b_table = bTbl = [None] * 256
        bTbl[B_PUSH_SELF] = self.b_push_self
        bTbl[B_RETURN_METHOD_STACK_TOP]= self.b_meth_ret
        
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
        if is_nil(selObj):
            raise NameError("unknown selector %s" % selName)
        
        # push receiver, selector, and args onto current stack
        psh(recvObj)
        psh(selObj)
        for a in argValues:
            psh(a)
            
        # send message
        self.send_message(len(argValues))
        
    def send_message(self, numArgs):
        """
        Send a message.  This assumes that the receiver,
        message selector, and argument values have been
        pushed to the current stack.
        """
        oldCtx = self.i_context
        pop = oldCtx.pop
        
        # pop the message arguments
        argList = []
        n = numArgs
        while n > 0:
            argList.append(pop())
            n -= 1
        argList.reverse()
        
        # pop the message selector and receiver
        selObj = pop()
        recvObj = pop()
    
        # lookup method object
        methDict = recvObj.get_class().methodDictionary
        methObj = self._sys.identdict_find(methDict, selObj)
        if is_nil(methObj):
            raise NameError("unknown method %s" % selObj)
        
        # check number of arguments
        if numArgs != methObj.get_num_arg():
            raise RuntimeError("wrong number of arguments")
        
        # allocate a new context and link to old
        newCtx = MethodContext()
        newCtx.parent = oldCtx
        newCtx.receiver = recvObj
        newCtx.method = methObj
        newCtx.ip = 0
        
        # push args onto new stack
        for a in argList:
            newCtx.push(a)
            
        # make room for temp variables
        numTemp = methObj.get_num_temp()
        if numTemp > 0:
            newCtx.expand(numTemp)
        
        # transfer control to new context
        self.i_context = newCtx
        
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
        op(code[ip + 1])
        ctx.ip = ip + 2        
        
    def b_push_self(self, arg):
        """
        Execute push self bytecode
        """
        ctx = self.i_context
        ctx.push(ctx.receiver)
        
    def b_meth_ret(self, arg):
        """
        Execute method return bytecode
        """
        # get sender parent context
        oldCtx = self.i_context
        newCtx = oldCtx.parent
        
        # pop return value from current stack
        # and push onto sender's stack
        newCtx.push(oldCtx.pop())
        
        # return control to sender
        self.i_context = newCtx
        
        



        
        
        
        
        