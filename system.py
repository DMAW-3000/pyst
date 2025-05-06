"""
The entire Smalltalk environment
"""

from st import *

class Smalltalk(object):
    """
    The Smalltalk system state
    """
    
    _SmalltalkInstance = None
    
    def __init__(self):
        """
        Create a blank Smalltalk environment
        """
        # global dictionaries
        self._st_dict = None
        self._sym_table = None
        
        # cached class definitions
        self.k_object = None
        self.k_undef_obj = None
        self.k_boolean = None
        self.k_true = None
        self.k_false = None
        self.k_behavior = None
        self.k_class_desc = None
        
    @classmethod
    def get_smalltalk(klass):
        """
        Get a reference to the Smalltalk instance
        """
        return klass._SmalltalkInstance
    
    @classmethod
    def rebuild(klass):
        """
        Create a fresh Smalltalk enviroment from scratch
        """
        import init
        
        klass._SmalltalkInstance = inst = klass()
        
        # create global dictionaries
        inst._st_dict = Dictionary(64)
        inst._sym_table = Dictionary(64)
            
        # class initialization pass 1
        for klassInfo in init.Init_Class:
            klassName = klassInfo[0]
            cacheName = klassInfo[1]
            superName = klassInfo[2]
            isFixed = klassInfo[3]
            instVars = klassInfo[4]
            if superName is not None:
                superObj = getattr(inst, "k_" + superName)
                superVars = superObj.get_num_inst()
            else:
                superObj = None
                superVars = 0
            klassObj = Class(superObj, len(instVars) + superVars, isFixed)
            klassObj.subClasses = 0
            if superObj is not None:
                superObj.subClasses += 1
            setattr(inst, "k_" + cacheName, klassObj)
            inst.add_symbol(klassName)
            
        return inst
            
    def add_symbol(self, name):
        """
        Add a new Symbol to the global symbol table
        """
        symObj = Symbol.from_str(name)
        linkObj = SymLink(symObj, self._sym_table.get(symObj))
        self._sym_table.add(symObj, linkObj)
        

            