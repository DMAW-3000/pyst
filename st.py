"""
Common definitions of Smalltalk fundamental types
"""

import sys

from obj import Obj_Table


# globals
_Obj_Nil = None
Int_Max = sys.maxsize


def is_int(x):
    """
    Returns True if x is a SmallInteger,
    False otherwise.
    """
    return isinstance(x, int)
    
def is_obj(x):
    """
    Returns True if x is an object reference,
    False otherwise.
    """
    return not isinstance(x, int)

def set_obj_nil(x):
    """
    Set the global Smalltalk Nil instance.
    """
    global _Obj_Nil
    _Obj_Nil = x
    
def hsh_seq(x):
    """
    Create a hash key from a sequence of values
    """
    global Int_Max
    h = 1497032417
    m = Int_Max
    for c in x:
        h = (h + c) & m
        h = (h + ((h << 10) & m)) & m
        h ^= (h >> 6)
    return h
    
def hsh_scram(x):
    """
    Generate a hash key from a single value
    """
    global Int_Max
    m = Int_Max
    x ^= (((x << 33) & m) | (x >> 31))
    x ^= (((x << 10) & m) | (x >> 22))
    x ^= (((x <<  6) & m) | (x >> 26))
    x ^= (((x << 16) & m) | (x >> 16))
    return x


class Object(object):
    """
    Smalltalk base Object definition.
    """
    
    # this will point to the Smalltalk class representing
    # this python class after init is complete.
    # each Object subclass will have its own _Cover
    _Cover = None
    
    @classmethod
    def set_cover(klass, x):
        """
        Link the python class to its Smalltalk counterpart
        """
        klass._Cover = x
    
    def __init__(self, sz):
        """
        Create a blank object
        """
        global Obj_Table
        self._py_cache = None
        self._obj_id = Obj_Table.new_obj()
        self._klass = self._Cover
        self._flags = 0
        self.resize(sz)
        
    @property
    def size(self):
        """
        The number of attributes contained in the object
        """
        return len(self._refs)
        
    def resize(self, sz):
        """
        Resize the reference storage arrary for this Object.
        This will not preserve the old references.
        """
        global _Obj_Nil
        self._refs = [_Obj_Nil] * sz
        
    def get_class(self):
        """
        Return the Smalltalk class to which Object belongs
        """
        return self._klass
        
    def get_id(self):
        """
        Return the Object's unique id (integer)
        """
        return self._obj_id
        
    def hsh(self):
        """
        Return a hash key for the object.
        """
        return hsh_scram(self._obj_id)
        
    def is_same(self, other):
        """
        Returns True if other Object is identical to this one,
        False otherwise.
        """
        return self._obj_id == other._obj_id
        
    def is_nil(self):
        """
        Returns True if Object is nil, False otherwise.
        """
        return self._obj_id == 0
        
    def __getitem__(self, idx):
        """
        Get one of the Object's child references
        """
        return self._refs[idx]
        
    def __setitem__(self, idx, x):
        """
        Set one of the Object's child references
        """
        self._refs[idx] = x
        
    def __len__(self):
        """
        Return the number of child references in the Object
        """
        return self.size
        
    def __del__(self):
        """
        Notify when the object is out of scope
        """
        global Obj_Table
        #print("DEL", self._obj_id, self)
        Obj_Table.free_obj(self._obj_id)
        

class UndefinedObject(Object):
    """
    Smalltalk UndefinedObject internal representation
    """
    
    _Cover = None
    
    def __init__(self):
        """
        Create an UndefinedObject innstance.  This should only
        be called once.  The new object has special ID '0'.
        """
        self._obj_id = 0
        self._klass = self._Cover
        self._flags = 0
        self.resize(1)
        
    def __str__(self):
        return "NIL"
    
    
class CFalse(Object):
    """
    Internal representation of Smalltalk False
    """
    
    _Cover = None
    
    def __init__(self):
        """
        Create a False object innstance.  This should only
        be called once.  The new object has special ID '1'.
        """
        self._obj_id = 1
        self._klass = self._Cover
        self._flags = 0
        self.resize(1)
        
    @property
    def truthValue(self):
        return self[0]
        
    @truthValue.setter
    def truthValue(self, x):
        self[0] = x
        
    def __str__(self):
        return "FALSE"
    

