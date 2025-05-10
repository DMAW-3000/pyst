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
        self.i_this = self._nil
        self.i_context = self._nil
        self.i_method = self._nil
        self.i_temps = self._nil
        self.i_literals = self._nil
        
        # the bytecode table
        self.b_table = bTbl = [None] * 256
        
    def reset(self):
        """
        Prepare for execution
        """
        self.i_context = BlockContext(self._nil)
        
    def exe(self):
        """
        Start execution
        """
        oldCtx = self.i_context
        newCtx = MethodContext(oldCtx)
        
        