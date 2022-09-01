from time import time
from datetime import datetime
from typing import Dict, FrozenSet

"""
этот файл содержит реализацию класса для для постобработки трекинга
"""
class Item(object):
    def __init__(self, track_id, frame_num: int = 0):
        self.track_id = track_id
        self.start_time = datetime.now()
        self.last_seen = time()
        self.frame_num = frame_num        

##### добавьте нужные действия для начала трекинга
        print(f"{self.track_id} вошел в кадр в {self.start_time}. Номер кадра : {self.frame_num}")

    def update(self, in_frame: bool, frame_num: int, delete_after: int = 60):
        if in_frame:
            self.last_seen = time()
            self.frame_num = frame_num
        else:
            if(frame_num - self.frame_num > delete_after):
                
##### добавьте действия перед концом трекинга
                print(f"{self.track_id} вышел из кадра в {datetime.now()}. Номер кадра : {self.frame_num}")
                return 1
        return 0
            

class Notify_tracker():
    """
    трекер
    delete_after - число кадров которое объект должен отсутствовать в кадре после которого он удаляется
    
    """
    def __init__(self, delete_after: int = 60):
        self.items : Dict[int, Item] = {}
        self.delete_after = delete_after

    def update(self, id_list: FrozenSet[int], frame_num: int):
        id_list = frozenset(id_list)
        for key in list(self.items.keys()):
            val = self.items[key]
            upd = val.update(key in id_list, frame_num, self.delete_after)
            if upd:
                del self.items[key]

        for key in(id_list - self.items.keys()):
            self.items[key] = Item(key, frame_num)
