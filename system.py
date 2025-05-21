"""
The entire Smalltalk environment
"""

import sys
import os
import pickle
from copy import copy

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
        self.g_cover_map = {}
        
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
        self.k_iterable = None
        self.k_collection = None
        self.k_seq_collection = None
        self.k_arr_collection = None
        self.k_array = None
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
        self.k_number = None
        self.k_integer = None
        self.k_small_int = None
        self.k_context_part = None
        self.k_blk_context = None
        self.k_meth_context = None
        self.k_comp_code = None
        self.k_comp_method = None
        self.k_meth_info = None
        self.k_lookup_table = None
        self.k_ident_dictionary = None
        self.k_meth_dictionary = None
        
        # fundamental objects
        self.o_nil = None
        self.o_false = None
        self.o_true = None
        self.o_char = [None] * 256
        
        # interpeter and compiler
        self.g_compile = None
        self.g_interp = None
        
        # bytecode disassembly table
        # each entry is (name, num_arg)
        self.g_dis = [None] * 256
    
    @classmethod
    def rebuild(klass, debug):
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
        
        # create global symbol table
        inst.g_sym_table = Array(512)
        
        # create the global namespace dictionary ("Smalltalk")
        inst.g_st_dict = stDict = Namespace.new_n(512)
        stDict._klass = inst.k_sys_dictionary
        stDict.name = inst.symbol_add("Smalltalk")
        inst.name_add_sym(stDict, stDict.name.to_str(), stDict)
        
        # add global objects
        inst.name_add_sym(stDict, "SymbolTable", inst.g_sym_table)
        inst.name_add_sym(stDict, "KernelInitialized", inst.o_false)
        inst.name_add_sym(stDict, "Version", String.from_str("1.0"))
        inst.name_add_sym(stDict, "Features", Array(1))
        inst.name_add_sym(stDict, "Undeclared", Namespace.new_n(32))
        inst.name_add_sym(stDict, "SytemExceptions", stDict)
        
        # finalize class build
        inst.build_classes_3()
        
        # generate disassembly info
        inst.build_disassembly()
            
        # initialize runtime objects
        inst.name_add_sym(inst.g_st_dict, "Bigendian", inst.o_false)
        
        # initialize interpreter
        inst.g_interp = Interp(inst)
        inst.g_interp.reset()
        if debug:
            inst.g_interp.set_debug(inst.debug_hook_pre, inst.debug_hook_post)
        
        # initialize primitive ops
        inst.build_primitives()
        
        # compile the Kernel modules
        inst.g_compile = Compile(inst)
        for mod in init.Init_Kernel_Mod:
            inst.g_compile.parse_file(os.path.join("Kernel", mod))
        
        print("ST Dictionary:")
        inst.dict_print(inst.g_st_dict, True)
            
        #for klassInfo in init.Init_Class:
        #    cacheName = klassInfo[2]
        #    klassObj = getattr(inst, "k_" + cacheName)
        #    print("%s %s %s %s %s" % ( \
        #                         klassObj.name,
        #                         klassObj.instanceVariables, 
        #                         klassObj.subClasses,
        #                         klassObj.superClass,
        #                         klassObj.classVariables))
        
        x = inst.g_interp.send_message_extern(inst.g_sym_table, 
                                              "size", 
                                              ())
        print(x)
        
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
        CTrue._Cover = self.k_true
                
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
            klassObj.environment = self.g_st_dict
            klassObj.instanceVariables = self.create_inst_vars(superObj, instVars)
            klassObj.classVariables = self.create_class_vars(klassObj, classVars)
            klassObj.sharedPools = self.create_shared_pools(poolNames)
            klassObj.methodDictionary = self.o_nil
            klassObj.comment = self.o_nil
            klassObj.category = self.o_nil
            klassObj.pragmaHandlers = self.o_nil
            klassObj.name = self.name_add_sym(self.g_st_dict, klassName, klassObj)
    
    def build_disassembly(self):
        """
        Create info needed for disassembly
        """
        disTbl = self.g_dis
        disTbl[B_PUSH_SELF] = ("PUSH_SELF", 0)
        disTbl[B_RETURN_METHOD_STACK_TOP] = ("RETURN_METHOD", 0)
        disTbl[B_PUSH_LIT_VARIABLE] = ("PUSH_LIT_VARIABLE", 1)
        disTbl[B_PUSH_LIT_CONSTANT] = ("PUSH_LIT_CONSTANT", 1)
        disTbl[B_SEND] = ("SEND", 1)
        disTbl[B_POP_STACK_TOP] = ("POP_STACK_TOP", 0)
        disTbl[B_PUSH_TEMPORARY_VARIABLE] = ("PUSH_TEMP_VARIABLE", 1)
        disTbl[B_STORE_LIT_VARIABLE] = ("STORE_LIT_VARIABLE", 1)
        disTbl[B_STORE_TEMPORARY_VARIABLE] = ("STORE_TEMP_VARIABLE", 1)
    
    def build_primitives(self):
        """
        Create the primitives dictionary and register ops with
        interpreter.
        """
        primDict = BindingDictionary.new_n(512)
        primDict.environment = self.g_st_dict
        self.name_add_sym(self.g_st_dict, "VMPrimitives", primDict)
        for primId,primName in enumerate(init.Init_Primitive):
            primId += 1     # 0 is reserved
            if not self.g_interp.add_primitive(primName):
                self.fatal_err("cannot find primitive handler", primName)
            symObj = self.symbol_add("VMpr_" + primName)
            self.dict_add(primDict, symObj, primId)
        print("VM Primitives:")
        self.dict_print(primDict)
        print()
    
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
        symbol table, nil otherwise.
        """
        symTable = self.g_sym_table 
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
        symTable = self.g_sym_table
        idx = hsh_seq(map(ord, symName)) & (symTable.size - 1)
        link = symTable[idx]
        while not link.is_nil():
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
        assoc = self.dict_find(self.g_st_dict, symObj)
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
        dictObj[self.dict_index(dictObj, keyObj)] = Association(keyObj, itemObj)
        dictObj.tally = tly + 1
        
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
        idx = keyObj.hsh() 
        while arrSize > 0:
            idx &= mask
            assoc = dictObj[idx + numInst]
            if assoc.is_nil() or (keyObj.is_same(assoc.key)):
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
        print("Tally %d (%d)" % (dictObj.tally, dictObj.size - numInst))
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
        dictObj[idx - 1] = keyObj
        dictObj[idx] = itemObj
        dictObj.tally = tly + 1
        
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
        idx = (keyObj.hsh() << 1) & Int_Max
        mask = arrSize - 1
        arrSize >>= 1
        while arrSize > 0:
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
        for n,b in enumerate(byteCode[::2]):
            info = self.g_dis[b]
            if info is None:
                prList = ["????"]
            else:
                prList = ["[%d]" % (n * 2), info[0]]
                if info[1] == 1:
                    prList.append(byteCode[(n * 2) + 1])
            print(*prList)
            
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
        
    def debug_user_input(self):
        """
        Get user input and process debugger command
        """
        while True:
            line = input(">>")
            if len(line) < 1:
                print()
                continue
            c = line[0]
            if c == 's':
                break
            elif c == 'c':
                self.g_interp.set_debug(None, None)
                break
            elif c == 'd':
                self.context_print_byte()
                print()
                continue
            elif c == '0':
                self.context_print_state(self.g_interp.i_context)
                print()
                continue
            elif c == '1':
                parent = self.g_interp.i_context.parent
                if not parent.is_nil():
                    self.context_print_state(parent)
                else:
                    print("NO CONTEXT")
            elif c == 'h':
                print("s = step")
                print("c = continue")
                print("d = disassemble current bytecode")
                print("h = help")
                print("q = quit immediately")
                print()
                continue
            elif c == 'q':
                sys.exit(0)
            else:
                print("???\n")
                continue
                
    def context_print_byte(self):
        """
        Display the next bytecode to be executed in the current
        context.
        """
        ctx = self.g_interp.i_context
        ip = ctx.ip
        code = ctx.method.get_code()
        selName = ctx.method.descriptor.selector
        klassName = ctx.method.descriptor.klass
        print("<%s> %s[%d]:" % (klassName, selName, ip), 
              self.dis_byte(code[ip]), 
              code[ip + 1])
    
    @staticmethod
    def context_print_state(ctx):
        """
        Display the state of the context
        """
        meth = ctx.method
        if meth.is_nil():
            methName = meth
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
        print()
        
    def fatal_err(self, *s):
        """
        Print a message and exit.  None of the
        system state will be saved.
        """
        print(*s)
        sys.exit(-1)
            
        
Smalltalk._SmalltalkInstance = Smalltalk()

            