class CTrue(Object):
    """
    Internal representation of Smalltalk True
    """
    
    _Cover = None
    
    def __init__(self):
        """
        Create a True object innstance.  This should only
        be called once.  The new object has special ID '2'.
        """
        self._obj_id = 2
        self._klass = self._Cover
        self._flags = 0
        self.resize(1)
        
    @property
    def truthValue(self):
        return self[0]
        
    @truthValue.setter
    def truthValue(self, x):
        self[0] = x
    
    def __str__(self):
        return "TRUE"
        

class Array(Object):
    """
    Internal representation of Smalltalk Array
    """
    
    _Cover = None
    
    @classmethod
    def from_seq(klass, x):
        """
        Create an Array from a Python sequence
        """
        arr = klass(len(x))
        for n,r in enumerate(x):
            arr[n] = r
        return arr
        
    def __str__(self):
        return "ARRAY(%d)" % self.size
    
    
class String(Array):
    """
    Internal representation of Smalltalk String
    """
    
    _Cover = None
        
    @classmethod
    def from_str(klass, s):
        """
        Create Smalltalk String from Python str
        """
        strObj = klass(len(s))
        for n,c in enumerate(s):
            strObj[n] = ord(c)
        return strObj
        
    def to_str(self):
        """
        Return the String contents as a Python str
        """
        s = ""
        for n in range(self.size):
            s += chr(self[n])
        return s
        
    def __str__(self):
        return "\'" + self.to_str() + "\'"
        
        
class Symbol(String):
    """
    Internal representation of a Smalltalk Symbol
    """
    
    _Cover = None
        
    @classmethod
    def from_str(klass, s):
        """
        Create a Smalltalk Symbol from a Python str
        """
        symObj = super().from_str(s)
        symObj._py_cache = s
        return symObj
        
    def resize(self, sz):
        """
        Resize the Symbol storage. For efficiency, a python 
        bytearray is used instead of the usual python list.  The old 
        values stored in the object are not preserved.
        """
        self._refs = bytearray(sz)
            
    def to_str(self):
        """
        Return Symbol contents as a Python str
        """
        if self._py_cache is not None:
            return self._py_cache
        return super().to_str()
            
    def __str__(self):
        return "#\'" + self.to_str() + '\''
        
        
class SymLink(Object):
    """
    Internal representation of SymLink object
    """
    
    _Cover = None
    
    def __init__(self, symObj, linkObj):
        """
        Create an new SymLink
        """
        super().__init__(2)
        self.nextLink = linkObj
        self.symbol = symObj
        
    @property
    def nextLink(self):
        return self[0]
        
    @nextLink.setter
    def nextLink(self, x):
        self[0] = x
        
    @property
    def symbol(self):
        return self[1]
        
    @symbol.setter
    def symbol(self, x):
        self[1] = x
        

class Association(Object):
    """
    Internal representation of a Smalltalk Association
    """
    
    _Cover = None
    
    def __init__(self, keyObj, valueObj):
        """
        Create an Association
        """
        super().__init__(2)
        self.key = keyObj
        self.value = valueObj
        
    @property
    def key(self):
        return self[0]
        
    @key.setter
    def key(self, x):
        self[0] = x
        
    @property
    def value(self):
        return self[1]
        
    @value.setter
    def value(self, x):
        self[1] = x
        
        
class VariableBinding(Object):
    """
    Internal representation of a Smalltalk VariableBinding
    """
    
    _Cover = None
    
    def __init__(self, keyObj, valueObj, envObj):
        """
        Create an Association
        """
        super().__init__(3)
        self.key = keyObj
        self.value = valueObj
        self.environment = envObj
        
    @property
    def key(self):
        return self[0]
        
    @key.setter
    def key(self, x):
        self[0] = x
        
    @property
    def value(self):
        return self[1]
        
    @value.setter
    def value(self, x):
        self[1] = x
        
    @property
    def environment(self):
        return self[2]
        
    @environment.setter
    def environment(self, x):
        self[2] = x
        
        
class _Dict(Object):
    """
    Not a real Smalltalk class but hold functionality
    common to dictionary objects.
    """
    
    @classmethod
    def new_n(klass, n):
        """
        Create a dictionary with the number of initial
        slots.  This should be a power of 2.
        """
        return klass(klass.size_n(n))
        
    @staticmethod
    def size_n(n):
        raise NotImplementedError("_Dict subclass responsibility")
        
        
