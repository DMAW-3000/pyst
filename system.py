"""
The entire Smalltalk environment
"""

import pickle

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
        # manage the class covers
        self.cover_map = {}
        
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
        self.k_char_array = None
        self.k_string = None
        self.k_symbol = None
        
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
        # this establishes the Class tree.
        for klassInfo in init.Init_Class:
            klassName = klassInfo[0]
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
            
        # class intialization pass 2
        # set the class covers
        # After this point, Python cover classes have the right
        # Smalltalk type except the Class objects created above.
        metaInstVarNames = None
        for klassInfo in init.Init_Class:
            klassName = klassInfo[0]
            hasCover = klassInfo[1]
            cacheName = klassInfo[2]
            instVars = klassInfo[5]
            klassObj = getattr(inst, "k_" + cacheName)
            if hasCover and (klassObj is not inst.k_class):
                coverKlass = globals()[klassName]
                inst.cover_map[klassName] = coverKlass
                coverKlass.set_cover(klassObj)
            if klassObj is inst.k_class:
                metaInstVarNames = instVars
        
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
        inst.name_add_sym(stDict, "Version", String.from_str("1.0"))
        inst.name_add_sym(stDict, "Features", Array(1))
        inst.name_add_sym(stDict, "Undeclared", inst.o_nil)
        inst.name_add_sym(stDict, "SytemExceptions", stDict)
        
        # create Class metaclass and fixup
        klassObj = inst.k_class
        inst.create_meta(klassObj)
        klassObj.subClasses = Array(2)
        klassObj.subClasses[0] = 1
        
        # fixup Object parent nil link
        inst.k_object.superClass = inst.o_nil
        
        # class initialization pass 3
        # after this all of the Class objects are
        # correctly initialized
        for klassInfo in init.Init_Class:
            klassName = klassInfo[0]
            cacheName = klassInfo[2]
            instVars = klassInfo[5]
            klassObj = getattr(inst, "k_" + cacheName)
            metaObj = klassObj._klass
            if metaObj is None:
                metaObj = inst.create_meta(klassObj)
            superObj = klassObj.superClass
            if is_nil(superObj):
                metaObj.superClass = inst.k_class
            else:
                metaObj.superClass = superObj.get_class()
            inst.subclass_add(metaObj.superClass, metaObj)
            metaObj.instanceVariables = inst.create_inst_vars(inst.o_nil, init.Init_Meta_Vars)
            if not is_nil(superObj):
                inst.subclass_add(superObj, klassObj)
            klassObj.environment = inst.g_st_dict
            klassObj.instanceVariables = inst.create_inst_vars(superObj, instVars)
            klassObj.name = inst.symbol_add(klassName)
            klassObj.methodDictionary = inst.o_nil
            klassObj.comment = inst.o_nil
            klassObj.category = inst.o_nil
            klassObj.pragmaHandlers = inst.o_nil

        for klassInfo in init.Init_Class:
            cacheName = klassInfo[2]
            klassObj = getattr(inst, "k_" + cacheName)
            print("%s %s %s %s %s" % ( \
                                 klassObj.name,
                                 klassObj.instanceVariables, 
                                 klassObj.subClasses,
                                 klassObj.superClass,
                                 klassObj.get_class()))
            
            
        for s in inst.g_st_dict[5:]:
            if not is_nil(s):
                print(s.key, s.key.hsh() & 511, s.value.value)
        
    def symbol_add(self, symName):
        """
        Add a new Symbol to the global symbol table if it
        does not already exist.
        """
        symTable = self.g_sym_table
        symObj = Symbol.from_str(symName)
        idx = hsh_seq(map(ord, symName)) & (symTable.size - 1)
        symTable[idx] = SymLink(symObj, symTable[idx])
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
        
    def symbol_find_or_add(self, symName):
        """
        Returns a Symbol object, either already or existing
        or created and added to global symbol table.
        """
        symTable = self.g_sym_table
        idx = hsh_seq(map(ord, symName)) & (symTable.size - 1)
        link = symTable[idx]
        while not is_nil(link):
            if symName == link.symbol.to_str():
                return link.symbol
            link = link.nextLink
        symObj = Symbol.from_str(symName)
        symTable[idx] = SymLink(symObj, symTable[idx])
        return symObj
        
    def name_add_sym(self, dictObj, symName, itemObj):
        """
        Add an item to a Namespace instance using
        a newly created Symbol as the key.
        """
        symObj = self.symbol_add(symName)
        bind = VariableBinding(symObj, itemObj, dictObj)
        self.dict_add(dictObj, symObj, bind)
        
    def dict_add(self, dictObj, keyObj, itemObj):
        """
        Add an item to a Dictionary-like instance.
        """
        idx = self.dict_index(dictObj, keyObj)
        dictObj[idx] = Association(keyObj, itemObj)
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
        n = 0
        while n < arrSize:
            idx &= mask
            assoc = dictObj[idx + numInst]
            if is_nil(assoc) or (keyObj.is_same(assoc.value)):
                return idx + numInst
            idx += 1
            n += 1
        raise IndexError("Dictionary is too sma1l")
        
    @staticmethod
    def create_meta(instObj):
        """
        Create a Metaclass and link it with instance Class
        Also create the subclass arrays in both objects
        so that they match up.  Returns the new Metaclass
        object.
        """
        metaObj = Metaclass(instObj)
        instObj._klass = metaObj
        numSubclass = instObj.subClasses
        if numSubclass > 0:
            metaObj.subClasses = Array(numSubclass)
            metaObj.subClasses[0] = numSubclass
            instObj.subClasses = Array(numSubclass)
            instObj.subClasses[0] = numSubclass
        return metaObj
    
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
        else:
            numSuper = superObj.instanceVariables.size
        numInst = len(varNames)
        numVar = numSuper + numInst
        if numVar == 0:
            return self.o_nil
        arrObj = Array(numSuper + numInst)
        for n,s in enumerate(varNames):
            symObj = self.symbol_find_or_add(s)
            arrObj[numSuper + n] = symObj
        return arrObj
        
        
        
        

            