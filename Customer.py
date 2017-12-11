# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 23:15:14 2017

@author: danz
"""

class Customer:
    def __init__(
                self,
                cId,
                cType,
                status = 0,
                residual = 0,
                arrivalTime = -1,
                serviceBeginTime = -1,
                departureTime = -1,
                serverId = -1):
        """
        status:
        0 - not being served
        1 - being served
        """
        self.cId = cId
        self.cType = cType
        self.status = status
        self.residual = residual
        self.arrivalTime = arrivalTime
        self.serviceBeginTime = serviceBeginTime
        self.departureTime = departureTime
        self.serverId = serverId
