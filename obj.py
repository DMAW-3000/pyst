"""
Object ID manager
"""

import sys


import random
random.seed()


class _ObjTableBase(object):
    """
    Maintain a unique ID for every Object in the system
    """
    
    _Min_Id = 3
    _Max_Id = sys.maxsize
    
    def __init__(self):
        """
        Create an empty object table
        """
        self._obj_map = set()
    
    def free_obj(self, objId):
        """
        Remove the Object id from the global set.
        """
        self._obj_map.discard(objId)
    

class _ObjTableRandom(_ObjTableBase):
    """
    Maintain a unique ID for every Object in the system
    """
    
    _Get_Random = random.randrange
    
    def new_obj(self):
        """
        Allocate a new ID for the given Object.
        Returns the ID value.
        """
        objMap = self._obj_map
        objId = self._Get_Random(self._Min_Id, self._Max_Id)
        while objId in objMap:
            objId = klass._Get_Random(self._Min_Id, self._Max_Id)
        objMap.add(objId)
        return objId
        
        
class _ObjTableLinear(_ObjTableBase):

    def __init__(self):
        """
        Create an empty object table
        """
        super().__init__()
        self._cur_id = self._Min_Id

    def new_obj(self):
        """
        Allocate a new ID for the given Object.
        Returns the ID value.
        """
        objMap = self._obj_map
        objId = self._cur_id
        while objId in objMap:
            objId += 9
            if objId > self._Max_Id:
                objId = self._Min_Id
        objMap.add(objId)
        self._cur_id = objId + 9
        if self._cur_id > self._Max_Id:
            self._cur_id = self._Min_Id + (self._cur_id % 9)
        return objId


# globals
Obj_Table = _ObjTableLinear()