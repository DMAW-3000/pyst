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
        self.g_st_dict = None
        self.g_sym_table = None
        
        # cached class definitions
        self.k_object = None
        self.k_undef_obj = None
        self.k_boolean = None
        self.k_true = None
        self.k_false = None
        self.k_behavior = None
        self.k_class_desc = None
        self.k_class = None
        self.k_metaclass = None
        self.k_link = None
        self.k_sym_link = None
        
        # fundamental objects
        self.o_nil = None
        self.o_false = None
        self.o_true = None
        self.o_char = [None] * 256
        
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
        
        # create empty system
        klass._SmalltalkInstance = inst = klass()
            
        # Class initialization pass 1
        # this establishes the Class tree and
        # set the cover classes for those Classes that have them.
        # After this point, Python cover classes have the right
        # Smalltalk type.
        for klassInfo in init.Init_Class:
            klassName = klassInfo[0]
            hasCover = klassInfo[1]
            cacheName = klassInfo[2]
            superName = klassInfo[3]
            isFixed = klassInfo[4]
            instVars = klassInfo[5]
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
            if hasCover:
                coverKlass = globals()[klassName]
                coverKlass.set_cover(klassObj)
                
        # create Class metaclass and fixup
        klassObj = inst.k_class
        inst.create_meta(klassObj)
        klassObj._klass = klassObj
        klassObj.subClasses = Array(2)
        klassObj.subClasses[0] = 1
        
        # create Smalltalk Nil singleton
        inst.o_nil = UndefinedObject()
        
        # set object global Nil so covers created
        # after this point use Smalltalk Nil instead
        # of Python None
        set_obj_nil(inst.o_nil)
        
        # create Smalltalk Boolean singletons
        inst.o_false = CFalse()
        inst.o_true = CTrue()
        
        # create global dictionaries
        inst.g_st_dict = Namespace(64)
        inst.g_sym_table = Array(512)
        
        # class initialization pass 2
        for klassInfo in init.Init_Class:
            klassName = klassInfo[0]
            cacheName = klassInfo[2]
            klassObj = getattr(inst, "k_" + cacheName)
            if klassObj is not inst.k_class:
                inst.create_meta(klassObj)
            metaObj = klassObj._klass
            superObj = klassObj.superClass
            if superObj is not None:
                metaObj.superClass = superObj
            else:
                metaObj.superClass = inst.k_class
                klassObj.superClass = inst.o_nil
            inst.add_subclass(metaObj.superClass, metaObj)
            inst.add_symbol(klassName)
            klassObj.methodDictionary = inst.o_nil
                
            print("%s: %d %s %s %s" % (klassName, 
                                 klassObj.get_num_inst(), 
                                 klassObj.subClasses,
                                 klassObj.superClass,
                                 klassObj._klass))
            
        return inst
            
    def add_symbol(self, symName):
        """
        Add a new Symbol to the global symbol table if it
        does not already exist.
        """
        if is_nil(self.find_symbol(symName)):
            symTable = self.g_sym_table
            symObj = Symbol.from_str(symName)
            idx = symObj.hsh() & (symTable.size - 1)
            link = SymLink(symObj, symTable[idx])
            symTable[idx] = link
        
    def find_symbol(self, symName):
        """
        Returns a Symbol object if name is found in global
        symbol table, Nil otherwise.
        """
        symTable = self.g_sym_table 
        link = symTable[hsh_seq(map(ord, symName)) & (symTable.size - 1)]
        while not is_nil(link):
            if symName == link.symbol.to_str():
                return link.symbol
            link = link.nextLink
        return link
        
    def create_meta(self, instObj):
        """
        Create a Metaclass and link it with instance Class
        Also create the subclass arrays in both objects
        so that they match up.
        """
        metaObj = Metaclass(instObj)
        instObj._klass = metaObj
        numSubclass = instObj.subClasses
        if numSubclass > 0:
            metaObj.subClasses = Array(numSubclass)
            metaObj.subClasses[0] = numSubclass
            instObj.subClasses = Array(numSubclass)
            instObj.subClasses[0] = numSubclass
            
    def add_subclass(self, superObj, subObj):
        """
        Add a subclass to a class
        """
        subArray = superObj.subClasses
        idx = subArray[0] - 1
        subArray[0] = idx
        subArray[idx] = subObj
        
    def create_inst_vars(self, superObj, varNames):
        """
        Create the Array for holding instance variables
        """
        
        if is_nil(superObj):
            numSuper = 0
        
        
        
        

            