class Dictionary(_Dict):
    """
    Internal representation of a Smalltalk Dictionary
    """
    
    _Cover = None
    
    @staticmethod
    def size_n(n):
        """
        Return the size needed for the number of slots.
        This should be a power of 2.
        """
        return n + 1
    
    def __init__(self, sz):
        """
        Create a Dictionary object.
        """
        super().__init__(sz)
        self.tally = 0
        
    @property
    def tally(self):
        return self[0]
        
    @tally.setter
    def tally(self, x):
        self[0] = x
        
    def __str__(self):
        return "DICT(%d)" % self.tally
        
        
class BindingDictionary(_Dict):
    """
    Internal representation of a Smalltalk BindingDictionary
    """
    
    _Cover = None
    
    @staticmethod
    def size_n(n):
        """
        Return the size needed for the number of slots.
        This should be a power of 2.
        """
        return n + 2
    
    def __init__(self, sz):
        """
        Create a BindingDictionary object.
        """
        super().__init__(sz)
        self.tally = 0
        
    @property
    def tally(self):
        return self[0]
        
    @tally.setter
    def tally(self, x):
        self[0] = x
        
    @property
    def environment(self):
        return self[1]
        
    @environment.setter
    def environment(self, x):
        self[1] = x
        
    def __str__(self):
        return "BINDDICT(%d)" % self.tally
        
     
class MethodDictionary(_Dict):
    """
    Internal representation of a Smalltalk IdentityDictionary
    """
    
    _Cover = None
    
    @staticmethod
    def size_n(n):
        """
        Return the size needed for the number of slots.
        This should be a power of 2.
        """
        return (n << 1) + 2
    
    def __init__(self, sz):
        """
        Create a MethodDictionary object.
        """
        super().__init__(sz)
        self.tally = 0
        
    @property
    def tally(self):
        return self[0]
        
    @tally.setter
    def tally(self, x):
        self[0] = x
        
    @property
    def mutex(self):
        return self[1]
        
    @mutex.setter
    def mutex(self, x):
        self[1] = x
        
    def __str__(self):
        return "METHDICT(%d)" % self.tally
    
        
class Namespace(_Dict):
    """
    Internal representation of a Smalltalk Namespace
    """
    
    _Cover = None
    
    @staticmethod
    def size_n(n):
        """
        Return the size needed for the number of slots.
        This should be a power of 2.
        """
        return n + 5
    
    def __init__(self, sz):
        """
        Create a Namespace object.  Size is the number
        of initial storage slots and should be a power of 2.
        """
        super().__init__(sz)
        self.tally = 0
        
    @property
    def tally(self):
        return self[0]
        
    @tally.setter
    def tally(self, x):
        self[0] = x
        
    @property
    def environment(self):
        return self[1]
        
    @environment.setter
    def environment(self, x):
        self[1] = x
        
    @property
    def name(self):
        return self[2]
        
    @name.setter
    def name(self, x):
        self[2] = x
        
    @property
    def subspaces(self):
        return self[3]
        
    @subspaces.setter
    def subspaces(self, x):
        self[3] = x
        
    @property
    def sharedPools(self):
        return self[4]
        
    @sharedPools.setter
    def sharedPools(self, x):
        self[4] = x
        
    def __str__(self):
        return "NAMESPACE(%d)" % self.tally
        
        
