# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 22:29:54 2017

@author: danz
"""

import Customer

class CustomerSource:
    def __init__(self, serviceFcn, interarrivalFcn, cType, startId = 0):
        self.serviceFcn = serviceFcn
        self.interarrivalFcn = interarrivalFcn
        self.nextId = startId
        self.cType = cType
        
    def nextInterarrival(self):
        """
        return next interarrival time
        """
        return self.interarrivalFcn()
    
    def nextService(self):
        """
        return next service time
        """
        return self.serviceFcn()
    
    def nextCustomer(self):
        self.nextId += 1
        return Customer.Customer(self.nextId - 1, self.cType, 0, self.serviceFcn())
