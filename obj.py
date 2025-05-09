"""
Object ID manager
"""

import random
random.seed()


class OBJ_TABLE_BASE(object):
    """
    Maintain a unique ID for every Object in the system
    """
    
    _Obj_Map = set()
    _Min_Id = 3
    _Max_Id = 0xffffffff
    
    @classmethod
    def free_obj(klass, objId):
        """
        Remove the Object id from the global set.
        """
        klass._Obj_Map.discard(objId)
    

class OBJ_TABLE_RANDOM(OBJ_TABLE_BASE):
    """
    Maintain a unique ID for every Object in the system
    """
    
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
        
        
class OBJ_TABLE_LINEAR(OBJ_TABLE_BASE):

    _Cur_Id = OBJ_TABLE_BASE._Min_Id

    @classmethod
    def new_obj(klass):
        """
        Allocate a new ID for the given Object.
        Returns the ID value.
        """
        objMap = klass._Obj_Map
        objId = klass._Cur_Id
        while objId in objMap:
            objId += 7
            if objId > klass._Max_Id:
                objId = klass._Min_Id
        objMap.add(objId)
        return objId


# globals
OBJ_TABLE = OBJ_TABLE_LINEAR