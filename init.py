"""
Configuration for creating a new environment
"""


# Data for building initial class definitions
# 0 = class name
# 1 = cache variable name
# 2 = superclass cache variable name
# 3 = True if object is fixed size
# 3 = tuple of instance variable names
Init_Class = (
    ("Object", "object", None, False, ()),
    ("UndefinedObject", "undef_obj", "object", True, ()),
    ("Boolean", "boolean", "object", True, ()),
    ("False", "false", "boolean", True, ("truthValue",)),
    ("True", "true", "boolean", True, ("truthValue",)),
    ("Behavior", "behavior", "object", True, ("superClass", "methodDictionary", "instanceSpec", "subClasses", "instanceVariables")), 
    ("ClassDescription", "class_desc", "behavior", True, ()),
)