"""
Object ID manager
"""

import weakref
import random
random.seed()


class _ObjTableBase(object):
    """
    Maintain a unique ID for every Object in the system
    """
    
    _Min_Id = 3
    _Max_Id = 0xffffffff
    
    def __init__(self):
        """
        Create an empty object table
        """
        self._obj_map = weakref.WeakValueDictionary()
    
    def free_obj(self, objId):
        """
        Remove the Object id from the global set.
        """
        self._obj_map.pop(objId, None)
        
    def get_all_obj(self):
        """
        Return a list of all Objects
        """
        return list(self._obj_map.values())
    

class _ObjTableRandom(_ObjTableBase):
    """
    Maintain a unique ID for every Object in the system
    """
    
    _Get_Random = random.randrange
    
    def new_obj(self, obj):
        """
        Allocate a new ID for the given Object.
        Returns the ID value.
        """
        objMap = self._obj_map
        objId = self._Get_Random(self._Min_Id, self._Max_Id)
        while objId in objMap:
            objId = self._Get_Random(self._Min_Id, self._Max_Id)
        objMap[objId] = obj
        return objId
        
        
class _ObjTableLinear(_ObjTableBase):

    def __init__(self):
        """
        Create an empty object table
        """
        super().__init__()
        self._cur_id = self._Min_Id

    def new_obj(self, obj):
        """
        Allocate a new ID for the given Object.
        Returns the ID value.
        """
        objMap = self._obj_map
        objId = self._cur_id
        while objId in objMap:
            objId += 1
            if objId > self._Max_Id:
                objId = self._Min_Id
        objMap[objId] = obj
        self._cur_id = objId + 1
        if self._cur_id > self._Max_Id:
            self._cur_id = self._Min_Id
        return objId


# globals
Obj_Table = _ObjTableLinear()