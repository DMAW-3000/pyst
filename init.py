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

Init_Class = (
    ("Object", True, "object", None, False, (), ("Dependencies", "FinalizableObjects"), ("Primitives",)),
    ("UndefinedObject", False, "undef_obj", "object", True, (), (), ()),
    ("Boolean", False, "boolean", "object", True, (), (), ()),
    ("False", False, "false", "boolean", True, ("truthValue",), (), ()),
    ("True", False, "true", "boolean", True, ("truthValue",), (), ()),
    ("Behavior", False, "behavior", "object", True, ("superClass", "methodDictionary", "instanceSpec", "subClasses", "instanceVariables"), (), ()), 
    ("ClassDescription", False, "class_desc", "behavior", True, (), (), ()),
    ("Class", True, "class", "class_desc", True, ("name", "comment", "category", "environment", "classVariables", "sharedPools", "pragmaHandlers"), (), ()),
    ("Metaclass", True, "metaclass", "class_desc", True, ("instanceClass",), (), ()),
    ("Iterable", False, "iterable", "object", True, (), (), ()),
    ("Collection", False, "collection", "iterable", True, (), (), ()),
    ("SequencableCollection", False, "seq_collection", "collection", True, (), (), ()),
    ("ArrayedCollection", False, "arr_collection", "seq_collection", False, (), (), ()),
    ("Array", True, "array", "arr_collection", False, (), (), ()),
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
    ("Number", False, "number", "magnitude", True, (), (), ()),
    ("Integer", False, "integer", "number", True, (), (), ("PySymbols",)),
    ("SmallInteger", False, "small_int", "integer", True, (), (), ()),
)

# the instance vaariable names for Metaclass
# these end up as the instance variables for Class instances
Init_Meta_Vars = ("superClass", "methodDictionary", "instanceSpec", "subClasses", "instanceVariables", 
                  "name", "comment", "category", "environment", "classVariables", "sharedPools", "pragmaHandlers")