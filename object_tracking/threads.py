import threading
import queue
from time import sleep
from tkinter.tix import Tree
import sys
import select
class Thread_item(threading.Thread):
    """
    класс объекта потока.
    
    на функции надагаются следующие ограничения:
    - все функции от одного аргумента
    - если это начало конвеера (input == None), то функция должна быть итератором и 
    возвращать None после того как вернула все элементы
    - input и output - очереди queue.Queue()
    """
    def __init__(self, func, input, output, daemon = True):
        super(Thread_item, self).__init__(daemon = daemon)
        self.func = func
        self.input = input
        self.output = output
        self.work = True    
        self._frames_ = None

    def run(self):
        if self.input is not None and self.output is not None:
            while True:
                item = self.input.get()
                if item is None:
                    self.output.put(None)
                    break
                self.output.put(self.func(item))
                
        elif self.input is None and self.output is not None:
            """ 
            head of convey   
            """
            while True: 
                for item in self.func:
                    if not self.work:
                        self._frames_ = item[0] 
                        break
                    self.output.put(item)
                
                self.output.put(None)
                

                break


        elif self.input is not None and self.output is None:
            while True:
                item = self.input.get()
                if item is None:
                    break
                self.func(item)
        else:
            raise Exception("Поток не может ничего принимать или выдавать")
    
    def stop(self):
        self.work = False
                       
class Thread_convey():   
    QUEUE_SIZE = 10


    def __init__(self, funcs):
        self.funcs = funcs

    def start(self, join: bool = True):
        n = len(self.funcs)
        self.queue = [None] + [queue.Queue(maxsize = Thread_convey.QUEUE_SIZE) for i in range(n - 1)] + [None]
        self.threads = [Thread_item(self.funcs[i], self.queue[i], self.queue[i + 1], daemon = True) for i in range(n)]
        for thr in self.threads:
            thr.start()


        def hearEnter():
            i, o, e = select.select([sys.stdin], [], [], 1)
            for s in i:
                if s == sys.stdin:
                    return True
            return False

# функция выхода из трекера
        while True:
            if hearEnter():
                self.threads[0].stop()
            if not self.threads[0].is_alive():
                break


        if join:
            for thr in self.threads:
                thr.join()

        return self.threads[0]._frames_