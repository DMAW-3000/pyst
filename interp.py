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
        self._sys = system
        self._nil = system.o_nil
        
        self.i_this = self._nil
        self.i_context = self._nil
        self.i_method = self._nil
        self.i_temps = self._nil
        self.i_literals = self._nil
        
    def run(self):
        """
        Start execution
        """
        self.i_context = BlockContext(self._nil)