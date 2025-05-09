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
        self.k_hash_collection = None
        self.k_dictionary = None
        self.k_bind_dictionary = None
        self.k_abs_namespace = None
        self.k_namespace = None
        self.k_root_namespace = None
        self.k_sys_dictionary = None
        self.k_magnitude = None
        self.k_lookup_key = None
        self.k_assoc = None
        self.k_homed_assoc = None
        self.k_variable_bind = None
        
        # fundamental objects
        self.o_nil = None
        self.o_false = None
        self.o_true = None
        self.o_char = [None] * 256
    
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
        inst.g_sym_table = Array(512)
        inst.g_st_dict = stDict = Namespace(512)
        stDict._klass = inst.k_sys_dictionary
        stDict.name = inst.symbol_add("Smalltalk")
        inst.name_add_sym(stDict, "Smalltalk", stDict)
        inst.name_add_sym(stDict, "SymbolTable", inst.g_sym_table)
        inst.name_add_sym(stDict, "KernelInitialized", inst.o_false)
        
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
            inst.subclass_add(metaObj.superClass, metaObj)
            klassObj.name = inst.symbol_add(klassName)
            klassObj.methodDictionary = inst.o_nil
            
            """
            print("%s: %s %d %s %s %s" % (klassName,
                                 klassObj.name,
                                 klassObj.get_num_inst(), 
                                 klassObj.subClasses,
                                 klassObj.superClass,
                                 klassObj._klass))
            """
            
    def symbol_add(self, symName):
        """
        Add a new Symbol to the global symbol table if it
        does not already exist.
        """
        symTable = self.g_sym_table
        symObj = Symbol.from_str(symName)
        idx = hsh_seq(map(ord, symName)) & (symTable.size - 1)
        link = SymLink(symObj, symTable[idx])
        symTable[idx] = link
        return symObj
        
    def symbol_find(self, symName):
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
        return link  # nil
        
    def name_add_sym(self, dictObj, symName, itemObj):
        """
        Add an item to a Namespace instance using
        a newly created Symbol as the key.
        """
        symObj = self.symbol_add(symName)
        bind = VariableBinding(symObj, itemObj, self.o_nil)
        self.dict_add(dictObj, symObj, bind)
        
    def dict_add(self, dictObj, keyObj, itemObj):
        """
        Add an item to a Dictionary-like instance.
        """
        idx = self.dict_index(dictObj, keyObj)
        dictObj[idx] = Association(keyObj, itemObj)
        print(keyObj, idx)
        dictObj.tally += 1
        
    @staticmethod
    def dict_index(dictObj, keyObj):
        """
        Find the index for a key in a Dictionary-like instance
        """
        numInst = dictObj.get_class().get_num_inst()
        arrSize = dictObj.size - numInst
        mask = arrSize - 1
        idx = keyObj.hsh()
        for n in range(arrSize):
            idx &= mask
            assoc = dictObj[idx + numInst]
            if is_nil(assoc) or (assoc.key is keyObj):
                return idx + numInst
            idx += 1
        raise IndexError("Dictionary is too sma1l")
        
    @staticmethod
    def create_meta(instObj):
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
    
    @staticmethod
    def subclass_add(superObj, subObj):
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
        
        
        
        

            