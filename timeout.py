#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import threading
import thread
import Queue
import time

class Timeout(threading.Thread):
    
    def __init__ ( self, queue, timeout  ):
        self.__queue   = queue
        self.__timeout = timeout
        threading.Thread.__init__(self)

    def run(self):
        count = 0
        while count < self.__timeout:
            if not self.__queue.empty():
                item = self.__queue.get()
                if item == 'exit':
                    thread.exit()
        
            time.sleep(1)
            count += 1
        
        thread.interrupt_main()