class Class(Object):
    """
    Internal representation of a Smalltalk Class
    """
    
    _Cover = None
    
    def __init__(self, superKlass, numInstVars, isFixed):
        """
        Create a Class object
        """
        super().__init__(12)
        self.superClass = superKlass
        self.instanceSpec = numInstVars << 12
        if isFixed:
            self.instanceSpec |= 0x10
        
    def get_num_inst(self):
        return self.instanceSpec >> 12
        
    def is_fixed(self):
        return (self.instanceSpec & 0x10) != 0
        
    @property
    def superClass(self):
        return self[0]
        
    @superClass.setter
    def superClass(self, x):
        self[0] = x
        
    @property
    def methodDictionary(self):
        return self[1]
        
    @methodDictionary.setter
    def methodDictionary(self, x):
        self[1] = x
        
    @property
    def instanceSpec(self):
        return self[2]
        
    @instanceSpec.setter
    def instanceSpec(self, x):
        self[2] = x
        
    @property
    def subClasses(self):
        return self[3]
        
    @subClasses.setter
    def subClasses(self, x):
        self[3] = x
        
    @property
    def instanceVariables(self):
        return self[4]
        
    @instanceVariables.setter
    def instanceVariables(self, x):
        self[4] = x
        
    @property
    def name(self):
        return self[5]
        
    @name.setter
    def name(self, x):
        self[5] = x
        
    @property
    def comment(self):
        return self[6]
        
    @comment.setter
    def comment(self, x):
        self[6] = x
        
    @property
    def category(self):
        return self[7]
        
    @category.setter
    def category(self, x):
        self[7] = x
        
    @property
    def environment(self):
        return self[8]
        
    @environment.setter
    def environment(self, x):
        self[8] = x
        
    @property
    def classVariables(self):
        return self[9]
        
    @classVariables.setter
    def classVariables(self, x):
        self[9] = x
        
    @property
    def sharedPools(self):
        return self[10]
        
    @sharedPools.setter
    def sharedPools(self, x):
        self[10] = x
        
    @property
    def pragmaHandlers(self):
        return self[11]
        
    @pragmaHandlers.setter
    def pragmaHandlers(self, x):
        self[11] = x
        
    def __str__(self):
        if not self.name.is_nil():
            s = str(self.name)
        else:
            s = '????'
        return "CLASS(" + s + ")"
        

class Metaclass(Object):
    """
    The internal representation of Smalltalk Metaclass
    """
    
    _Cover = None
    
    def __init__(self, instKlass):
        super().__init__(6)
        self.instanceSpec = (12 << 13) | 0x20
        self.instanceClass = instKlass
            
    @property
    def superClass(self):
        return self[0]
        
    @superClass.setter
    def superClass(self, x):
        self[0] = x
        
    @property
    def methodDictionary(self):
        return self[1]
        
    @methodDictionary.setter
    def methodDictionary(self, x):
        self[1] = x
        
    @property
    def instanceSpec(self):
        return self[2]
        
    @instanceSpec.setter
    def instanceSpec(self, x):
        self[2] = x
        
    @property
    def subClasses(self):
        return self[3]
        
    @subClasses.setter
    def subClasses(self, x):
        self[3] = x
        
    @property
    def instanceVariables(self):
        return self[4]
        
    @instanceVariables.setter
    def instanceVariables(self, x):
        self[4] = x
        
    @property
    def instanceClass(self):
        return self[5]
        
    @instanceClass.setter
    def instanceClass(self, x):
        self[5] = x
        

class _Context(Object):
    """
    Not a real Smalltalk class, but encapsulates
    common behavior of context objects.
    """
    
    def __init__(self):
        """
        Create a new context
        """
        super().__init__(7)
        self.ip = 0
        self.sp = 6
        
    def push(self, x):
        """
        Push a new item onto the context stack
        """
        self._refs.append(x)
        self.sp += 1
        
    def pop(self):
        """
        Pop an item from the context stack
        """
        if self.size == 7:
            raise IndexError("stack underflow")
        x = self._refs.pop()
        self.sp -= 1
        return x
        
    def expand(self, n):
        """
        Increase the context stack space a number
        of slots.
        """
        global _Obj_Nil
        self._refs.extend([_Obj_Nil] * n)
        self.sp += n
        

class BlockContext(_Context):
    """
    Internal representation of Smalltalk BlockContext
    """
    
    _Cover = None
        
    @property
    def parent(self):
        return self[0]
        
    @parent.setter
    def parent(self, x):
        self[0] = x
  
    @property
    def native_ip(self):
        return self[1]
        
    @native_ip.setter
    def native_ip(self, x):
        self[1] = x
        
    @property
    def ip(self):
        return self[2]
        
    @ip.setter
    def ip(self, x):
        self[2] = x
  
    @property
    def sp(self):
        return self[3]
        
    @sp.setter
    def sp(self, x):
        self[3] = x
        
    @property
    def receiver(self):
        return self[4]
        
    @receiver.setter
    def receiver(self, x):
        self[4] = x
        
    @property
    def method(self):
        return self[5]
        
    @method.setter
    def method(self, x):
        self[5] = x
        
    @property
    def outerContext(self):
        return self[6]
        
    @outerContext.setter
    def outerContext(self, x):
        self[6] = x
        
        
