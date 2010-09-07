#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import binascii

class Tools(object):
    """ Collection of usefull little tools.
    
    >>> from tools import Tools
    >>> t = Tools()
    >>> t.hexhex('FD')
    '0xfd'
    """
    
    def __init__(self):
        pass
        
    def hexhex(self,str):
        return hex(int(str, 16))
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
