"""
Configuration for creating a new environment
"""

# Data for building initial class definitions
# 0 = class name
# 1 = True if class has Python class of same name
# 2 = cache variable name
# 3 = superclass cache variable name
# 4 = True if object is fixed size
# 5 = tuple of instance variable names
# 6 = tuple of class variable names
# 7 = tuple of shared pool names

Init_Class = (
    ("Object", True, "object", None, False, (), ("Dependencies", "FinalizableObjects"), ("VMPrimitives",)),
    ("UndefinedObject", True, "undef_obj", "object", True, (), (), ()),
    ("Boolean", False, "boolean", "object", True, (), (), ()),
    ("False", False, "false", "boolean", True, ("truthValue",), (), ()),
    ("True", False, "true", "boolean", True, ("truthValue",), (), ()),
    ("Exception", False, "exception", "object", True, ("creator", "tag", "messageText", "resumeBlock", "onDoBlock", "handlerBlock", "context", "isNested", "previousState"), ("NoTag",), ()),
    ("Behavior", False, "behavior", "object", True, ("superClass", "methodDictionary", "instanceSpec", "subClasses", "instanceVariables"), (), ()), 
    ("ClassDescription", False, "class_desc", "behavior", True, (), (), ()),
    ("Class", True, "class", "class_desc", True, ("name", "comment", "category", "environment", "classVariables", "sharedPools", "pragmaHandlers"), (), ()),
    ("Metaclass", True, "metaclass", "class_desc", True, ("instanceClass",), (), ()),
    ("Iterable", False, "iterable", "object", True, (), (), ()),
    ("Collection", False, "collection", "iterable", True, (), (), ()),
    ("SequenceableCollection", False, "seq_collection", "collection", True, (), (), ()),
    ("ArrayedCollection", False, "arr_collection", "seq_collection", False, (), (), ()),
    ("Array", True, "array", "arr_collection", False, (), (), ()),
    ("ByteArray", True, "bytearray", "arr_collection", False, (), (), ()),
    ("Link", False, "link", "object", True, ("nextLink",), (), ()),
    ("SymLink", True, "sym_link", "link", True, ("symbol",), (), ()),
    ("HashedCollection", False, "hash_collection", "collection", False, ("tally",), (), ()),
    ("Dictionary", True, "dictionary", "hash_collection", False, (), (), ()),
    ("BindingDictionary", True, "bind_dictionary", "dictionary", False, ("environment",), (), ()),
    ("AbstractNamespace", False, "abs_namespace", "bind_dictionary", False, ("name", "subspaces", "sharedPools"), (), ()),
    ("Namespace", True, "namespace", "abs_namespace", False, (), (), ()),
    ("RootNamespace", False, "root_namespace", "abs_namespace", False, (), (), ()),
    ("SystemDictionary", False, "sys_dictionary", "root_namespace", False, (), (), ()),
    ("Magnitude", False, "magnitude", "object", True, (), (), ()),
    ("LookupKey", False, "lookup_key", "magnitude", True, ("key",), (), ()),
    ("Association", True, "assoc", "lookup_key", True, ("value",), (), ()),
    ("HomedAssociation", False, "homed_assoc", "assoc", True, ("environment",), (), ()),
    ("VariableBinding", True, "variable_bind", "homed_assoc", True, (), (), ()),
    ("CharacterArray", False, "char_array", "arr_collection", False, (), (), ()),
    ("String", True, "string", "char_array", False, (), (), ()),
    ("Symbol", True, "symbol", "string", False, (), (), ()),
    ("Stream", False, "stream", "iterable", True, (), (), ()),
    ("PositionableStream", False, "pos_stream", "stream", True, ("collection", "ptr", "endPtr", "access"), (), ()),
    ("ReadStream", False, "read_stream", "pos_stream", True, (), (), ()),
    ("WriteStream", False, "write_stream", "pos_stream", True, (), (), ()),
    ("Number", False, "number", "magnitude", True, (), (), ()),
    ("Integer", False, "integer", "number", True, (), (), ("PySymbols",)),
    ("SmallInteger", False, "small_int", "integer", True, (), (), ()),
    ("Float", False, "float", "number", True, (), (), ()),
    ("FloatD", False, "float_d", "float", True, (), (), ()),
    ("Character", True, "character", "magnitude", True, ("codePoint",), ("Table", "UpperTable", "LowerTable"), ()),
    ("ContextPart", False, "context_part", "object", False, ("parent", "nativeIP", "ip", "sp", "receiver", "method"), (), ()),
    ("BlockContext", True, "blk_context", "context_part", False, ("outerContext",), (), ()),
    ("MethodContext", True, "meth_context", "context_part", False, ("flags",), (), ()),
    ("BlockClosure", True, "blk_closure", "object", True, ("outerContext", "block", "receiver"), (), ()),
    ("CompiledCode", False, "comp_code", "arr_collection", False, ("literals", "header"), (), ()),
    ("CompiledMethod", True, "comp_method", "comp_code", False, ("descriptor",), (), ()),
    ("CompiledBlock", True, "comp_block", "comp_code", False, ("method",), (), ()),
    ("MethodInfo", True, "meth_info", "object", False, ("sourceCode", "category", "class", "selector", "debugInfo"), (), ()),
    ("LookupTable", False, "lookup_table", "dictionary", False, (), (), ()),
    ("IdentityDictionary", False, "ident_dictionary", "lookup_table", False, (), (), ()),
    ("MethodDictionary", True, "meth_dictionary", "ident_dictionary", False, ("mutex",), (), ()),
    ("TestSuite", False, "test", "object", True, ("testInst1", "testInst2"), ("TestClassVar",), ()),
)

