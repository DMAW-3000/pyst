"""
Object ID manager
"""

import random

random.seed()


class OBJ_TABLE(object):
    """
    Maintain a unique ID for every Object in the system
    """
    
    _Obj_Map = set()
    _Min_Id = 3
    _Max_Id = 0xffffffff
    _Get_Random = random.randrange
	
    @classmethod
    def new_obj(klass):
        """
        Allocate a new ID for the given Object.
        Returns the ID value.
        """
        objMap = klass._Obj_Map
        objId = klass._Get_Random(klass._Min_Id, klass._Max_Id)
        while objId in objMap:
            objId = klass._Get_Random(klass._Min_Id, klass._Max_Id)
        objMap.add(objId)
        return objId
        
    @classmethod
    def free_obj(klass, objId):
        """
        Remove the Object id from the global set.
        """
        klass._Obj_Map.discard(objId)

