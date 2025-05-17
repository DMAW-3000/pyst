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
        
    def reset(self):
        """
        Prepare for execution
        """
        # create the root context
        # leave the parent nil
        self.i_context = MethodContext()
        
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
        print(argList)
        
        # pop the message selector
        selObj = pop()
        print(selObj)
        
        # pop the receiver
        recvObj = pop()
        print(recvObj)
        
        # TODO: lookup method object
        methDict = recvObj.get_class().methodDictionary
        
        # check number of arguments
        if numArgs != methObj.get_num_arg():
            raise RuntimeError("wrong number of arguments")
        
        # allocate a new context and link to old
        newCtx = MethodContext()
        newCtx.parent = oldCtx
        newCtx.receiver = recvObj
        newCtx.method = methObj
        
        # transfer control to new context
        self.i_context = newCtx

        
        
        
        
        