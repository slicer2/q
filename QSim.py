# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 22:51:04 2017

@author: danz
"""

import math
import random
import Server
import CustomerSource
from EventQ import Event, EventQ
import numpy as np

class QSim:
    def __init__(self, tMax, DEBUG = False):
        self.placement = np.array([[1, 1], [1, 0]])
        self.nContent, self.nServer = self.placement.shape
        self.la = np.array([0.8, 0.6])
        self.mu = np.array([0.6, 0.8])
        self.laMat = np.array([[0.5, 0.5], [1, 0]])
        self.I = np.zeros(self.laMat.shape)

        # find out which server contains a particular content
        self.hasServer = [np.where(self.placement[i, :] > 0)[0]
                        for i  in range(self.placement.shape[0])]

        # find out what contents are hosted on a particular server
        self.hasContent = [np.where(self.placement[:, i] > 0)[0]
                        for i in range(self.placement.shape[1])]


		# by default support customer type 0
        self.servers = [Server.Server() for i in range(self.nServer)]

		# default customer type 0
        self.customerSources = [CustomerSource.CustomerSource(
                                constRndFcn(self.mu[i]),
                                expRndFcn(self.la[i]), i
                                ) for i in range(self.nContent)]

        # master event queue
        self.eq = EventQ()

        # queue where customers actually line up
        # implemented as an event queue
        self.qs = [EventQ() for x in range(self.nContent)]

		# QSim maintains t (time) 
        self.t, self.tMax = 0.0, tMax

        # generate first arrival
        # each arrival triggers generation of next arrival
        for i in range(self.nContent):
            self.eq.push(Event(
                        self.t + self.customerSources[i].nextInterarrival(),
                        0,
                        self.customerSources[i].nextCustomer())
                        )

        # number of customers in system
        self.occupants = 0

        # book keeping
        self.log = []

        # print DEBUG information
        self.DEBUG = DEBUG
        
    def run(self):
        # event loop
        while self.t < self.tMax:
            event = self.eq.pop()
            self.t = event.ts
            if event.eType == 0: # arrival
                self.processArrival(event)
            elif event.eType == 1: # departure
                self.processDeparture(event)
            else:
                raise RuntimeError("Unsupported event type")
                
    def processArrival(self, event):
        self.occupants += 1
        customer = event.eData
        customer.arrivalTime = self.t
        if self.DEBUG:
            print("Arrival at", self.t, "cType", customer.cType, "service needed", customer.residual)
        self.log.append({"type":"arrival", "cType":customer.cType, "t":self.t})
        self.log.append({"type":"occupants", "t":self.t, "value":self.occupants})

        # if server busy, put cutomer in queue
        # otherwise in service
        idleServers = self.idleServers()
        if customer.cType in idleServers:
            self.assign(customer, idleServers)
        else:
            assert len(self.qs[customer.cType]) == 0
            self.qs[customer.cType].push(Event(self.t, 0, customer));

        # generate next arrival
        self.eq.push(Event(
                        self.t + self.customerSources[customer.cType].nextInterarrival(),
                        0,
                        self.customerSources[customer.cType].nextCustomer())
                    )

    def idleServers(self):
        return [x for x in range(self.nServer) if self.servers[x].status == 0]

    def assign(self, customer, idleServers):
        customer.status = 1
        customer.serviceBeginTime = self.t

        minIndex, minIndexServer = np.inf, -1
        for s in idleServers:
            tmp = self.I[customer.cType][s] / self.laMat[customer.cType][s]
            if tmp < minIndex:
                minIndex = tmp
                minIndexServer = s

        assert not minIndexServer == -1

        customer.server = minIndexServer
        self.servers[minIndexServer].status = 1
        self.I[customer.cType][minIndexServer] += 1

        # generate departure
        self.eq.push(Event(self.t + customer.residual, 1, customer))
        self.log.append({"type":"waittime", "value":customer.serviceBeginTime - customer.arrivalTime})
        
    def processDeparture(self, event):
        self.occupants -= 1
        assert self.occupants >= 0

        customer = event.eData
        customer.departureTime = self.t
        if self.DEBUG:
            print("Departure at", self.t)
        self.log.append({"type":"departure", "t":self.t})
        self.log.append({"type":"occupants", "t":self.t, "value":self.occupants})
        self.log.append({"type":"systemtime", "value":customer.departureTime - customer.arrivalTime})

        if not self.schedule(customer.serverId):
            self.servers[customer.serverId].status = 0

    def schedule(self, serverId):
        minIndex, minIndexContent = np.inf, -1
        for c in self.hasContent(serverId):
            if len(self.qs[c]) > 0:
                tmp = self.I[c][serverId] / self.laMat[c][serverId]
                if minIndex < tmp:
                    minIndex = tmp
                    minIndexContent = c

        if minIndexContent == -1:
            return False
        else:
            event = self.qs[minInexContent].pop()
            customer = event.eData
            self.assign(customer, np.array([serverId]))
        
        
    def stats(self): 
        # interarrival
        logInterarrival = [x for x in self.log if x["type"] == "arrival"]
        tot, prev, cnt = 0, 0, 0
        for x in logInterarrival:
            tot += x["t"] - prev
            prev = x["t"]
            cnt += 1
    
        avgInterarrival = tot / cnt
        print("customers entered:", len(logInterarrival))
        print("average interarrival:", avgInterarrival)

        # occupants
        logOccupants = [x for x in self.log if x["type"] == "occupants"]
        accumulatedOccupants, prev, occupants = 0, 0, 0
        for x in logOccupants:
            accumulatedOccupants += occupants * (x["t"] - prev)
            prev, occupants = x["t"], x["value"]
        accumulatedOccupants += occupants * (self.tMax - prev)
        avgOccupants = accumulatedOccupants / self.tMax
        print("average occupants:", avgOccupants)

        # system time
        logSystemTime = [x for x in self.log if x["type"] == "systemtime"]
        tot = 0
        for x in logSystemTime:
            tot += x["value"]
        avgSystemTime = tot / len(logSystemTime)
        print("average system time:", avgSystemTime)
        
def expRndFcn(la):
    def expRnd():
        return -math.log(1.0 - random.random()) / la
    
    return expRnd;

def constRndFcn(la):
    def constRnd():
        return 1 / la;

    return constRnd;
    
if __name__ == "__main__":
    random.seed(0)
    qsim = QSim(20.0)
    qsim.run()
    #qsim.stats()