class MethodContext(_Context):
    """
    Internal representation of Smalltalk MethodContext
    """
    
    _Cover = None
    
    def __init__(self):
        """
        Create a new context
        """
        super().__init__()
        self.flags = 0
        
    @property
    def parent(self):
        return self[0]
        
    @parent.setter
    def parent(self, x):
        self[0] = x
  
    @property
    def native_ip(self):
        return self[1]
        
    @native_ip.setter
    def native_ip(self, x):
        self[1] = x
        
    @property
    def ip(self):
        return self[2]
        
    @ip.setter
    def ip(self, x):
        self[2] = x
  
    @property
    def sp(self):
        return self[3]
        
    @sp.setter
    def sp(self, x):
        self[3] = x
        
    @property
    def receiver(self):
        return self[4]
        
    @receiver.setter
    def receiver(self, x):
        self[4] = x
        
    @property
    def method(self):
        return self[5]
        
    @method.setter
    def method(self, x):
        self[5] = x
        
    @property
    def flags(self):
        return self[6]
        
    @flags.setter
    def flags(self, x):
        self[6] = x
        
        
class _Code(Object):
    """
    Not a real Smalltalk class, but encapsulates
    behavior common to method and block compiled
    objects.
    """
    
    def __init__(self):
        """
        Create a new code object.  Extend the usual
        reference list by an bytearray to hold the objects
        bytecodes.
        """
        super().__init__(3)
        self._bc_arr = bytearray(1)
        
    def get_code(self):
        """
        Get the bytecode array
        """
        return self._bc_arr
        
    def set_code(self, x):
        """
        Set the bytecode array
        """
        self._bc_arr = x
        
    @property
    def size(self):
        return len(self._refs) + len(self._bc_arr)
        
    def __getitem__(self, idx):
        """
        Get one of the Object's child references
        """
        refSize = len(self._refs)
        if idx >= refSize:
            return self._bc_arr[idx - refSize]
        return self._refs[idx]
        
    def __setitem__(self, idx, x):
        """
        Set one of the Object's child references
        """
        refSize = len(self._refs)
        if idx >= refSize:
            self._bc_arr[idx - refSize] = x
        else:
            self._refs[idx] = x
     
        
class CompiledMethod(_Code):
    """
    Internal representation of Smalltalk CompiledMethod
    """
    
    _Cover = None
        
    def set_hdr(self, numArg, numTemp, depth, primId):
        """
        Set the method header info
        """
        self.header = (numArg & 0x1f) | \
                      ((depth & 0x3f) << 5) | \
                      ((numTemp & 0x3f) << 11) | \
                      ((primId & 0x1ff) << 17)
                      
    def get_hdr(self):
        """
        Return the method header info as a tuple:
        (num_arg, num_temp, depth, prim_id)
        """
        hdr = self.header
        return (hdr & 0x1f, 
               (hdr >> 11) & 0x3f, 
               (hdr >> 5) & 0x3f, 
               (hdr >> 17) & 0x1ff)
        
    def get_num_arg(self):
        """
        Get number of method arguments
        """
        return self.header & 0x1f
        
    def get_num_temp(self):
        """
        Get number of method temporary variables
        """
        return (self.header >> 11) & 0x3f
        
    def get_depth(self):
        """
        Get stack depth required for method
        """
        return (self.header >> 5) & 0x3f
        
    def get_prim_id(self):
        """
        Get method primitive ID, 0 if none.
        """
        return (self.header >> 17) & 0x1ff
        
    @property
    def literals(self):
        return self[0]
        
    @literals.setter
    def literals(self, x):
        self[0] = x
    
    @property
    def header(self):
        return self[1]
        
    @header.setter
    def header(self, x):
        self[1] = x
        
    @property    
    def descriptor(self):
        return self[2]
        
    @descriptor.setter
    def descriptor(self, x):
        self[2] = x
        
    def __str__(self):
        if (not self.descriptor.is_nil()) and \
           (not self.descriptor.selector.is_nil()):
            s = str(self.descriptor.selector)
        else:
            s = '????'
        return "METHOD(" + s + ")"
        

class CompiledBlock(_Code):
    """
    Internal representation of Smalltalk CompiledBlock
    """
    
    _Cover = None
    
    @property
    def literals(self):
        return self[0]
        
    @property
    def literals(self):
        return self[0]
        
    @literals.setter
    def literals(self, x):
        self[0] = x
    
    @property
    def header(self):
        return self[1]
        
    @header.setter
    def header(self, x):
        self[1] = x
        
    @property
    def method(self):
        return self[2]
        
    @method.setter
    def method(self, x):
        self[2] = x
        
        
        
