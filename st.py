"""
Common definitions of Smalltalk fundamental types
"""


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
    
    
_Obj_Nil = None

def set_obj_nil(x):
    """
    Set the global Smalltalk Nil instance.
    """
    global _Obj_Nil
    _Obj_Nil = x
    
    
def is_nil(x):
    """
    Returns True if x is Nil,
    False otherwise.
    """
    global _Obj_Nil
    return x is _Obj_Nil
    
    
def hsh_seq(x):
    """
    Create a hash key from a sequence of values
    """
    h = 1497032417
    m = 0xffffffff
    for c in x:
        h = (h + c) & m
        h = (h + (h << 10)) & m
        h = (h ^ (h >> 6)) & m
    return h
    

class Object(object):
    """
    Smalltalk base Object definition.
    """
    
    _Cover = None
    
    @classmethod
    def set_cover(klass, x):
        """
        Link the python class to its Smalltalk counterpart
        """
        klass._Cover = x
    
    def __init__(self, sz = 0):
        """
        Create a blank object
        """
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
        

class UndefinedObject(Object):
    """
    Smalltalk UndefinedObject internal representation
    """
    pass
    
    
class CFalse(Object):
    """
    Internal representation of Smalltalk False
    """
    
    def __init__(self):
        super().__init__(1)
        
    @property
    def truthValue(self):
        return self[0]
        
    @truthValue.setter
    def truthValue(self, x):
        self[0] = x
    

class CTrue(Object):
    """
    Internal representation of Smalltalk True
    """
    
    def __init__(self):
        super().__init__(1)
        
    @property
    def truthValue(self):
        return self[0]
        
    @truthValue.setter
    def truthValue(self, x):
        self[0] = x
        

class Array(Object):
    """
    Internal representation of Smalltalk Array
    """
    pass
        
        
class Symbol(Object):
    """
    Internal representation of a Smalltalk Symbol
    """
    
    def __init__(self, sz):
        """
        Create a blank Symbol
        """
        super().__init__(sz)
    
    @classmethod
    def from_str(klass, s):
        """
        Create Smalltalk Symbol from Python str
        """
        sym = klass(len(s))
        for n,c in enumerate(s):
            sym[n] = ord(c)
        return sym
            
    def to_str(self):
        """
        Return Symbol contents as a Python str
        """
        s = ""
        for n in range(self.size):
            s += chr(self[n])
        return s
        
    def hsh(self):
        """
        Return a hash value for the Symbol
        """
        return hsh_seq(self._refs)
            
    def __str__(self):
        return self.to_str()
        
        
class SymLink(Object):
    """
    Internal representation of SymLink object
    """
    
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
        
        
class Namespace(Object):
    """
    Internal representation of a Smalltalk Namespace
    """
    
    def __init__(self, sz):
        """
        Create a Namespaece object
        """
        super().__init__(sz + 5)
        self.tally = 0
        
    @property
    def tally(self):
        return self[0]
        
    @tally.setter
    def tally(self, x):
        self[0] = x
        
    @property
    def superspace(self):
        return self[1]
        
    @superspace.setter
    def superspace(self, x):
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
        
        
class Class(Object):
    """
    Internal representation of a Smalltalk Class
    """
    
    def __init__(self, superKlass, numInstVars, isFixed):
        """
        Create a Class object
        """
        super().__init__(11)
        self.superClass = superKlass
        self.instanceSpec = numInstVars << 13
        if isFixed:
            self.instanceSpec |= 0x20
        
    def get_num_inst(self):
        return self.instanceSpec >> 13
        
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
        

class Metaclass(Object):
    """
    The internal representation of Smalltalk Metaclass
    """
    
    def __init__(self, instKlass):
        super().__init__(6)
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