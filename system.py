"""
The entire Smalltalk environment
"""

import os
import pickle

from st import *
from compiler import Compile
from interp import Interp
import init


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
        self.g_cover_map = weakref.WeakValueDictionary()
        
        # global dictionaries
        self.e_st_dict = None
        self.e_sym_table = None
        
        # cached class definitions
        self.k_object = None
        self.k_undef_obj = None
        self.k_boolean = None
        self.k_true = None
        self.k_false = None
        self.k_exception = None
        self.k_behavior = None
        self.k_class_desc = None
        self.k_class = None
        self.k_metaclass = None
        self.k_iterable = None
        self.k_collection = None
        self.k_seq_collection = None
        self.k_arr_collection = None
        self.k_array = None
        self.k_bytearray = None
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
        self.k_stream = None
        self.k_pos_stream = None
        self.k_read_stream = None
        self.k_write_stream = None
        self.k_number = None
        self.k_integer = None
        self.k_small_int = None
        self.k_float = None
        self.k_float_d = None
        self.k_character = None
        self.k_context_part = None
        self.k_blk_context = None
        self.k_meth_context = None
        self.k_blk_closure = None
        self.k_comp_code = None
        self.k_comp_method = None
        self.k_comp_block = None
        self.k_meth_info = None
        self.k_lookup_table = None
        self.k_ident_dictionary = None
        self.k_meth_dictionary = None
        self.k_test = None
        
        # fundamental objects
        self.o_nil = None
        self.o_false = None
        self.o_true = None
        self.o_char = [None] * 256
        
        # global environment
        self.e_sym_table = None
        self.e_st_dict = None
        
        # interpeter and compiler
        self.g_compile = None
        self.g_interp = None
        
        # debug support
        self.d_save = None
        self.d_breakpoint = None
        
        # bytecode disassembly table
        # each entry is (name, num_arg)
        self.g_dis = [None] * 256
    
    @classmethod
    def rebuild(klass, verbose, brkpoint):
        """
        Create a fresh Smalltalk enviroment from scratch
        """
        inst = klass._SmalltalkInstance
            
        # Class initialization pass 1
        # this establishes the Class tree.
        inst.build_classes_1()
            
        # class intialization pass 2
        # set the class covers
        # After this point, Python cover classes have the right
        # Smalltalk type except the Class objects created above.
        inst.build_classes_2()
        
        # create Smalltalk Nil singleton
        inst.o_nil = UndefinedObject()
        
        # set object global Nil so covers created
        # after this point use Smalltalk Nil instead
        # of Python None
        set_obj_nil(inst.o_nil)
        
        # create Smalltalk Boolean singletons
        inst.o_false = CFalse()
        inst.o_true = CTrue()
        
        # create Smalltalk Character singletons
        for n in range(256):
            inst.o_char[n] = Character(n)
        set_obj_char(inst.o_char)
        
        # create global symbol table
        inst.e_sym_table = Array(512)
        
        # create the global namespace dictionary ("Smalltalk")
        inst.e_st_dict = stDict = Namespace.new_n(512)
        stDict._klass = inst.k_sys_dictionary
        sym = inst.name_add_sym(stDict, "Smalltalk", stDict)
        stDict.name = sym
        
        # add global objects
        inst.name_add_sym(stDict, "SymbolTable", inst.e_sym_table)
        inst.name_add_sym(stDict, "KernelInitialized", inst.o_false)
        inst.name_add_sym(stDict, "Version", String.from_str("0.1"))
        inst.name_add_sym(stDict, "Features", Array(1))
        inst.name_add_sym(stDict, "Undeclared", Namespace.new_n(32))
        inst.name_add_sym(stDict, "SytemExceptions", stDict)
        
        # finalize class build
        # after this point, the class cache attributes are weakrefs
        inst.build_classes_3()
        
        # generate disassembly info
        inst.build_disassembly()
            
        # initialize runtime objects
        inst.name_add_sym(inst.e_st_dict, "Bigendian", inst.o_false)
        
        # initialize interpreter
        inst.g_interp = Interp(inst)
        
        # seetup requested debug options
        if brkpoint is not None:
            # break at [Class, method]
            inst.d_breakpoint = brkpoint
            inst.d_save = inst.g_interp.get_debug()
            inst.g_interp.set_debug(inst.break_hook_pre, inst.d_save[1])
        
        # initialize primitive ops
        inst.build_primitives(verbose)
        
        # compile the Kernel modules
        inst.g_compile = Compile(inst, verbose)
        for mod in init.Init_Kernel_Mod:
            print("Compiling module ", mod)
            inst.g_compile.parse_file(os.path.join("Kernel", mod))
        
        # dump information
        if verbose:
            print("Smalltalk Dictionary:")
            inst.dict_print(inst.e_st_dict, True)
            print()
            
            print("Symbol Table:")
            inst.symbol_tbl_print()
            print()
            
            print("Class Init Info:")
            for klassInfo in init.Init_Class:
                cacheName = klassInfo[2]
                klassObj = getattr(inst, "k_" + cacheName)()
                print("%s %s %s %s %s" % ( \
                                 klassObj.name,
                                 klassObj.instanceVariables, 
                                 klassObj.subClasses,
                                 klassObj.superClass,
                                 klassObj.classVariables))
            print()
            
        # static class initialization
        for klassName in init.Init_Class_Init:
            klassSym = inst.symbol_find(klassName)
            klassObj = inst.dict_find(inst.e_st_dict, klassSym).value.value
            print("Initializing class", klassSym)
            inst.g_interp.send_message_extern(klassObj, "initialize", ())
        
    
    @classmethod
    def run(klass):
        inst = klass._SmalltalkInstance
        testObj = inst.g_interp.send_message_extern(inst.k_test(), "new", ())
        result = inst.g_interp.send_message_extern(testObj, "runAll", ())
        print()
        print(result)
        
    def build_classes_1(self):
        """
        Class rebuild
        """
        for klassInfo in init.Init_Class:
            klassName = klassInfo[0]
            cacheName = klassInfo[2]
            superName = klassInfo[3]
            isFixed = klassInfo[4]
            instVars = klassInfo[5]
            if superName is not None:
                superName = "k_" + superName
                if not hasattr(self, superName):
                    self.fatal_err("missing class cache", superName)
                superObj = getattr(self, superName)
                superVars = superObj.get_num_inst()
            else:
                superObj = None
                superVars = 0
            klassObj = Class(superObj, len(instVars) + superVars, isFixed)
            klassObj.subClasses = 0
            if superObj is not None:
                superObj.subClasses += 1
            cacheName = "k_" + cacheName
            if not hasattr(self, cacheName):
                self.fatal_err("missing class cache", cacheName)
            setattr(self, cacheName, klassObj)
            
    def build_classes_2(self):
        """
        Class rebuild
        """
        metaInstVarNames = None
        for klassInfo in init.Init_Class:
            klassName = klassInfo[0]
            hasCover = klassInfo[1]
            cacheName = klassInfo[2]
            instVars = klassInfo[5]
            klassObj = getattr(self, "k_" + cacheName)
            if hasCover and (klassObj is not self.k_class):
                coverKlass = globals()[klassName]
                self.g_cover_map[klassName] = coverKlass
                coverKlass.set_cover(klassObj)
            if klassObj is self.k_class:
                metaInstVarNames = instVars
        self.g_cover_map["False"] = self.k_false
        CFalse.set_cover(self.k_false)
        self.g_cover_map["True"] = self.k_true
        CTrue.set_cover(self.k_true)
                
    def build_classes_3(self):
        """
        Class rebuild
        """
        # create Class metaclass and fixup
        klassObj = self.k_class
        self.create_meta(klassObj)
        klassObj.subClasses = Array(2)
        klassObj.subClasses[0] = 1
        
        # fixup Object parent nil link
        self.k_object.superClass = self.o_nil
        
        # class initialization pass 3
        # after this all of the Class objects are
        # correctly initialized
        for klassInfo in init.Init_Class:
            klassName = klassInfo[0]
            cacheName = klassInfo[2]
            instVars = klassInfo[5]
            classVars = klassInfo[6]
            poolNames = klassInfo[7]
            klassObj = getattr(self, "k_" + cacheName)
            metaObj = klassObj._klass
            if metaObj is None:
                metaObj = self.create_meta(klassObj)
            superObj = klassObj.superClass
            if superObj.is_nil():
                metaObj.superClass = self.k_class
            else:
                metaObj.superClass = superObj.get_class()
            self.subclass_add(metaObj.superClass, metaObj)
            metaObj.instanceVariables = self.create_inst_vars(self.o_nil, init.Init_Meta_Vars)
            if not superObj.is_nil():
                self.subclass_add(superObj, klassObj)
            metaObj.methodDictioary = self.o_nil
            klassObj.environment = self.e_st_dict
            klassObj.instanceVariables = self.create_inst_vars(superObj, instVars)
            klassObj.classVariables = self.create_class_vars(klassObj, classVars)
            klassObj.sharedPools = self.create_shared_pools(poolNames)
            klassObj.methodDictionary = self.o_nil
            klassObj.comment = self.o_nil
            klassObj.category = self.o_nil
            klassObj.pragmaHandlers = self.o_nil
            klassObj.name = self.name_add_sym(self.e_st_dict, klassName, klassObj)
            setattr(self, "k_" + cacheName, weakref.ref(klassObj))
    
    def build_disassembly(self):
        """
        Create info needed for disassembly.  Each entry is a tuple:
        0 = bytecode name
        1 = number bytes
        2 = number of parameters
        """
        disTbl = self.g_dis
        disTbl[B_PUSH_SELF]                 = ("PUSH_SELF", 2, 0)
        disTbl[B_RETURN_METHOD_STACK_TOP]   = ("RETURN_METHOD", 2, 0)
        disTbl[B_RETURN_CONTEXT_STACK_TOP]  = ("RETURN_CONTEXT", 2, 0)
        disTbl[B_PUSH_LIT_VARIABLE]         = ("PUSH_LIT_VARIABLE", 2, 1)
        disTbl[B_PUSH_LIT_CONSTANT]         = ("PUSH_LIT_CONSTANT", 2, 1)
        disTbl[B_SEND]                      = ("SEND", 2, 1)
        disTbl[B_SEND_SUPER]                = ("SEND_SUPER", 2, 1)
        disTbl[B_POP_STACK_TOP]             = ("POP_STACK_TOP", 2, 0)
        disTbl[B_DUP_STACK_TOP]             = ("DUP_STACK_TOP", 2, 0)
        disTbl[B_PUSH_TEMPORARY_VARIABLE]   = ("PUSH_TEMP_VARIABLE", 2, 1)
        disTbl[B_PUSH_OUTER_TEMP]           = ("PUSH_OUTER_VARIABLE", 4, 2)
        disTbl[B_PUSH_RECEIVER_VARIABLE]    = ("PUSH_RECV_VARIABLE", 2, 1)
        disTbl[B_PUSH_INTEGER]              = ("PUSH_INTEGER", 2, 1)
        disTbl[B_PUSH_SPECIAL]              = ("PUSH_SPECIAL", 2, 0)
        disTbl[B_STORE_LIT_VARIABLE]        = ("STORE_LIT_VARIABLE", 2, 1)
        disTbl[B_STORE_TEMPORARY_VARIABLE]  = ("STORE_TEMP_VARIABLE", 2, 1)
        disTbl[B_STORE_RECEIVER_VARIABLE]   = ("STORE_RECV_VARIABLE", 2, 1)
        disTbl[B_STORE_OUTER_TEMP]          = ("STORE_OUTER_VARIABLE", 4, 2)
        disTbl[B_VALUE_SPECIAL]             = ("SEND_SPECIAL_VALUE", 2, 1)
        disTbl[B_SIZE_SPECIAL]              = ("SEND_SPECIAL_SIZE", 2, 1)
        disTbl[B_IS_NIL_SPECIAL]            = ("SEND_SPECIAL_ISNIL", 2, 1)
        disTbl[B_NOT_NIL_SPECIAL]           = ("SEND_SPECIAL_NOTNIL", 2, 1)
        disTbl[B_CLASS_SPECIAL]             = ("SEND_SPECIAL_CLASS", 2, 1)
        disTbl[B_AT_SPECIAL]                = ("SEND_SPECIAL_AT", 2, 1)
        disTbl[B_AT_PUT_SPECIAL]            = ("SEND_SPECIAL_AT_PUT", 2, 1)
        disTbl[B_VALUE_COLON_SPECIAL]       = ("SEND_SPECIAL_VALUE_COLON", 2, 1)
        disTbl[B_PLUS_SPECIAL]              = ("SEND_SPECIAL_PLUS", 2, 1)
        disTbl[B_MINUS_SPECIAL]             = ("SEND_SPECIAL_MINUS", 2, 1)
        disTbl[B_LESS_THAN_SPECIAL]         = ("SEND_SPECIAL_LESS_THAN", 2, 1)
        disTbl[B_GREATER_THAN_SPECIAL]      = ("SEND_SPECIAL_GREATER_THAN", 2, 1)
        disTbl[B_LESS_EQUAL_SPECIAL]        = ("SEND_SPECIAL_LESS_EQU", 2, 1)
    
    def build_primitives(self, verbose):
        """
        Create the primitives dictionary and register ops with
        interpreter.
        """
        primDict = BindingDictionary.new_n(512)
        primDict.environment = self.e_st_dict
        self.name_add_sym(self.e_st_dict, "VMPrimitives", primDict)
        for primId,primName in enumerate(init.Init_Primitive):
            primId += 1     # 0 is reserved
            if not self.g_interp.add_primitive(primName):
                self.fatal_err("cannot find primitive handler", primName)
            symObj = self.symbol_find_or_add("VMpr_" + primName)
            self.dict_add(primDict, symObj, primId)
        if verbose:
            print("VM Primitives:")
            self.dict_print(primDict)
            print()
        
    def symbol_find(self, symName):
        """
        Returns a Symbol object if name is found in global
        symbol table, nil otherwise.
        """
        symTable = self.e_sym_table 
        link = symTable[hsh_seq(map(ord, symName)) & (symTable.size - 1)]
        while not link.is_nil():
            if symName == link.symbol.to_str():
                return link.symbol
            link = link.nextLink
        return link  # nil
        
    def symbol_find_or_add(self, symName):
        """
        Returns a Symbol object, either already existing
        or new one created and added to global symbol table.
        """
        symTable = self.e_sym_table
        idx = hsh_seq(map(ord, symName)) & (symTable.size - 1)
        link = symTable[idx]
        while not link.is_nil():
            if symName == link.symbol.to_str():
                return link.symbol
            link = link.nextLink
        symObj = Symbol.from_str(symName)
        symTable[idx] = SymLink(symObj, symTable[idx])
        return symObj
        
    def symbol_tbl_print(self):
        """
        Print contents of global symbol table.
        """
        symTable = self.e_sym_table 
        for n,link in enumerate(symTable):
            print("[%d]" % n, end = "")
            while not link.is_nil():
                print(link.symbol, end = " ")
                link = link.nextLink
            print()
        
    def name_add_sym(self, dictObj, symName, itemObj):
        """
        Add an item to a Namespace instance using
        a newly created Symbol as the key.
        """
        symObj = self.symbol_find_or_add(symName)
        self.dict_add(dictObj, symObj, VariableBinding(symObj, itemObj, dictObj))
        return symObj
        
    def find_global(self, itemName):
        """
        Find a global symbol value in the Smalltalk namespace.
        Returns VariableBinding, or nil if not found.
        """
        symObj = self.symbol_find(itemName)
        if symObj.is_nil():
            return symObj
        assoc = self.dict_find(self.e_st_dict, symObj)
        if assoc.is_nil():
            return assoc
        return assoc.value
        
    def dict_add(self, dictObj, keyObj, itemObj):
        """
        Add an item to a Dictionary-like instance.
        """
        tly = dictObj.tally
        if tly / dictObj.size > 0.4:
            self.dict_grow(dictObj)
        idx = self.dict_index(dictObj, keyObj)
        if dictObj[idx].is_nil():
            dictObj[idx] = Association(keyObj, itemObj)
            dictObj.tally = tly + 1
        else:
            raise NameError("duplicate Dictionary key: %s" % keyObj)
        
    def dict_find(self, dictObj, keyObj):
        """
        Find an item in a Dictionary-like instance.
        Returns the Association, or nil.
        """ 
        return dictObj[self.dict_index(dictObj, keyObj)]
        
    @staticmethod
    def dict_index(dictObj, keyObj):
        """
        Find the index for a key in a Dictionary-like instance
        """
        numInst = dictObj.get_class().get_num_inst()
        arrSize = dictObj.size - numInst
        mask = arrSize - 1
        idx = hsh_scram(keyObj.get_id()) 
        while arrSize:
            idx &= mask
            assoc = dictObj[idx + numInst]
            if assoc.is_nil() or keyObj.is_same(assoc.key):
                return idx + numInst
            idx += 1
            arrSize -= 1
        raise IndexError("Dictionary overflow")
        
    def dict_grow(self, dictObj):
        """
        Increase the capacity of a Dictionary-like object
        and re-hash the items.
        """
        numInst = dictObj.get_class().get_num_inst()
        oldArrSize = dictObj.size - numInst
        oldDict = copy(dictObj._refs)
        dictObj.resize((oldArrSize << 1) + numInst)
        for n,r in enumerate(oldDict[:numInst]):
            dictObj[n] = r
        for assoc in oldDict[numInst:]:
            if not assoc.is_nil(): 
                dictObj[self.dict_index(dictObj, assoc.key)] = assoc
        
    @staticmethod
    def dict_print(dictObj, nameSpace = False):
        """
        Display the contents of a Dictionary-like object
        """
        numInst = dictObj.get_class().get_num_inst()
        print("Tally: %d (%d)" % (dictObj.tally, dictObj.size - numInst))
        for n,assoc in enumerate(dictObj[numInst:]):
            if not nameSpace:
                if not assoc.is_nil():
                    print("[%d]" % n, assoc.key, assoc.value)
            else:
                if not assoc.is_nil():
                    binding = assoc.value
                    if not binding.is_nil():
                        print("[%d]" % n, binding.key, binding.value)
                        
    def identdict_add(self, dictObj, keyObj, itemObj):
        """
        Add an item to a IdentityDictionary-like instance.
        """
        tly = dictObj.tally
        if tly / (dictObj.size >> 1) > 0.4:
            self.identdict_grow(dictObj)
        idx = self.identdict_index(dictObj, keyObj)
        if dictObj[idx].is_nil():
            dictObj[idx - 1] = keyObj
            dictObj[idx] = itemObj
            dictObj.tally = tly + 1
        else:
            raise NameError("duplicate IdentityDictionary key: %s" % keyObj)
        
    def identdict_find(self, dictObj, keyObj):
        """
        Find an item in an IdentityDictionary-like instance,
        or nil if not found.
        """
        return dictObj[self.identdict_index(dictObj, keyObj)]
                        
    @staticmethod
    def identdict_index(dictObj, keyObj):
        """
        Find the index for a key in a IdentityDictionary-like 
        instance
        """
        global Int_Max
        numInst = dictObj.get_class().get_num_inst()
        arrSize = dictObj.size - numInst
        idx = (hsh_scram(keyObj.get_id()) << 1) & Int_Max
        mask = arrSize - 1
        arrSize >>= 1
        while arrSize:
            idx &= mask
            item = dictObj[idx + numInst]
            if item.is_nil() or item.is_same(keyObj):
                return idx + numInst + 1
            idx += 2
            arrSize -= 1
        raise IndexError("IdentityDictionary overflow")
        
    def identdict_grow(self, dictObj):
        """
        Increase the capacity of a IdentityDictionary-like object
        and re-hash the items.
        """
        numInst = dictObj.get_class().get_num_inst()
        oldArrSize = dictObj.size - numInst
        oldDict = copy(dictObj._refs)
        dictObj.resize((oldArrSize << 1) + numInst)
        for n,r in enumerate(oldDict[:numInst]):
            dictObj[n] = r
        for n,key in enumerate(oldDict[numInst::2]):
            if not key.is_nil():
                idx = self.identdict_index(dictObj, key)
                dictObj[idx - 1] = key
                dictObj[idx] = oldDict[(n << 1) + numInst + 1]
        
    @staticmethod
    def identdict_print(dictObj):
        """
        Display the contents of a IdentityDictionary-like object
        """
        numInst = dictObj.get_class().get_num_inst()
        print("Tally: %d (%d)" % (dictObj.tally, (dictObj.size - numInst) >> 1))
        for n,key in enumerate(dictObj[numInst::2]):
            if not key.is_nil():
                print("[%d]" % n, key, dictObj[(n << 1) + numInst + 1])
                        
    @staticmethod
    def arr_print(arrObj):
        """
        Display the contents of an Array-like object
        """
        for n,x in enumerate(arrObj):
            print("[%d]" % n, x)
        
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
        if superObj.is_nil():
            numSuper = 0
        else:
            if superObj.instanceVariables.is_nil():
                numSuper = 0
            else:
                numSuper = superObj.instanceVariables.size
        numInst = len(varNames)
        numVar = numSuper + numInst
        if numVar == 0:
            return self.o_nil
        arrObj = Array(numVar)
        for n in range(numSuper):
            arrObj[n] = superObj.instanceVariables[n]
        for n,s in enumerate(varNames):
            arrObj[numSuper + n] = String.from_str(s)
        return arrObj
        
    def create_class_vars(self, klassObj, varNames):
        """
        Create the BindingDictionary for holding the class
        variable values.
        """
        if len(varNames) == 0:
            return self.o_nil
        bindDict = BindingDictionary.new_n(8)
        bindDict.environment = klassObj
        for s in varNames:
            symObj = self.symbol_find_or_add(s)
            self.dict_add(bindDict, symObj, self.o_nil)
        return bindDict
        
    def create_shared_pools(self, poolNames):
        """
        Create the Array of share pools for a class
        """
        numPool = len(poolNames)
        if numPool == 0:
            return self.o_nil
        arrObj = Array(numPool)
        return arrObj
        
    def dis_bytecode(self, byteCode):
        """
        Disassemble an array of bytecode values and
        display the results.
        """
        n = 0
        while n < len(byteCode):
            info = self.g_dis[byteCode[n]]
            if info is None:
               info = ("????", 2, 0)
            prList = ["[%d]" % n, info[0]]
            for k in range(info[2]):
                prList.append(byteCode[n + (k * 2) + 1])
            print(*prList)
            n += info[1]
            
    def dis_byte(self, b):
        """
        Disassemble a single byte opcode and resturn
        the result as a str.
        """
        info = self.g_dis[b]
        if info is None:
            prStr = "????"
        else:
            prStr = info[0]
        return prStr
        
    def break_hook_pre(self):
        """
        Check for breakpoints before execution
        """
        # get current context
        ctx = self.g_interp.i_context
        
        # check for method context and get name
        methObj = ctx.method
        if (ctx.ip != 0) or methObj.is_nil() or (not is_int(ctx[6])):
            return
        descObj = methObj.descriptor
        methName = descObj.selector
        klassName = descObj.klass.name
        if (klassName.to_str() == self.d_breakpoint[0]) and \
           (methName.to_str() == self.d_breakpoint[1]):
            # switch to debug hooks
            print("BREAK: ", klassName, methName)
            print()
            self.d_save = self.g_interp.get_debug()
            self.g_interp.set_debug(self.debug_hook_pre, self.debug_hook_post)
            self.debug_hook_pre()
        
    def debug_hook_pre(self):
        """
        Debug bytecode before execution
        """
        self.context_print_byte()
        self.debug_user_input()
        
    def debug_hook_post(self):
        """
        Debug bytecode after execution
        """
        self.context_print_state(self.g_interp.i_context)
        print()
        
    def debug_user_input(self):
        """
        Get user input and process debugger command
        """
        while True:
            line = input(">>")
            if len(line) < 1:
                print()
                continue
            c = line.split()[0]
            if c == 's':
                break
            elif c == 'c':
                self.g_interp.set_debug(*self.d_save)
                break
            elif c == 'd':
                print()
                self.context_print_byte()
                print()
            elif c == 'i':
                ctx = self.g_interp.i_context
                if ctx.size <= 7:
                    print("STACK EMPTY")
                else:
                    print()
                    if is_obj(ctx[-1]):
                        self.object_print_state(ctx[-1])
                    else:
                        print("Primitive: ", str(ctx[-1]))
                    print()
            elif c == 'x':
                print()
                self.context_print_state(self.g_interp.i_context)
                print()
            elif c == 'p':
                parent = self.g_interp.i_context.parent
                print()
                if not parent.is_nil():
                    self.context_print_state(parent)
                else:
                    print("ROOT CONTEXT")
                print()
            elif c == 'h':
                print("s = step")
                print("c = continue")
                print("d = disassemble current bytecode")
                print("h = help")
                print("i = inspect stack top object")
                print("q = quit immediately")
                print("x = examine context")
                print()
            elif c == 'q':
                sys.exit(0)
            else:
                print("???\n")
                
    def context_print_byte(self):
        """
        Display the next bytecode to be executed in the current
        context.
        """
        ctx = self.g_interp.i_context
        ip = ctx.ip
        code = ctx.method.get_code()
        if not is_int(ctx[6]):
            desc =  ctx.method.method.descriptor
            selName = "%s[Block]" % desc.selector
        else:
            desc = ctx.method.descriptor
            selName = desc.selector
        klassName = desc.klass
        print("<%s> %s[%d]:" % (klassName, selName, ip), self.dis_byte(code[ip]))
    
    @staticmethod
    def context_print_state(ctx):
        """
        Display the state of the context
        """
        meth = ctx.method
        if meth.is_nil():
            methName = meth
        else:
            if not is_int(ctx[6]):
                methName = "Block<%s>" % meth.method.descriptor.selector
            else:
                methName = meth.descriptor.selector
        print("Method:", methName, "[%d]" % ctx.ip)
        print("Recv:", ctx.receiver)
        if not meth.is_nil():
            numTemp = meth.get_num_arg() + meth.get_num_temp()
            if numTemp > 0:
                print("Temps (%d):" % numTemp)
                for n,r in enumerate(ctx[7 : 7 + numTemp]):
                    print("[%d]" % n, r)
        else:
            numTemp = 0
        print("\nStack (%d):" % (ctx.sp - (6 + numTemp),))
        for n,r in enumerate(ctx[7 + numTemp:]):
            print("[%d]" % n, r)
        
    def object_print_state(self, obj):
        """
        Print the state of an object
        """
        print(str(obj.get_class()))
        print("ID:    ", obj.get_id())
        print("Flags: ", obj._flags)
        print("Cache: ", obj._py_cache)
        print("Size:  ", obj.size)
        if obj.size > 0:
            self.arr_print(obj)
        
    def fatal_err(self, *s):
        """
        Print a message and exit.  None of the
        system state will be saved.
        """
        print("ERROR:", *s)
        sys.exit(-1)
            
        
Smalltalk._SmalltalkInstance = Smalltalk()

            