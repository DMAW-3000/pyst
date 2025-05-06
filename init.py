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
    ("Object", True, "object", None, False, ()),
    ("UndefinedObject", False, "undef_obj", "object", True, ()),
    ("Boolean", False, "boolean", "object", True, ()),
    ("False", False, "false", "boolean", True, ("truthValue",)),
    ("True", False, "true", "boolean", True, ("truthValue",)),
    ("Behavior", False, "behavior", "object", True, ("superClass", "methodDictionary", "instanceSpec", "subClasses", "instanceVariables")), 
    ("ClassDescription", False, "class_desc", "behavior", True, ()),
    ("Class", True, "class", "class_desc", True, ("superClass", "name", "comment", "category", "environment", "classVariables", "sharedPools")),
    ("Metaclass", True, "metaclass", "class_desc", True, ("instanceClass",)),
    ("Iterable", False, "iterable", "object", True, ()),
    ("Collection", False, "collection", "iterable", True, ()),
    ("SequencableCollection", False, "seq_collection", "collection", True, ()),
    ("ArrayedCollection", False, "arr_collection", "seq_collection", False, ()),
    ("Array", True, "array", "arr_collection", False, ()),
    ("Link", False, "link", "object", True, ("nextLink",)),
    ("SymLink", True, "sym_link", "link", True, ("symbol",)),
)