class MethodInfo(Object):
    """
    Internal representation of Smalltalk MethodInfo
    """
    
    _Cover = None
    
    def __init__(self, linkKlass):
        super().__init__(5)
        self.klass = linkKlass
        
    @property
    def sourceCode(self):
        return self[0]
        
    @sourceCode.setter
    def sourceCode(self, x):
        self[0] = x

    @property
    def category(self):
        return self[1]
        
    @category.setter
    def category(self, x):
        self[1] = x
        
    @property
    def klass(self):
        return self[2]
        
    @klass.setter
    def klass(self, x):
        self[2] = x
  
    @property
    def selector(self):
        return self[3]
        
    @selector.setter
    def selector(self, x):
        self[3] = x
    
    @property
    def debugInfo(self):
        return self[4]
        
    @debugInfo.setter
    def debugInfo(self, x):
        self[4] = x
        
        
class BlockClosure(Object):
    """
    Internal representation of Smalltalk BlockClosure
    """
    
    _Cover = None
    
    def __init__(self, blk):
        """
        Create a new BlockClosure
        """
        super().__init__(3)
        self.block = blk
        
    @property
    def outerContext(self):
        return self[0]
        
    @outerContext.setter
    def outerContext(self, x):
        self[0] = x
        
    @property
    def block(self):
        return self[1]
        
    @block.setter
    def block(self, x):
        self[1] = x
        
    @property
    def receiver(self):
        return self[2]
        
    @receiver.setter
    def receiver(self, x):
        self[2] = x


# the global bytecode values
B_PLUS_SPECIAL              = 0
B_MINUS_SPECIAL             = 1
B_LESS_THAN_SPECIAL         = 2
B_GREATER_THAN_SPECIAL      = 3
B_LESS_EQUAL_SPECIAL        = 4
B_GREATER_EQUAL_SPECIAL     = 5
B_EQUAL_SPECIAL             = 6
B_NOT_EQUAL_SPECIAL         = 7
B_TIMES_SPECIAL             = 8
B_DIVIDE_SPECIAL            = 9
B_REMAINDER_SPECIAL         = 10
B_BIT_XOR_SPECIAL           = 11
B_BIT_SHIFT_SPECIAL         = 12
B_INTEGER_DIVIDE_SPECIAL    = 13
B_BIT_AND_SPECIAL           = 14
B_BIT_OR_SPECIAL            = 15

B_AT_SPECIAL                = 16
B_AT_PUT_SPECIAL            = 17
B_SIZE_SPECIAL              = 18
B_CLASS_SPECIAL             = 19
B_IS_NIL_SPECIAL            = 20
B_NOT_NIL_SPECIAL           = 21
B_VALUE_SPECIAL             = 22
B_VALUE_COLON_SPECIAL       = 23
B_SAME_OBJECT_SPECIAL       = 24
B_JAVA_AS_INT_SPECIAL       = 25
B_JAVA_AS_LONG_SPECIAL      = 26

B_SEND                      = 28
B_SEND_SUPER                = 29
B_SEND_IMMEDIATE            = 30
B_SEND_SUPER_IMMEDIATE      = 31

B_PUSH_TEMPORARY_VARIABLE   = 32
B_PUSH_OUTER_TEMP           = 33
B_PUSH_LIT_VARIABLE         = 34
B_PUSH_RECEIVER_VARIABLE    = 35
B_STORE_TEMPORARY_VARIABLE  = 36
B_STORE_OUTER_TEMP          = 37
B_STORE_LIT_VARIABLE        = 38
B_STORE_RECEIVER_VARIABLE   = 39
B_JUMP_BACK                 = 40
B_JUMP                      = 41
B_POP_JUMP_TRUE             = 42
B_POP_JUMP_FALSE            = 43
B_PUSH_INTEGER              = 44
B_PUSH_SPECIAL              = 45
B_PUSH_LIT_CONSTANT         = 46
B_POP_INTO_NEW_STACKTOP     = 47
B_POP_STACK_TOP             = 48
B_MAKE_DIRTY_BLOCK          = 49
B_RETURN_METHOD_STACK_TOP   = 50
B_RETURN_CONTEXT_STACK_TOP  = 51
B_DUP_STACK_TOP             = 52
B_EXIT_INTERPRETER          = 53
B_LINE_NUMBER_BYTECODE      = 54
B_EXT_BYTE                  = 55 
B_PUSH_SELF                 = 56
