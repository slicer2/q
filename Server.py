# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 23:13:27 2017

@author: danz
"""

class Server:
    def __init__(self, customerTypes, status = 0):
        """
        status:
        0 - not busy
        1 - busy
        """
        self.customerTypes = customerTypes
        self.status = 0
