# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 23:13:27 2017

@author: danz
"""

class Server:
    def __init__(self, status = 0):
        """
        status:
        0 - not busy
        1 - busy
        """
        self.status = 0
