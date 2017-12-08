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

class QSim:
    def __init__(self, tMax, DEBUG = False):
		# by default support customer type 0
        self.server = Server.Server(0)

		# default customer type 0
        self.customerSource = CustomerSource.CustomerSource(constRndFcn(1), expRndFcn(0.8), 0)

        # master event queue
        self.eq = EventQ()

        # queue where customers actually line up
        # implemented as an event queue
        self.q = EventQ()

		# QSim maintains t (time) 
        self.t, self.tMax = 0.0, tMax

        # generate first arrival
        # each arrival triggers generation of next arrival
        self.eq.push(Event(self.t + self.customerSource.nextInterarrival(), 0, self.customerSource.nextCustomer()))

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
            print("Arrival at", self.t, "service needed", customer.residual)
        self.log.append({"type":"arrival", "t":self.t})
        self.log.append({"type":"occupants", "t":self.t, "value":self.occupants})

        # if server busy, put cutomer in queue
        # otherwise in service
        if self.server.status == 1:
            self.q.push(Event(self.t, 0, customer));
        else:
            assert len(self.q) == 0
            self.assign(customer, self.server)

        # generate next arrival
        self.eq.push(Event(self.t + self.customerSource.nextInterarrival(), 0, self.customerSource.nextCustomer()))

    def assign(self, customer, server):
        customer.status = 1
        customer.serviceBeginTime = self.t
        server.status = 1

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

        if len(self.q) > 0:
            self.schedule(self.server)
        else:
            self.server.status = 0

    def schedule(self, server):
        event = self.q.pop()
        customer = event.eData
        self.assign(customer, self.server)
        
        
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
    qsim = QSim(20.0, True)
    qsim.run()
    qsim.stats()
