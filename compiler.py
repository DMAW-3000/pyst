"""
Smalltalk bootstrap compiler
"""

class Compile(object):

    def __init__(self, system):
        """
        Create a blank compiler instance
        """
        # cache system information
        self._sys = system

        