# the instance variable names for Metaclass
# these end up as the instance variables for Class 
# and Metaclass instances
Init_Meta_Vars = ("superClass", "methodDictionary", "instanceSpec", "subClasses", "instanceVariables", 
                  "name", "comment", "category", "environment", "classVariables", "sharedPools", "pragmaHandlers")
                  

# the list of Smalltalk source modules that need compiled for rebuild
Init_Kernel_Mod = (
    "Object.st",
    "UndefObject.st",
    "Boolean.st",
    "False.st",
    "True.st",
    "BlkClosure.st",
    "ContextPart.st",
    "BlkContext.st",
    "MthContext.st",
    "ExcHandling.st",
    "Behavior.st",
    "Magnitude.st",
    "Character.st",
    "Number.st",
    "Integer.st",
    "SmallInt.st",
    "Iterable.st",
    "Collection.st",
    "SeqCollect.st",
    "ArrayColl.st",
    "Array.st",
    "ByteArray.st",
    "Stream.st",
    "PosStream.st",
    "ReadStream.st",
    "WriteStream.st",
    "TestSuite.st",
)

# the list of classes whose 'initialize' message
# should be sent at startup
Init_Class_Init = (
    "Character",
)

# the list of primitive ops handled by the interpreter
# the primitive ID is the index of the name in the list
# plus 1 (0 is reserved)
Init_Primitive = (
    "Object_basicSize",
    "Object_identity",
    "Object_class",
    "Object_basicAt",
    "Object_basicAtPut",
    "Object_shallowCopy",
    "Object_isReadOnly",
    "Object_hash",
    "Object_become",
    "Object_allOwners",
    "BlockClosure_value",
    "BlockClosure_cull",
    "BlockClosure_valueWithArguments",
    "Behavior_basicNew",
    "Behavior_basicNewColon",
    "Behavior_newInitialize",
    "Behavior_newColonInitialize",
    "Character_create",
    "Character_equal",
    "SmallInteger_plus",
    "SmallInteger_minus",
    "SmallInteger_lt",
    "SmallInteger_gt",
    "SmallInteger_le",
    "SmallInteger_ge",
    "SmallInteger_eq",
    "SmallInteger_ne",
    "SmallInteger_times",
    "SmallInteger_intDiv",
    "SmallInteger_modulo",
    "SmallInteger_quo",
    "SmallInteger_bitAnd",
    "SmallInteger_bitOr",
    "SmallInteger_bitXor",
    "SmallInteger_bitShift",
    "ByteArray_basicNewColon",
    "ByteArray_newColonInitialize",
)
